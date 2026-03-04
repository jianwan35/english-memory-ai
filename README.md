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
```

2) 查看今日待复习：

```bash
python app/english_memory_work.py due
```

3) 完成一次复习并打分（0-5）：

```bash
python app/english_memory_work.py review --phrase-id 1 --quality 4 --note "知道意思但例句卡壳"
```

4) 再看待复习列表：

```bash
python app/english_memory_work.py due
```

5) 给不懂命令行的用户：直接用交互模式（推荐）

```bash
python app/english_memory_work.py session
```

交互模式会逐条引导：
- 先自己回忆（不看答案）
- 回车后显示参考含义/例句
- 让你输入 0-5 评分和备注
- 自动写入复习日志并更新下次复习时间

## 如何结合你给的参考对话（chatgpt share）

建议你把流程固定成每日 10-20 分钟：

1. **回忆阶段（不看答案）**：先看 expression，口头解释 + 造句。
2. **AI 反馈阶段**：把你的回忆内容贴到 `templates/review_prompt.md` 模板里，让 AI 严格打分与纠错。
3. **打分入库阶段**：用 `review` 命令把质量分和备注写入。
4. **追踪阶段**：每周回看 `data/review_log.jsonl`，找出总是低分的表达（重点突破）。

## 可行性结论

**可行，而且成本很低。**

这个 MVP 已经覆盖了 memory-work 的核心闭环：
- 捕获知识（import）
- 计划复习（due + schedule）
- 主动回忆（你先答）
- 反馈迭代（AI + 质量分）
- 数据沉淀（review log）

下一步可以升级：
- 增加“主题包”（工作英语/口语/写作）。
- 接入 OpenAI API 自动评分。
- 做一个简单网页前端（可视化复习热力图与遗忘曲线）。


## 发布到 GitHub（解决“仓库里看不到代码”）

如果你本地已经有 commit，但 GitHub 看不到，通常是因为没有配置远程仓库或没有 push。

1) 一键发布（推荐）：

```bash
bash scripts/publish_to_github.sh https://github.com/<你的用户名>/<你的仓库名>.git work
```

2) 或手动执行：

```bash
git remote add origin https://github.com/<你的用户名>/<你的仓库名>.git
git push -u origin work
```

> 如果你希望使用 `main` 分支，请把命令中的 `work` 改为 `main`。
