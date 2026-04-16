# Reddit 创业机会发现工具

从 Reddit 子版块爬取热门帖子和评论，使用 AI 分析创业点子的可行性、市场潜力和落地优先级，生成结构化报告。

## 功能

- 爬取指定子版块的热门帖子（按时间范围筛选）
- 收集帖子和评论内容
- 使用 Claude AI 进行多维度分析
- 生成 Markdown 报告

## 快速开始

### 1. 安装依赖

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置 API 凭证

编辑 `config.json`，填入以下凭证：

**Reddit API：**
- 访问 https://www.reddit.com/prefs/apps
- 创建 "script" 类型应用
- 获取 `client_id` 和 `client_secret`

**Claude API：**
- 访问 https://console.anthropic.com
- 创建 API Key

### 3. 运行工具

```bash
# 一键运行（默认 Past Month）
./run.sh

# 或使用命令行参数
python reddit_ideas.py --time month
python reddit_ideas.py --time week --top 20
```

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--time` | 时间范围：week/month/year/all | 必填 |
| `--subreddits` | 子版块列表，逗号分隔 | SomebodyMakeThis,AppIdeas,Startup_Ideas |
| `--top` | 分析热度 Top N 的帖子 | 15 |
| `--output` | 输出目录 | ./reports/ |

## 输出

- `data/YYYY-MM-DD.json` - 原始爬取数据
- `reports/YYYY-MM-DD-report.md` - 分析报告

## 默认监控子版块

- **r/SomebodyMakeThis** - 用户直接发布产品需求
- **r/AppIdeas** - 软件/App 点子
- **r/Startup_Ideas** - 完整创业点子

## 项目结构

```
reddit-idea-finder/
├── reddit_ideas.py      # 主程序
├── config.json          # API 凭证配置
├── run.sh               # 一键启动脚本
├── requirements.txt     # Python 依赖
├── config.py            # 配置加载模块
├── crawler/             # 爬取模块
│   ├── reddit_client.py # Reddit API 客户端
│   └── fetcher.py       # 数据爬取逻辑
├── analyzer/            # 分析模块
│   ├── claude_client.py # Claude API 客户端
│   └── analyzer.py      # 分析逻辑
├── generator/           # 报告生成模块
│   └── report.py        # Markdown 报告生成
├── data/                # 原始数据存储
└── reports/             # 报告输出
```

## 测试

```bash
source venv/bin/activate
pytest tests/ -v
```