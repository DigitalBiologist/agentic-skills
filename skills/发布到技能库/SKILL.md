---
name: 发布到技能库
description: "把一个开发成熟的 Claude Code 技能脱敏后发布到 agentic-skills 公共技能库（GitHub）：按仓库结构入库、生成配置指南、grep 全量自检零命中、更新 README 索引表、commit + push。与「技能分享」的区别——技能分享是把单个技能打包成独立文件夹发给某个朋友（一次性）；本技能是持续维护一个公开技能集（入库 + 版本控制 + 共享）。仓库地址和提交身份运行时动态读取，不硬编码，因此 fork 本库的人也能用它发布到自己的库。触发：'发布技能'/'发布到技能库'/'把 XXX 加进 agentic-skills'/'上传技能到公共库'/'/发布到技能库 XXX'。"
---

# 发布到技能库 — 把技能发布到 agentic-skills 公共库

把一个本地已开发成熟的技能,**脱敏后入库**到 agentic-skills 这个公开、可与他人共享的技能仓库,并完成版本控制(commit + push)。

## 与「技能分享」的区别

| | 技能分享 | 发布到技能库（本技能） |
|---|---|---|
| 目标 | 打包成独立文件夹发给**某个朋友** | 入库到**公共仓库**并持续维护 |
| 产物 | `~/Desktop/{技能名}-kit/`(一次性) | `<repo>/skills/{技能名}/` + 更新索引 + git 提交 |
| 之后 | 压缩发出即结束 | push 到 GitHub,任何人可 clone |

脱敏规则两者共用 —— 本技能在 Step 2 直接复用 `技能分享` 的扫描清单。

## 配置区（首次使用按需调整；默认值即本库)

| 变量 | 默认 | 说明 |
|------|------|------|
| `REPO_LOCAL` | `~/Desktop/agentic-skills` | 本地仓库路径 |
| 远端地址 | **动态读取** | `git -C "$REPO_LOCAL" remote get-url origin`,不写死账号 |
| 提交身份 | **动态拼接** | GitHub noreply email,见 Step 6,避免暴露真实邮箱 |

> fork 本库的人:把 `REPO_LOCAL` 改成你自己的本地路径即可,远端和身份会自动跟随你的 git/gh 登录,无需改其它任何东西。

## 仓库结构约定（务必遵守）

```
<repo>/
├── README.md            # 顶层,含 Skills index 表
├── CONTRIBUTING.md      # 脱敏 checklist（发布前必读）
└── skills/
    └── <技能名>/
        ├── SKILL.md            # 技能本体（脱敏版）
        ├── README-配置指南.md   # 安装/配置文档
        └── ...                 # 可选 scripts/ vendor/ templates/
```

---

## 执行流程

### Step 0: 确认仓库就绪

```bash
REPO_LOCAL=~/Desktop/agentic-skills
git -C "$REPO_LOCAL" rev-parse --is-inside-work-tree >/dev/null 2>&1 \
  && echo "✅ repo ok: $(git -C "$REPO_LOCAL" remote get-url origin)" \
  || echo "❌ 仓库不存在,先 clone 或 gh repo create"
git -C "$REPO_LOCAL" pull --ff-only 2>&1 | tail -1   # 先同步,避免 push 冲突
```

### Step 1: 定位源技能 + 脱敏（复用「技能分享」）

按 `技能分享` 技能的 Step 1–2 执行:

1. 读取技能主文件,**递归追踪所有关联文件**(scripts/ templates/ references/ vendor/、symlink 指向的文件)。
2. 扫描并替换敏感信息(API Key/密码/Token/用户名/邮箱/团队组织/内网 IP/订阅链接/家目录路径)为占位符。
3. **grep 之外务必通读全文** —— 家目录路径(`~/<你的私人目录>`)、大小写人名(`john` vs `John`)最容易漏。

### Step 2: 按仓库结构放置

```bash
SKILL_NAME="<技能名>"
mkdir -p "$REPO_LOCAL/skills/$SKILL_NAME"
```

- **单文件技能** → 脱敏后写成 `skills/<技能名>/SKILL.md`。
- **文件夹技能** → 保留 `scripts/`、`vendor/` 等结构;主文档命名 `SKILL.md`。
- **大的第三方库**(如 PDF.js、d3) → 放 `vendor/`,并在 README-配置指南 注明来源 + license;能走 CDN 的可不打包。

### Step 3: 生成 README-配置指南.md

在 `skills/<技能名>/README-配置指南.md` 写:前置条件、环境变量(给 zshrc 模板)、安装依赖、放置文件(cp 到 `~/.claude/commands/`)、一条可跑的测试命令、3–5 条 FAQ、第三方组件与 license。

### Step 4: grep 全量自检（零命中才能继续）

把占位换成你自己的真实标识后运行,**全部必须零命中**(凭证模式词若出现在"教学示例"里需人工判断):

```bash
cd "$REPO_LOCAL/skills/$SKILL_NAME"
grep -rniE '<你的用户名>|<你的拼音名>|<你的中文名>|<你的机构>|<你的导师/同事>' .   # 个人身份
grep -rn  '<你的英文名首字母大写形式>' .                                          # 大小写陷阱:大写名单独扫
grep -rniE '<你的私人目录名>|/Users/<你>' .   # 家目录路径(如 notes/、Documents/ 这类私人目录前缀)
grep -rnE  '172\.16\.[0-9]+\.[0-9]+|192\.168\.[0-9]+\.[0-9]+'  .                  # 具体内网 IP
grep -rniE 'password|passwd|bearer|token=|sk-[a-z0-9]{6}' . --exclude-dir=vendor  # 凭证（确认无真实值）
```

命中 → 修 → 重扫,直到干净。

### Step 5: 更新顶层 README 索引表

在 `README.md` 的 **Skills index** 表里加一行:

```
| [<技能名>](skills/<技能名>) <br>(英文别名) | 一句话功能描述 | ✅ ready |
```

### Step 6: commit + push（用 noreply 邮箱,不暴露真实邮箱）

```bash
cd "$REPO_LOCAL"
# 动态拼接当前 gh 登录账号的 noreply email（首次在本 repo 设一次即可）
NOREPLY=$(gh api user --jq '"\(.id)+\(.login)@users.noreply.github.com"')
git config user.email "$NOREPLY"
git config user.name  "$(gh api user --jq '.login')"

git add -A
git commit -m "Add skill: <技能名> (<英文别名>)

De-identified and packaged. grep self-check clean: no PII / credentials / internal IPs."
git push 2>&1 | tail -2
```

### Step 7: 报告

向用户报告:入库路径、脱敏自检结果(确认零命中)、commit hash、远端链接(`<remote>/tree/main/skills/<技能名>`)。

---

## 注意事项

- **公共库 = 对外发布**,脱敏宁多勿少;任何疏漏一旦 push 就进了 git 历史,极难清除。
- **每个技能都必须单独过 Step 4 自检**,不能因为"看起来干净"就跳过。
- **中文文件夹名**:git/GitHub 支持 UTF-8,macOS/Linux 无碍;若主要面向 Windows 用户可改用英文/拼音。
- **先 pull 再 push**(Step 0),多设备/多 session 发布避免冲突。
- 提交身份用 noreply email,使 git 历史不暴露真实邮箱(即便仓库转 Public)。
