# 提交技能 — 配置指南

新手专用技能：让你的 Claude **替你**把一个写好的技能提交到大家共享的 `agentic-skills` 仓库（自动建分支、commit、push、开 Pull Request）。你不用懂 git，说一句话就行。

## 前置条件

| 需要 | 怎么搞定 | 检查命令 |
|------|----------|----------|
| GitHub CLI (`gh`) | macOS: `brew install gh`；其它见 https://cli.github.com | `gh --version` |
| 已登录 GitHub | `gh auth login` → 选 **GitHub.com → HTTPS → Login with a web browser**，照提示在浏览器点确认 | `gh auth status` |
| 是仓库协作者 | 等管理员邀请，去 https://github.com/DigitalBiologist/agentic-skills/invitations 点接受 | （没接受也行，技能会自动改用 fork） |
| git 装好了 | macOS 自带；首次会让你设 user.name/email（本技能会自动用 noreply 邮箱，无需手动设） | `git --version` |

> 不需要任何 API Key 或付费服务。

## 安装

把这个文件夹拷进你的 Claude Code 技能目录：

```bash
cp -r 提交技能 ~/.claude/commands/
```

然后**重启 Claude Code**（或开个新会话），技能就会被自动发现。

## 怎么用（测试一下）

在 Claude Code 里随便说一句，比如：

```
帮我把 ~/.claude/commands/我的新技能 提交到 agentic-skills
```

或直接：

```
/提交技能 我的新技能
```

Claude 会：同步仓库 → 把技能放进你的个人暂存区 `contrib/<你的名字>/<技能名>/` → 跑一遍脱敏快速检查 → 建分支、commit、push → 开一个 Pull Request → 把 PR 链接给你。之后等管理员合并即可。

## 常见问题 (FAQ)

**Q：我还没被加成协作者，能用吗？**
能。技能检测到你没有 push 权限时会自动改用 fork 方式提 PR，流程对你完全一样。

**Q：会不会不小心改坏 main 分支？**
不会。main 开了分支保护，你（非管理员）只能提 PR，改不了 main。所有合并都要管理员点确认。

**Q：提交前要自己脱敏吗？**
技能会自动跑一遍快速 grep 检查（API Key / 密码 / Token / 个人姓名 / 家目录路径 / 内网 IP）。但**公开库无小事**，建议你自己也扫一眼有没有私密信息。完整清单见仓库根目录 `CONTRIBUTING.md`。

**Q：提交后多久能进库？**
你的技能会先进**个人暂存区** `contrib/<你的名字>/`（管理员审核合并后）。这里是大家试用、给你反馈的地方；公认好用的，管理员会把它**提升**进正式 `skills/` 库。先有人用、有反馈再进正式库——这样你的技能更有底，大家也更有参与感。

**Q：完全不想用命令行/gh 行不行？**
行。见 `SKILL.md` 末尾的"纯网页 3 步"备选方案，全程在浏览器里点。

## 依赖与第三方组件

- 仅依赖 `gh`（GitHub CLI，官方工具，MIT 许可）和 `git`。无其它第三方库、无网络服务、无密钥。
