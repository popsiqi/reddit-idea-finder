#!/bin/bash
# Reddit 创业机会发现工具 - 一键启动

echo "🚀 启动 Reddit 创业机会发现工具..."

# 检查配置文件是否存在
if [ ! -f "config.json" ]; then
    echo "❌ 配置文件 config.json 不存在"
    echo "请先配置 config.json，参考以下步骤："
    echo "1. 复制 config.json 模板"
    echo "2. 填入 Reddit API 凭证（client_id, client_secret）"
    echo "3. 填入 Anthropic API Key"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "⚠️  虚拟环境不存在，正在创建..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# 运行工具（默认爬取 Past Month）
python reddit_ideas.py --time month

# 报告完成后自动打开（macOS）
if [ -f "./reports/$(date +%Y-%m-%d)-report.md" ]; then
    echo "📄 打开报告..."
    open "./reports/$(date +%Y-%m-%d)-report.md"
fi