# contrib — community staging area

This is where new contributors and interns share **work-in-progress** skills before they join the main [`skills/`](../skills/) library.

- Each person gets their own folder: **`contrib/<your-name>/`**.
- Anyone can install a staging skill to try it out:
  ```bash
  cp -r contrib/<name>/<skill-name> ~/.claude/commands/
  ```
- Tried one? **Leave feedback** — open an issue, comment on the PR, or tell the maintainer. That feedback is how a skill earns its way into the shared library.
- When the team agrees a skill is genuinely useful, a maintainer **promotes** it into [`skills/`](../skills/) and removes it from this list.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the de-identification rule and the full `contrib → skills` promotion workflow.

## In staging now

### contrib/songyixuan/ — songyixuan

| Skill | What it does |
|-------|--------------|
| [虚拟细胞论文建模提取](songyixuan/虚拟细胞论文建模提取) <br>(virtual-cell paper modeling extractor) | Extract a single E. coli / bacterial paper into modeling-ready evidence and produce an interactive markmap HTML: strains, conditions, genes, metabolites, pathways, data, model hypotheses, limitations, and parameter gaps. |
| [代谢工程改造清单生成](songyixuan/代谢工程改造清单生成) <br>(metabolic-engineering model checklist) | Convert metabolic-engineering papers or strain designs into a modeling/FBA operation checklist and interactive markmap HTML: knockouts, overexpression, attenuation, transporters, reaction/GPR candidates, approximations, and validation readouts. |
| [虚拟细胞文献网络](songyixuan/虚拟细胞文献网络) <br>(virtual-cell literature network) | Connect multiple E. coli / bacterial papers into an interactive markmap evidence network: shared genes, metabolites, pathways, phenotypes, support/conflict links, integrated modeling hypotheses, risks, and next modeling steps. |
