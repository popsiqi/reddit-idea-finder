"""Reddit 创业机会发现工具 - 主程序"""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

from config import load_config, get_output_dir, get_data_dir
from crawler import RedditClient, Fetcher
from analyzer import ClaudeClient, Analyzer
from generator import ReportGenerator


def print_progress(current: int, total: int, context: str = ""):
    """打印进度信息"""
    if context:
        print(f"⏳ {context}... ({current}/{total})")
    else:
        print(f"⏳ 进度... ({current}/{total})")


def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(description="Reddit 创业机会发现工具")
    parser.add_argument(
        "--time",
        required=True,
        choices=["week", "month", "year", "all"],
        help="时间范围：week/month/year/all"
    )
    parser.add_argument(
        "--subreddits",
        default=None,
        help="子版块列表，逗号分隔（默认使用配置中的子版块）"
    )
    parser.add_argument(
        "--top",
        type=int,
        default=15,
        help="分析热度 Top N 的帖子（默认 15）"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="输出目录（默认使用配置中的目录）"
    )
    parser.add_argument(
        "--config",
        default="config.json",
        help="配置文件路径"
    )

    args = parser.parse_args()

    # 加载配置
    print("✓ 加载配置...")
    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        print(f"❌ 配置文件不存在: {e}")
        print("请先创建 config.json，参考 config.json 模板")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        sys.exit(1)

    # 设置子版块
    subreddits = args.subreddits.split(",") if args.subreddits else config["default_subreddits"]

    # 设置输出目录
    output_dir = Path(args.output) if args.output else get_output_dir(config)
    data_dir = get_data_dir(config)

    # 初始化客户端
    print("✓ 连接 Reddit API...")
    reddit_client = RedditClient(config)
    if not reddit_client.test_connection():
        print("❌ Reddit API 连接失败，请检查凭证")
        sys.exit(1)

    print("✓ 连接 Claude API...")
    claude_client = ClaudeClient(config)
    if not claude_client.test_connection():
        print("❌ Claude API 连接失败，请检查 API Key")
        sys.exit(1)

    # 爬取数据
    print("✓ 开始爬取...")
    fetcher = Fetcher(reddit_client, max_comments=config.get("max_comments_per_post", 100))
    crawl_data = fetcher.crawl_all(
        subreddits=subreddits,
        time_filter=args.time,
        posts_limit=50,
        progress_callback=print_progress
    )

    # 保存原始数据
    timestamp = datetime.now().strftime("%Y-%m-%d")
    data_path = data_dir / f"{timestamp}.json"
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(crawl_data, f, ensure_ascii=False, indent=2)
    print(f"✓ 原始数据已保存: {data_path}")

    # 分析帖子
    print("✓ 开始 AI 分析...")
    analyzer = Analyzer(claude_client)
    analysis_results = analyzer.analyze_posts(
        posts=crawl_data["posts"],
        top_n=args.top,
        progress_callback=print_progress
    )

    # 生成报告
    print("✓ 生成报告...")
    generator = ReportGenerator(output_dir)
    report_path = generator.generate(crawl_data, analysis_results, top_n=args.top)

    print(f"\n✓ 报告生成完成！\n")
    print(f"📄 报告路径: {report_path}")

    # 自动打开报告（macOS）
    if sys.platform == "darwin":
        subprocess.run(["open", str(report_path)], check=False)

    return 0


if __name__ == "__main__":
    sys.exit(main())