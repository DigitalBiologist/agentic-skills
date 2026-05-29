# 发布到技能库 — 配置指南

一个**元技能**:把本地开发成熟的 Claude Code 技能**脱敏后发布到一个 GitHub 公共技能库**(本库就叫 agentic-skills),并完成入库、更新索引、版本提交、推送的全套流程。

和 `技能分享`(打包发给单个朋友)的区别:本技能面向**持续维护一个公开、可共享的技能集**。

**纯指令技能,零依赖**;唯一外部要求是装好并登录了 `git` + GitHub CLI(`gh`)。

---

## 1. 前置条件

| 依赖 | 用途 |
|------|------|
| `git` | 版本控制、提交、推送 |
| GitHub CLI `gh`(已 `gh auth login`) | 创建/读取仓库、动态拼接 noreply 提交身份 |
| 一个 agentic-skills 风格的仓库 | 发布目标(本库即是;fork 即可拥有自己的) |

## 2. 配置环境变量

无需环境变量。仓库地址从本地 repo 的 git remote **动态读取**,提交身份用 `gh api user` **动态拼接**,都不写死。

## 3. 安装依赖

```bash
# macOS
brew install gh        # git 通常已自带
gh auth login          # 首次登录 GitHub
```

## 4. 放置文件

```bash
# Claude Code（文件夹形式）
cp -r 发布到技能库 ~/.claude/commands/
```

## 5. 测试

新开 session 后:「把 XXX 技能发布到技能库」或「/发布到技能库 XXX」。agent 会:同步仓库 → 脱敏源技能 → 按结构入库 → 生成配置指南 → grep 自检零命中 → 更新 README 索引 → commit + push → 报告 commit hash 和远端链接。

## 6. 配置为技能

放进 `~/.claude/commands/` 后自动发现(凭 `SKILL.md` frontmatter)。触发词:「发布技能 / 发布到技能库 / 把 XXX 加进 agentic-skills / 上传技能到公共库」。

---

## fork 本库的人怎么用

本技能的仓库地址和提交身份都是运行时动态解析的,所以你**只需要**:

1. fork 或新建一个同结构的仓库(`skills/<名>/SKILL.md` + 顶层 `README.md` 索引表)。
2. clone 到本地,把技能里的 `REPO_LOCAL` 改成你的本地路径。
3. `gh auth login` 成你自己的账号。

之后远端地址、noreply 邮箱都会自动跟随你的登录,发布到**你自己的**库,不会带入本库作者的任何信息。

## 使用示例

1. **发布单个新技能** —— "把 生成脑图 发布到技能库",脱敏后入库 `skills/生成脑图/`、更新索引、推送。
2. **批量上新** —— 逐个发布;每个都单独过 grep 自检。
3. **fork 后建自己的技能站** —— 指向自己的仓库,把常用技能陆续发布上去做版本控制。

## 常见问题

**Q: 和 `技能分享` 到底用哪个?**
A: 只想把一个技能发给某人 → `技能分享`(打包成 kit 文件夹)。想长期维护一个公开技能仓库、做版本控制和共享 → 本技能。

**Q: 会暴露我的真实邮箱吗?**
A: 不会。提交身份用 GitHub noreply email(`<id>+<login>@users.noreply.github.com`),即便仓库转 Public,git 历史也只显示 noreply 地址。

**Q: push 报冲突?**
A: 多设备/多 session 发布时先 `git pull --ff-only`(技能 Step 0 已包含)。

**Q: 脱敏不彻底会怎样?**
A: 一旦 push 进公共库的 git 历史,极难彻底清除。所以 Step 4 的 grep 自检是硬关卡,且 grep 之外必须通读全文。
