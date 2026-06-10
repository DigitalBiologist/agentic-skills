---
name: 提交技能
description: "新手专用：把你写好的一个 Claude Code 技能，自动提交到 agentic-skills 这个大家共享的公共仓库——全程由你的 Claude 完成（clone/同步仓库 → 放进你在 `contrib/` 下的个人暂存文件夹 → 快速脱敏检查 → 建分支 → commit → push → 开 Pull Request），你只要说一句话，最后等管理员合并即可。专为完全不懂 git/分支/PR 的新手设计。与「发布到技能库」的区别：那个把技能直推到你自己的仓库；本技能是给大家共享的 agentic-skills 提 PR（要管理员审核后才合并进去）。触发：'提交技能'/'把我的技能交上去'/'贡献到 agentic-skills'/'帮我把 XXX 提交到技能库'/'/提交技能 XXX'。"
---

# 提交技能 — 一句话，把你的技能交到大家的共享库（走 PR）

> **给学生看的一句话**：你写好了一个 Claude Code 技能，想加进大家一起维护的 `agentic-skills` 仓库？
> 直接跟我（Claude）说 **"帮我把 XX 技能提交上去"**，剩下的全交给我。你不用懂 git，最后只要等管理员点合并就行。

---

## 这个技能给谁用

- 你是 `agentic-skills` 仓库的协作者（被管理员加进来了，邀请邮件点过"接受"）。
- 你在本地写好了一个技能（通常在 `~/.claude/commands/<技能名>/`，或你自己指定的路径）。
- 你**不需要**懂分支、PR、git 命令——这些我（你的 Claude）全包。

## 只配一次（新手照抄）

1. 装 GitHub CLI 并登录（只做一次）：
   ```bash
   gh auth login      # 选 GitHub.com → HTTPS → Login with a web browser，照提示在浏览器点确认
   gh auth status     # 看到 "Logged in" 就好了
   ```
2. 确认你已接受仓库邀请：打开 https://github.com/DigitalBiologist/agentic-skills/invitations 点接受（没接受也没关系，本技能会自动改用 fork 方式）。

---

## 我（Claude）执行的流程

> 下面是给 agent 的执行步骤。把 `<技能名>` 换成实际名字；遇到失败就把报错原样告诉用户、别硬撑。

### Step 0 · 确认环境 + 搞清要提交什么

```bash
gh auth status || echo "❌ 还没登录，请先跑 gh auth login"
ME=$(gh api user --jq .login); echo "当前 GitHub 账号: $ME"
```

跟用户确认这几件事：① 要提交哪个技能？② 它的源文件夹在哪？③ 技能叫什么名字（会成为技能目录名）？④ **你的名字**——会成为你的个人暂存文件夹 `contrib/<你的名字>/`（例如 `songyixuan`）。**之前提交过就沿用同一个名字、同一种拼法**，别冒出两个文件夹。

### Step 1 · 准备本地仓库（没有就自动 clone）

```bash
REPO=~/agentic-skills
if [ ! -d "$REPO/.git" ]; then
  gh repo clone DigitalBiologist/agentic-skills "$REPO"
fi
git -C "$REPO" checkout main
git -C "$REPO" pull --ff-only            # 先同步最新，避免冲突
```

### Step 2 · 判断走"分支"还是"fork"

```bash
PERM=$(gh api "repos/DigitalBiologist/agentic-skills/collaborators/$ME/permission" --jq .permission 2>/dev/null)
echo "你的权限: ${PERM:-none}"
```

- `write` 或 `admin` → 你是协作者，**直接在仓库里建分支**（最简单，下面默认走这条）。
- 其它/报错 → 你还不是协作者，自动改用 fork：
  ```bash
  gh repo fork DigitalBiologist/agentic-skills --clone=false --remote=true
  ```
  之后把 push 目标换成你 fork 的 remote，开 PR 时 `--head` 写成 `$ME:<分支名>`。

### Step 3 · 把技能放到你的 contrib 暂存文件夹

新人/实习生的技能先进**个人暂存区** `contrib/<你的名字>/`，**不直接进正式 `skills/`**。大家在这里装上试用、给你反馈，公认好用后由管理员提升进 `skills/`。

```bash
ls "$REPO/contrib" 2>/dev/null    # 先看已有哪些贡献者文件夹；你自己的那个就沿用，别新拼一个
NAME=<你的名字>                     # 你的 contrib 文件夹名，如 songyixuan
mkdir -p "$REPO/contrib/$NAME/<技能名>"
cp -r <源技能文件夹>/* "$REPO/contrib/$NAME/<技能名>/"
```

仓库结构约定：
```
contrib/<你的名字>/<技能名>/
├── SKILL.md            # 技能本体
├── README-配置指南.md   # 怎么装、怎么用、一条测试命令
└── ...                 # 可选 scripts/ vendor/ template 等
```

- 单文件技能 → 写成 `contrib/<你的名字>/<技能名>/SKILL.md`。
- 文件夹技能 → 整个拷进去，主文档命名 `SKILL.md`。
- 若还没有 `README-配置指南.md`，替用户补一份：前置条件、依赖、安装方式（`cp -r` 到 `~/.claude/commands/`）、一条能跑的测试命令。

### Step 4 · 快速脱敏检查（重要，别跳过）

仓库是**公开**的——任何密钥/个人信息一旦 push 进 git 历史极难清除。提交前跑一遍快速 grep，**命中就改成占位符再继续**：

```bash
cd "$REPO/contrib/$NAME/<技能名>"
# 凭据（出现真实值才算问题；纯说明文字里的词可人工判断）
grep -rniE 'sk-[a-z0-9]{10,}|password[=: ]|passwd|secret|bearer|token=|api[_-]?key' . --exclude-dir=vendor
# 个人/机构标识（把尖括号换成你的真实标识再扫）
grep -rniE '<你的用户名>|<你的中英文名>|<你的学校/机构>|<你的导师/同事名>' .
# 家目录绝对路径、内网 IP
grep -rniE '/Users/[a-z]' . ; grep -rnE '172\.16\.|192\.168\.|10\.[0-9]+\.[0-9]+\.' .
```

理想结果全部零命中。完整清单见仓库根目录的 `CONTRIBUTING.md`（不必全背，上面这几条够用）。

### Step 5 · 建分支 + 提交 + 推送

```bash
cd "$REPO"
BRANCH="add-$ME-<技能名>"                       # 用账号名保证分支名唯一、可读
git checkout -b "$BRANCH"
# 用 GitHub noreply 邮箱提交，不暴露你的真实邮箱
git config user.email "$(gh api user --jq '"\(.id)+\(.login)@users.noreply.github.com"')"
git config user.name  "$ME"
git add -A
git commit -m "Add <技能名> to contrib/$NAME"
git push -u origin "$BRANCH"                    # fork 用户：origin 指向你自己的 fork
```

### Step 6 · 开 Pull Request

```bash
gh pr create --repo DigitalBiologist/agentic-skills \
  --base main --head "$BRANCH" \
  --title "Add <技能名> to contrib/$NAME" \
  --body "把技能 **<技能名>** 放进个人暂存区 contrib/$NAME/，供大家试用反馈；好用了再提升进正式 skills/。已做脱敏快速自检。

功能：<一句话描述这个技能干嘛的>"
```

> fork 情况：`--head` 写成 `$ME:$BRANCH`（gh 通常能自动识别）。

### Step 7 · 告诉用户

把 PR 链接发给用户，并明确告诉 ta：
> ✅ 已提交，PR 链接在这。**接下来等管理员审核合并，你这边什么都不用做了。** 合并后你的技能就进 `contrib/<你的名字>/` 暂存区，大家就能装上试用、给你反馈；好用了管理员会提升进正式 `skills/` 库。

---

## 完全不想碰命令行的学生：纯网页 3 步（备选）

连 `gh` 都不想装也行，用浏览器：

1. 打开 https://github.com/DigitalBiologist/agentic-skills ，进 `contrib/` 目录，点 **Add file → Create new file**；文件名填 `你的名字/技能名/SKILL.md`（例如 `songyixuan/我的技能/SKILL.md`，斜杠会自动建子目录），把你的技能内容粘进去。
2. 页面底部选 **"Create a new branch for this commit and start a pull request"** → 点 **Propose changes**。
3. 在弹出的 PR 页填一句说明 → **Create pull request**。**提交前肉眼确认没有密钥、真实姓名、家目录路径。**

之后等管理员合并即可。

---

## 注意

- 你只需**提 PR**，不能也不需要直接改 `main`（管理员开了分支保护）。审核合并由管理员做——这是为了大家一起做时不出乱子，并不是不信任你 🙂。
- 公开库：Step 4 的脱敏检查别跳过，密钥/隐私一旦进历史很难清。
- 用 noreply 邮箱提交，git 历史就不会暴露你的真实邮箱。
- 流程里任何一步报错，把原始报错贴给用户，不要假装成功。
