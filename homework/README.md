# Homework 1: Compare Sorting
Insertion Sort + optimized Bubble Sort (class algorithms), Heap Sort (self-study).

## Run the code (Python 3.10 or later)
Open a terminal in this folder:
```bash
python3 verify.py
python3 demo.py
python3 benchmark.py
```
On Windows, use `python` instead of `python3` if necessary.
Sorting, validation and experiments use only the Python standard library.

## Regenerate the charts and report
```bash
python3 -m pip install -r requirements.txt
python3 build_report.py --student-id YOUR_STUDENT_ID --repo-url https://github.com/YOUR_ACCOUNT/YOUR_REPOSITORY
```
Use your actual student ID and actual repository URL. This reads the saved experimental results; it does not repeat the experiment. A new benchmark overwrites the CSV data, so regenerate the report afterward to keep them consistent. The supplied results were measured by Codex in a Linux environment, as disclosed in the report.

## Files
- `sorting.py`: three in-place algorithms; optional key function and counters.
- `verify.py`: exhaustive small inputs, random inputs and tagged-record checks.
- `demo.py`: numerical example and write-by-write traces saved in `results/demo.json`.
- `benchmark.py`: reproducible timing, counting and separately traced memory.
- `build_report.py`: linear-axis charts and PDF / Markdown report.
- `results/raw.csv`: individual timings and counts.
- `results/summary.csv`: medians, min/max times and mean counts.
- `results/environment.json`: seed, runtime and memory results.
- `results/verification.json`: correctness checks and stability example.
- `report/Sorting_Report.pdf`: English report with editable ID / URL fields.
- `report/REPORT.md`: editable report source.

## 中文提交步骤
1. 解压代码包。在 GitHub 建立一个仓库，例如 `sorting-homework1`。
2. 点击 Add file → Upload files，将本文件夹里的文件和子文件夹上传（不要只上传 ZIP）。确认 `sorting.py` 能在仓库中直接找到。
3. 复制仓库网址，例如 `https://github.com/你的用户名/sorting-homework1`。
4. 用上面的 `build_report.py` 命令填写真实学号和网址后生成 PDF；或用支持 PDF 表单的阅读器填写首页底部的两个可编辑栏，并保存。
5. 在 GitHub 仓库点击 Code → Download ZIP。老师指定用此功能下载 ZIP，最终提交请使用 GitHub 下载的版本。
6. 在 LearnUs 提交 PDF、仓库 URL 和从 GitHub 下载的代码 ZIP。打开最终 PDF 检查学号和网址已经保存。截止时间为韩国时间 2026/09/30 23:59。

报告写明 AI 协助和实际执行环境。提交前请阅读代码与报告，理解堆排序的建堆、提取最大值及稳定性示例。
