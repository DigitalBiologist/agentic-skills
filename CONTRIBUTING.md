# Contributing — and the de-identification rule

This repo is **public-facing**. Every skill must be de-identified *before* it is committed, because once a secret lands in git history it is extremely hard to remove.

## The golden rule

> 任何技能在 commit 前,必须跑一遍脱敏流程,并用 `grep` 对该技能文件夹做全量自检,确认零命中。

We use the `技能分享` (skill-share) workflow to do this automatically, but the checklist below is the source of truth.

## De-identification checklist

Before adding `skills/<name>/`, scan every file in it (the skill `.md`, plus any `.py`/`.sh`/`.yaml`/`.json`/templates/references it references) and strip:

### Credentials (highest priority)
- [ ] API keys (`sk-…`, `key-…`, `token=…`, long random strings) → keep the variable name, delete the value
- [ ] Passwords (`password:`, `passwd`, `sshpass -p`) → `<YOUR_PASSWORD>`
- [ ] Tokens / secrets / bearer strings → placeholder
- [ ] SSH key paths / `IdentityFile` → generic path

### Personal info
- [ ] Personal usernames (e.g. local account names) → `<YOUR_USERNAME>`
- [ ] Emails → `your@email.com`
- [ ] Real names of team members → remove or use example names
- [ ] Organization / institution names → remove or generalize

### Infrastructure
- [ ] Internal IPs (`172.16.x.x`, `192.168.x.x`, `10.x.x.x`) → `<YOUR_SERVER_IP>`
- [ ] Public IPs / owned domains → `<YOUR_SERVER>`
- [ ] SSH `Host`/`User`/port config → template form
- [ ] NAS/HPC absolute paths → `<YOUR_NAS_PATH>` etc.
- [ ] Hard-coded personal home paths (`/Users/<you>/…`) → `~/…` or placeholder

### Subscriptions / services
- [ ] VPN / clash subscription URLs (often contain tokens) → delete the line
- [ ] Paid-service account IDs → delete or replace

## Self-check (mandatory)

After writing the de-identified files, run a grep sweep over the skill folder. **All of these must return zero matches** (adjust the personal terms to your own):

```bash
cd skills/<name>
grep -rniE 'sk-[a-z0-9]|password|passwd|secret|bearer|token=' .
grep -rniE 'augustsirius|jiangheng|蒋恒|郭天南|西湖|westlake' .
grep -rnE '172\.16\.|192\.168\.|10\.[0-9]+\.' .
grep -rniE 'subscribe|clash.*url|订阅' .
```

If anything matches → fix and re-scan until clean. Only then `git add`.

## Each skill folder must contain

1. The skill file (`<name>.md` or `SKILL.md` + helpers), de-identified.
2. A `README-配置指南.md` covering: prerequisites, env vars (with `.zshrc` template), dependencies, where to place files, and one runnable test command.

## After adding a skill

Add a row to the **Skills index** table in [README.md](README.md).
