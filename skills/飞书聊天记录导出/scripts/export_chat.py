#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书群聊原始记录导出（含图片内嵌）。

依赖：飞书官方 lark-cli（@larksuite/cli），且已完成 config init + auth login（user 身份）。
本脚本只负责"拿到结构化的原始聊天记录 + 下载图片 + 内嵌进 Markdown"这一固定流程，
不做任何摘要/整理（总结是一句话的事，没必要写进技能）。

用法：
  python export_chat.py --chat-name "aivc-data-paper" --out-dir <目标目录>
  python export_chat.py --chat-id oc_xxx                --out-dir <目标目录>

增量 append（追加上次导出之后的新消息，不重复、不重排）：
  python export_chat.py --chat-id oc_xxx --out-dir <目标目录> --append

产物（写在 --out-dir 下）：
  飞书群聊原始转录_<chat>.md   逐条原始记录，图片用 ![](images/xxx) 内嵌
  images/                      下载的图片（png/jpg…），文件名 = <img_key>.<ext>
  .lark_export_state.json      增量状态（最后一条消息时间 + 已见 message_id）
"""
import argparse, json, os, re, shutil, subprocess, sys, glob

# ---- 找到 lark-cli 可执行文件（PATH 里没有时兜底到 npm 全局目录）----
def find_lark():
    for c in ("lark-cli", "lark-cli.cmd"):
        if shutil.which(c):
            return shutil.which(c)
    for base in (
        os.path.expandvars(r"%APPDATA%\npm"),
        os.path.expanduser("~/.npm-global/bin"),
        "/usr/local/bin", "/usr/bin",
    ):
        for c in ("lark-cli", "lark-cli.cmd"):
            p = os.path.join(base, c)
            if os.path.exists(p):
                return p
    sys.exit("ERROR: 找不到 lark-cli。请先 `npm install -g @larksuite/cli` 并完成授权。")

LARK = find_lark()

def run(args, cwd=None):
    """跑 lark-cli，返回 stdout 里第一个 JSON（容忍前导 warning 行）。"""
    p = subprocess.run([LARK] + args, capture_output=True, text=True,
                       encoding="utf-8", cwd=cwd)
    out = p.stdout or ""
    i = out.find("{")
    if i < 0:
        sys.exit(f"ERROR: lark-cli 无 JSON 输出。\ncmd={args}\nstderr={p.stderr}\nstdout={out[:500]}")
    return json.loads(out[i:])

def check_auth():
    d = run(["auth", "status"])
    user = (d.get("identities", {}) or {}).get("user", {})
    if not user.get("available"):
        sys.exit("ERROR: 未登录用户身份。请先在后台运行 `lark-cli auth login --recommend` "
                 "并在浏览器完成授权（读取私有群聊需要 user 身份）。")

def resolve_chat_id(name):
    d = run(["im", "+chat-search", "--query", name])
    chats = (d.get("data", {}) or {}).get("chats", []) or []
    exact = [c for c in chats if c.get("name") == name]
    pick = exact[0] if exact else (chats[0] if chats else None)
    if not pick:
        sys.exit(f"ERROR: 找不到名为 {name!r} 的群。")
    print(f"  匹配群: {pick.get('name')}  chat_id={pick.get('chat_id')}")
    return pick["chat_id"]

NAMEMAP = {}  # open_id -> 显示名（从群成员表补全 lark-cli 偶尔缺名的情况）
def load_members(chat_id):
    try:
        d = run(["im", "chat.members", "get", "--params",
                 json.dumps({"chat_id": chat_id})])
        items = (d.get("data", {}) or {}).get("items") or \
                (d.get("data", {}) or {}).get("members") or []
        for it in items:
            if it.get("member_id") and it.get("name"):
                NAMEMAP[it["member_id"]] = it["name"]
    except SystemExit:
        pass  # 拿不到成员表不致命

def fetch_all(chat_id, res_dir):
    """分页拉全部消息（asc），并下载图片/文件资源到 res_dir。返回去重后的消息列表。"""
    os.makedirs(res_dir, exist_ok=True)
    seen, token, page = {}, "", 1
    while True:
        args = ["im", "+chat-messages-list", "--chat-id", chat_id,
                "--order", "asc", "--page-size", "50", "--no-reactions",
                "--download-resources", "--format", "json"]
        if token:
            args += ["--page-token", token]
        # 资源下到 res_dir 的父目录的 lark-im-resources/，所以用 cwd 控制落点
        d = run(args, cwd=res_dir)
        data = d.get("data", {}) or {}
        for m in data.get("messages", []):
            seen[m["message_id"]] = m
        print(f"  page {page}: +{len(data.get('messages', []))}  has_more={data.get('has_more')}")
        token = data.get("page_token", "") if data.get("has_more") else ""
        page += 1
        if not token or page > 200:
            break
    return sorted(seen.values(), key=lambda m: (m["create_time"], m["message_id"]))

def build_imgmap(res_dir):
    """img_key -> 实际文件名（带真实扩展名）。"""
    m = {}
    for fn in os.listdir(res_dir):
        base = os.path.splitext(fn)[0]
        if base.startswith("img_"):
            m[base] = fn
    return m

IMG_RE = re.compile(r"\[Image:\s*([A-Za-z0-9_\-]+)\]")

def render(msgs, imgmap, append_to=None):
    """把消息渲染成 Markdown；[Image: key] -> ![](images/<file>)。"""
    lines = []
    for m in msgs:
        s = m.get("sender") or {}
        name = NAMEMAP.get(s.get("id")) or s.get("name") or \
               ("[系统]" if m.get("msg_type") == "system" else "[未知]")
        tag = f"  ·({m['msg_type']})" if m.get("msg_type") != "text" else ""
        def repl(mo):
            fn = imgmap.get(mo.group(1).strip())
            return f"![{mo.group(1)}](images/{fn})" if fn else mo.group(0)
        content = IMG_RE.sub(repl, m.get("content", ""))
        lines.append(f"**[{m['create_time']}] {name}{tag}**\n{content}\n")
    return "\n".join(lines)

def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--chat-name")
    g.add_argument("--chat-id")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--append", action="store_true",
                    help="增量追加（基于 .lark_export_state.json 去重，不重排已有内容）")
    a = ap.parse_args()

    check_auth()
    chat_id = a.chat_id or resolve_chat_id(a.chat_name)
    load_members(chat_id)

    out = os.path.abspath(a.out_dir)
    os.makedirs(out, exist_ok=True)
    imgdir = os.path.join(out, "images")
    os.makedirs(imgdir, exist_ok=True)
    res_dir = os.path.join(out, "_lark_resources_tmp")
    os.makedirs(res_dir, exist_ok=True)

    print("拉取消息中…")
    msgs = fetch_all(chat_id, res_dir)
    print(f"共 {len(msgs)} 条唯一消息。")

    # 资源默认下到 res_dir/lark-im-resources/
    raw_res = os.path.join(res_dir, "lark-im-resources")
    if os.path.isdir(raw_res):
        for fn in os.listdir(raw_res):
            if os.path.splitext(fn)[0].startswith("img_"):
                shutil.copy2(os.path.join(raw_res, fn), os.path.join(imgdir, fn))
    imgmap = build_imgmap(imgdir)
    print(f"图片 {len(imgmap)} 张已落到 images/。")

    label = a.chat_name or chat_id
    md_path = os.path.join(out, f"飞书群聊原始转录_{re.sub(r'[^A-Za-z0-9_-]','_',label)}.md")
    state_path = os.path.join(out, ".lark_export_state.json")

    if a.append and os.path.exists(md_path) and os.path.exists(state_path):
        st = json.load(open(state_path, encoding="utf-8"))
        old_ids = set(st.get("seen_ids", []))
        new = [m for m in msgs if m["message_id"] not in old_ids]
        if new:
            body = render(new, imgmap)
            with open(md_path, "a", encoding="utf-8") as f:
                f.write("\n" + body + "\n")
            print(f"已追加 {len(new)} 条新消息。")
        else:
            print("没有新消息，无需追加。")
        st["seen_ids"] = list(old_ids | {m["message_id"] for m in msgs})
        st["last_time"] = msgs[-1]["create_time"] if msgs else st.get("last_time")
        json.dump(st, open(state_path, "w", encoding="utf-8"), ensure_ascii=False)
    else:
        header = (f"# {label} 群聊原始转录（含图片）\n\n"
                  f"共 {len(msgs)} 条消息，{msgs[0]['create_time']} → {msgs[-1]['create_time']}。\n"
                  f"图片存于 `images/`（共 {len(imgmap)} 张）。原始记录，未做任何整理。\n\n---\n\n")
        open(md_path, "w", encoding="utf-8").write(header + render(msgs, imgmap))
        json.dump({"chat_id": chat_id,
                   "seen_ids": [m["message_id"] for m in msgs],
                   "last_time": msgs[-1]["create_time"] if msgs else None},
                  open(state_path, "w", encoding="utf-8"), ensure_ascii=False)
        print(f"已写出：{md_path}")

    # 清理临时资源目录（图片已复制到 images/）
    shutil.rmtree(res_dir, ignore_errors=True)
    print("完成。")

if __name__ == "__main__":
    main()
