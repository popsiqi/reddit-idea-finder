# Reddit Startup Idea Finder

A CLI tool that crawls hot posts from Reddit communities, analyzes startup ideas using Claude AI, and generates structured reports on feasibility, market potential, and implementation priority.

## Features

- Crawl top posts from specified subreddits (filtered by time range)
- Collect post content and comments
- Multi-dimensional AI analysis using Claude
- Generate Markdown reports

## Quick Start

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Credentials

Copy the example config and fill in your credentials:

```bash
cp config.example.json config.json
```

Edit `config.json`:

**Reddit API:**
- Visit https://www.reddit.com/prefs/apps
- Create a "script" type application
- Get `client_id` and `client_secret`

**Claude API:**
- Visit https://console.anthropic.com
- Create an API Key

### 3. Run the Tool

```bash
# Quick run (default: Past Month)
./run.sh

# Or use CLI arguments
python reddit_ideas.py --time month
python reddit_ideas.py --time week --top 20
```

## CLI Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--time` | Time range: week/month/year/all | Required |
| `--subreddits` | Subreddit list (comma-separated) | SomebodyMakeThis,AppIdeas,Startup_Ideas |
| `--top` | Analyze top N posts by score | 15 |
| `--output` | Output directory | ./reports/ |

## Output

- `data/YYYY-MM-DD.json` - Raw crawled data
- `reports/YYYY-MM-DD-report.md` - Analysis report

## Default Subreddits

- **r/SomebodyMakeThis** - Users post product requests directly
- **r/AppIdeas** - Software/App ideas
- **r/Startup_Ideas** - Full startup ideas with market analysis

## Project Structure

```
reddit-idea-finder/
├── reddit_ideas.py          # Main program
├── config.json              # API credentials (create from example)
├── config.example.json      # Configuration template
├── run.sh                   # Quick start script
├── requirements.txt         # Python dependencies
├── config.py                # Config loader module
├── crawler/                 # Crawling module
│   ├── reddit_client.py     # Reddit API client
│   └── fetcher.py           # Data fetching logic
├── analyzer/                # Analysis module
│   ├── claude_client.py     # Claude API client
│   └── analyzer.py          # Analysis logic
├── generator/               # Report generation module
│   └── report.py            # Markdown report generator
├── data/                    # Raw data storage
└── reports/                 # Report output
```

## Testing

```bash
source venv/bin/activate
pytest tests/ -v
```

## License

MIT License - For personal, non-commercial use only.

## Disclaimer

This tool is for personal research purposes only. It respects Reddit's API rate limits and only accesses public post data. It does not:
- Replace any Reddit functionality
- Scrape private user data
- Commercialize Reddit content