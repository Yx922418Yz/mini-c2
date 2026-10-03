# C2 提交包：AI for Math 论文

**论文标题**：From Natural Language to Verifiable Reasoning: A Semantic Reduction Framework for Reliable AI Mathematics
（从自然语言到可验证推理：面向可靠 AI 数学的语义规约框架）

挑战 ID：ch-20260717031343-8ot0ji（C2）

## 核心论点

AI 数学系统的可靠性既不取决于生成端，也不取决于最终的检查器，而取决于二者之间的**语义规约层**——把自然语言推理转换为带类型、可计算对象的那个（部分）映射。规约失败则验证器「无物可查」，幻觉在原理上不可检测；规约成功则验证是确定性的、可做到可靠（sound）。

## 交付物清单

| 文件 | 说明 | 对应要求 |
|---|---|---|
| `paper.tex` | 论文主文件，自包含（图用 TikZ 绘制），可独立编译 | required |
| `references.bib` | BibTeX 文献库，23 篇（≥8），均经独立来源核验，以一手文献为主 | required |
| `paper.pdf` | 编译产物 | 验证用 |
| `AI协作日志.md` | 每日 AI 协作日志，含文献核验台账与 6 个 AI 误导案例 | required（`*AI日志*`） |
| `C2_AAR七维复盘.md` | 七维 AAR 复盘，含问题、根因、改进计划与 rubric 自评 | required（`*AAR*`） |
| `artifacts/reduction_case_study.py` | 可复现参考实现（仅 Python 标准库，种子固定） | 增强材料 |
| `artifacts/case_study_results.json` | 脚本运行的原始结果数据 | 增强材料 |

## 原创贡献

1. 生成—语义规约—验证的**三层分解**，并定位规约层为可靠性瓶颈；
2. **Typed-IR 流水线**（generate → IR → verify → render）与双向一致性要求；
3. 可逐条审计的**十条 AI4Math 可靠性清单**；
4. 可复现的最小案例：36 个问题实例，可验证率 0.833，90 个可验证候选判定全部正确，18 个候选不可验证。

## 编译方法

需要 LaTeX 发行版（已在本机用 MiKTeX 25.12 验证；TeX Live 同样可用）：

```bash
latexmk -pdf paper.tex
```

或手动：

```bash
pdflatex paper
bibtex   paper
pdflatex paper
pdflatex paper
```

## 复现案例

```bash
cd artifacts
python reduction_case_study.py
```

固定随机种子 20261002，输出与论文 Table「Case study results」一致。

## 投稿前待办

- 将 `paper.tex` 中的匿名作者块替换为真实姓名与单位；
- 按目标 venue 模板调整格式与页数；
- 离线复现：归档宏包版本或提供容器化构建。
