# CVPR Extractor Demo

快速脚本示例，可以从 CVPR 官方网站的 “Accepted Papers” 页面下载并解析最新会议（默认 2024 年）的论文信息。输出内容包含标题、作者、分会场/展位信息等，支持关键字过滤，并会自动把结果保存到 `cvpr_<year>_accepted.json`，方便在 1 月 17 日前展示一个可运行的 demo。

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python cvpr_extractor.py --year 2024 --limit 5
```

如果你只需要包含某个关键字（例如 diffusion）的论文，脚本会保存默认 JSON 并打印到终端；也可以额外指定文件名：

```bash
python cvpr_extractor.py --keyword diffusion --limit 20 --json diffusion.json
```

若只想看输出而不落盘，追加 `--no-json`。

## 输出示例

```
1. Guided Slot Attention for Unsupervised Video Object Segmentation
   Session: Poster Session 1 & Exhibit Hall
   Location: Arch 4A-E Poster #352
   Authors: Minhyeok Lee, Suhwan Cho, Dogyoon Lee, Chaewon Park, Jungho Lee, Sangyoun Lee

Displayed 1 records.
```

## 工作流概览

- `cvpr_extractor.py`：核心脚本，负责下载 CVPR 页面、解析 HTML、提取结构化数据，并提供简单的 CLI 参数（年份、关键字、数量限制、JSON 导出）。
- `requirements.txt`：运行脚本的最小依赖（`requests` + `beautifulsoup4`）。

下一步可以将 JSON 上传到数据库或前端，或者把脚本封装成 API/定时任务，根据项目 1 的展示要求调整输出即可。
