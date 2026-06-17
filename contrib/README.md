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

### contrib/louhanzhi/ — louhanzhi

| Skill | What it does |
|-------|--------------|
| [论文下载](louhanzhi/论文下载) <br>(paper downloader) | Batch-download academic paper PDFs from a DOI list: 9-layer download strategy with multiple metadata-API fallbacks, plus async PMC fast path for large batches. Enforces a `_build/` + `pdfs/` layout and emits a `_需手动下载.md` manual-download list for failures. |

> Contributed by **louhanzhi**. This is her authored copy, kept here for attribution; the live skill also ships in [`skills/论文下载`](../skills/论文下载).

### contrib/DimuzBayamo/ — DimuzBayamo

| Skill | What it does |
|-------|--------------|
| [快速阅读论文](DimuzBayamo/快速阅读论文) <br>(fast paper reader) | DimuzBayamo's patched build of the fast-paper-reader skill: PDF → self-contained offline `index.html` (vendored PDF.js), build + render-verify scripts. Staged here for try-out and feedback. |
| [生成脑图](DimuzBayamo/生成脑图) <br>(mind-map generator) | DimuzBayamo's patched build of the mind-map skill: self-contained offline mind maps with vendored d3 + markmap. Staged here for try-out and feedback. |
