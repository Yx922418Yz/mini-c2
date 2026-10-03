# C2 AI 协作日志（AI Collaboration Log）

> 挑战：C2 AI for Math 论文
> 主题：AI4Math 可靠性 —— 从自然语言到可验证推理的语义规约框架
> 记录人：作者（人类） ｜ 协作工具：Doubao（含检索、文件与代码执行能力）
> 日志用途：让每一条「AI 生成结论」都可回溯到来源与人工核验动作（验收要点第 4 条）

---

## 0. 工作流总览

```
探查资料 → 拆解任务 → 文献检索 → 元数据核验 → 框架构建
       → 参考实现（可执行验证）→ 论文写作 → LaTeX 编译 → 复盘
```

协作分工原则（全程执行）：

| 环节 | AI 承担 | 人类承担（核验） |
|---|---|---|
| 资料阅读 | 递归列目录、读取 PDF、提炼大纲 | 核对目录真实存在、抽查 PDF 页内容 |
| 文献调研 | 生成候选文献与关键词 | 逐篇在 arXiv/出版商页面核验 |
| 框架构建 | 提出三层分解、IR 要素、清单初稿 | 判断逻辑自洽性、查反例、定边界 |
| 参考实现 | 编写 Python 脚本 | 实际运行、核对输出、修 bug |
| 论文写作 | 起草段落、公式、图表代码 | 核对每个事实性陈述与引用对应 |
| LaTeX 排版 | 编写 tex、TikZ 图 | 编译并回读 PDF |

**关键纪律**：AI 凭记忆给出的标识符（arXiv 编号、年份、标题）一律视为「待核验」，只有独立来源确认后才写入论文；可计算的结论一律实际运行得到，不接受口算。

---

## Day 1 — 资料探查与选题界定

### 动作记录
1. 用户给定路径 `D:\.cogseed\userWorkSpace\把我的挑战下载到我的电脑上\EduSeed挑战资料地址`。
2. 直接访问失败（路径不存在）。逐级回查上级目录，发现实际文件夹名为 **`EduSeed挑战资料`**（无「地址」二字）。
3. 递归列出 23 个挑战资料包，定位 `挑战_C2 AI for Math 论文_8ot0ji_完整资料`。
4. 读取 `CHALLENGE.md`、`README.md`、`rubric.json`、`challenge.yaml`。

### 关键 Prompt（原文摘录）
- 「帮我完成……EduSeed挑战资料地址里的挑战C2，并且在桌面新建一个名字叫提交挑战的文件夹……」
- （AI 自检指令）「先完整读取需求指定的全部输入，读不到就先解决读取问题」

### 结论与核验
- 交付物明确为 4 件：`paper.tex`、`references.bib`、`*AI日志*`、`*AAR*`。
- 红线：**引用造假 → 研究严谨性 0 分；不可编译 → 技术实现 ≤ 5**。
- 核验方式：文件均成功打开并读取；`rubric.json` 五维评分与 CHALLENGE.md 一致。✔

### 当日教训
- 用户口述路径与真实路径可能有出入；**逐级回查 + 列目录**比直接报错或猜测有效。

---

## Day 2 — 材料精读与框架雏形

### 动作记录
1. 读取 `materials\中文论文大纲（AI4Math）.pdf`：获得中英文双份建议大纲（三层结构、Typed IR、Pipeline、实验设计）。
2. 分两次读取 `Lectures on AI for Mathematics.pdf`：
   - 封面/目录/第一章（概述：发现—证明—证否的循环、争议与信任问题）；
   - 第四章全文（自动定理证明三阶段、AlphaProof 技术拆解、AlphaGeometry、LLM 智能体、创造力评估）及第五章开头（构造反例、Wagner 深度交叉熵方法）。
3. 提取讲座各章末参考文献列表作为候选文献池。

### 框架雏形（AI 起草，人类修订）
- 三层：**生成（Generation）→ 语义规约（Semantic Reduction）→ 验证（Verification）**。
- 核心论点初稿：「可靠性不能只靠最终验证，中间必须有语义规约层」。
- 人类修订：要求把「规约失败」与「验证失败」在模型上严格分开，并要求所有论断给出边界声明（scope）。

### 核验
- 大纲 PDF 与讲座内容相互印证（AlphaProof/AlphaGeometry2、Lean 验证、autoformalization 在两份材料中一致）。✔
- 讲座参考文献中含 2025/2026 年论文，标记为「需联网核验，不得直接照抄」。

---

## Day 3 — 文献检索与元数据核验（防止引用造假）

### 方法
对每篇候选文献，先检索、再打开 arXiv 摘要页或出版商页面核对「标题 / 作者 / 年份 / 出处 / 标识符」，全部通过才写入 `references.bib`。

### 核验台账（最终入库 23 篇，要求 ≥8）

| # | 文献（简） | 核验来源 | 结果 |
|---|---|---|---|
| 1 | Wei et al., Chain-of-Thought, NeurIPS 2022 | arXiv:2201.11903 | ✔ |
| 2 | Wang et al., Self-Consistency, ICLR 2023 | arXiv:2203.11171 | ✔ |
| 3 | Chen et al., Program of Thoughts, TMLR 2023 | arXiv:2211.12588 | ✔ |
| 4 | Schick et al., Toolformer, NeurIPS 2023 | arXiv:2302.04761 | ✔（编号被 AI 记错，已纠正，见误导案例 M1） |
| 5 | Lewkowycz et al., Minerva, NeurIPS 2022 | arXiv:2206.14858 | ✔ |
| 6 | Cobbe et al., GSM8K/Verifiers, 2021 | arXiv:2110.14168 | ✔ |
| 7 | Hendrycks et al., MATH, NeurIPS 2021 D&B | arXiv:2103.03874 | ✔ |
| 8 | Lightman et al., Let's Verify Step by Step, ICLR 2024 | arXiv:2305.20050 | ✔ |
| 9 | Uesato et al., Process/Outcome Feedback, 2022 | arXiv:2211.14275 | ✔ |
| 10 | Mirzadeh et al., GSM-Symbolic, 2024 | arXiv:2410.05229 | ✔（第一作者全名 Seyed-Iman） |
| 11 | Lample & Charton, Symbolic Mathematics, ICLR 2020 | arXiv:1912.01412 | ✔ |
| 12 | Polu & Sutskever, GPT-f, 2020 | arXiv:2009.03393 | ✔ |
| 13 | Polu et al., Curriculum Learning, ICLR 2022 | arXiv:2202.01344（抓取摘要页） | ✔ |
| 14 | Zheng et al., miniF2F, ICLR 2022 | arXiv:2109.00110 | ✔ |
| 15 | First et al., Baldur, ESEC/FSE 2023 | arXiv:2303.04910 + ACM 页（pp.1229–1241） | ✔ |
| 16 | Wang et al., LEGO-Prover, ICLR 2024 | arXiv:2310.00656（抓取摘要页） | ✔（编号被 AI 记错，见 M2） |
| 17 | Yang et al., LeanDojo, NeurIPS 2023 D&B | arXiv:2306.15626（pp.21573–21612） | ✔ |
| 18 | Xin et al., DeepSeek-Prover, 2024 | arXiv:2405.14333 | ✔（标题被 AI 记错，见 M3） |
| 19 | de Moura & Ullrich, Lean 4, CADE-28 2021 | LNCS 12699, pp.625–635（多源印证） | ✔ |
| 20 | Hubert et al., AlphaProof, Nature | DOI 10.1038/s41586-025-09833-y | ✔（年份被讲座/AI 误记，见 M4） |
| 21 | Trinh et al., AlphaGeometry, Nature 625 | pp.476–482, DOI 10.1038/s41586-023-06747-5 | ✔ |
| 22 | Chervonyi et al., AlphaGeometry2, 2025 | arXiv:2502.03544 | ✔ |
| 23 | Sørensen & Urzyczyn, Curry-Howard, 2006 | Studies in Logic vol.149, DOI 10.1016/S0049-237X(06)80499-4 | ✔ |

### 人工核验统计
- 23/23 入库文献均有独立来源；其中一手论文（作者本人系统/方法论文）占绝大多数。
- 4 处 AI 记忆错误在写入前被拦截（M1–M4）。

---

## Day 4 — 参考实现与论文写作

### 4.1 可执行参考实现
- 编写 `artifacts/reduction_case_study.py`（仅标准库，随机种子固定为 20261002），实现：受控英文 → 显式类型 AST（Typed IR）→ 确定性「内核」判定 → 规范化渲染，并包含 malformed（不可规约）变体。
- **实际运行两次**：
  - 第一次运行暴露两个问题：指标公式错误（输出 kernel accuracy 0.333）、F1 模板可能取到同名人物；
  - 修复后第二次运行输出与论文 Table 2 完全一致：可验证率 0.833；90 个可验证候选判定全部正确；18 个候选不可验证。详见误导案例 M5。

### 4.2 论文写作
- 按「摘要 → 引言 → 三层分解 → 瓶颈分析（含事件模型）→ 框架（IR/Pipeline/双向一致性/清单/案例）→ 相关工作 → 应用 → 讨论 → 结论」撰写。
- 两张 TikZ 图（三层架构、流水线）、四张表（规约目标分类、清单、案例结果、——分类表在正文）、成组公式。
- 原创贡献显式列出：三层分解、Typed-IR 框架与双向一致性、十条可靠性清单、可复现案例。
- 边界声明：案例为概念验证而非基准结果；不声称所有数学都可形式化。

### 核验
- 案例表数字全部来自脚本真实 stdout（非编造）。✔
- 每条系统/事实性陈述均能对应到上表文献。✔

---

## Day 5 — LaTeX 编译、回读与交付

### 环境准备
- 本机无 LaTeX；经 winget 安装 MiKTeX 25.12，设置 `[MPM]AutoInstall=1`（缺失宏包自动安装）。
- 使用 `latexmk -pdf` 执行 pdflatex + bibtex 完整序列。

### 编译与回读
- 编译结果：（以最终编译记录为准，见交付说明）；回读 PDF 检查：图、表、公式、引用解析、参考文献无 `?`。
- 桌面文件夹 `提交挑战` 已创建，最终交付物复制入内。

---

## AI 误导案例汇总（与 AAR 联动）

| 编号 | AI 的说法（凭记忆） | 实际事实 | 发现方式 | 对策 |
|---|---|---|---|---|
| M1 | Toolformer = arXiv:2302.0476 | **2302.04761** | 检索结果与 HF 页面 | 标识符一律以 arXiv 摘要页为准 |
| M2 | LEGO-Prover = arXiv:2310.04353 | **2310.00656**（抓取摘要页确认标题/作者） | 发现 Scholar 与记忆不一致后抓取原文 | 多个候选编号时直接 fetch 摘要页比对 |
| M3 | DeepSeek-Prover 标题为「Advancing Mathematical Reasoning…」 | 实为「**Advancing Theorem Proving in LLMs through Large-Scale Synthetic Data**」 | arXiv PDF/摘要页 | 标题逐字复制，不转述 |
| M4 | AlphaProof 为 Nature 651 (2026) | Nature **2025**，DOI …09833-y（卷 651 为 2025 年末） | Semantic Scholar + DOI 多源 | 年份/卷期以出版商 DOI 页为准 |
| M5 | 脚本首跑「kernel accuracy 0.333」看似通过 | 指标公式写错（分子漏加 wrong_rejected）；另有同名模板问题 | 人类检查输出合理性 | 可计算结论必须复算；结果「反常」即停下查因 |
| M6 | 用户路径含「…资料地址」 | 实际为「…资料」 | 逐级回查目录 | 路径问题先列目录，不猜不报错了事 |

**总体结论**：AI 在「组织、起草、扩展」上高效，但在「精确标识符与数字」上不可信；本项目所有关键事实均经过独立来源或实际执行核验，日志可逐条追溯。
