# english-memory-ai

这是一个 **“英语版 memory-work” 的可行性 MVP**（本地可跑、可扩展）。

## 你现在得到的能力
- 用 CSV 导入你想记忆的词组/表达。
- 每天列出应复习条目（due list）。
- 每次复习后记录自评（0-5），自动更新下次复习日期（简化版 SM-2）。
- 记录复习日志，方便后续分析学习质量。
- 提供可直接喂给 ChatGPT 的复盘提示词模板。

## 项目结构

- `app/english_memory_work.py`：CLI 主程序。
- `data/sample_phrases.csv`：示例输入数据。
- `templates/review_prompt.md`：复习时与 AI 对话模板。
- `data/phrases.json`：导入后生成（数据库）。
- `data/review_log.jsonl`：复习日志。

## 快速开始

> 需要 Python 3.10+（仅标准库）。

1) 导入示例词条：

```bash
python app/english_memory_work.py import-csv --csv data/sample_phrases.csv