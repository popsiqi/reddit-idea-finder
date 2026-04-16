"""报告生成器模块"""
from datetime import datetime
from pathlib import Path
from typing import Any


class ReportGenerator:
    """Markdown 报告生成器"""

    def __init__(self, output_dir: str | Path):
        """初始化报告生成器

        Args:
            output_dir: 报告输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        crawl_data: dict[str, Any],
        analysis_results: dict[str, dict[str, Any]],
        top_n: int = 5
    ) -> Path:
        """生成 Markdown 报告

        Args:
            crawl_data: 爬取的数据，包含元数据和帖子列表
            analysis_results: 分析结果，按帖子 ID 索引
            top_n: 高潜力帖子数量

        Returns:
            生成的报告文件路径
        """
        # 生成报告文件名
        now = datetime.now()
        filename = f"startup_ideas_{now.strftime('%Y%m%d_%H%M%S')}.md"
        report_path = self.output_dir / filename

        # 构建报告内容
        content = self._build_report(crawl_data, analysis_results, top_n)

        # 写入文件
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)

        return report_path

    def _build_report(
        self,
        crawl_data: dict[str, Any],
        analysis_results: dict[str, dict[str, Any]],
        top_n: int
    ) -> str:
        """构建报告内容"""
        sections = []

        # 标题
        title = self._build_title()
        sections.append(title)

        # 概览部分
        overview = self._build_overview(crawl_data)
        sections.append(overview)

        # 合并帖子和分析结果
        posts_with_analysis = self._merge_posts_and_analysis(
            crawl_data.get("posts", []),
            analysis_results
        )

        # 按优先级排序
        sorted_posts = sorted(
            posts_with_analysis,
            key=lambda x: self._extract_priority(x.get("analysis", {})),
            reverse=True
        )

        # 高潜力 Top N
        top_posts = self._build_top_posts(sorted_posts[:top_n])
        sections.append(top_posts)

        # 完整分析列表
        full_list = self._build_full_list(sorted_posts)
        sections.append(full_list)

        return "\n\n".join(sections)

    def _build_title(self) -> str:
        """构建报告标题"""
        now = datetime.now()
        return f"# 创业机会发现报告 - {now.strftime('%Y年%m月')}"

    def _build_overview(self, crawl_data: dict[str, Any]) -> str:
        """构建概览部分"""
        metadata = crawl_data.get("crawl_metadata", {})

        lines = ["## 概览", ""]

        # 时间范围
        time_range = metadata.get("time_range", "未知")
        time_range_display = self._format_time_range(time_range)
        lines.append(f"- **时间范围**: {time_range_display}")

        # 子版块
        subreddits = metadata.get("subreddits", [])
        if subreddits:
            subreddit_str = ", ".join(f"r/{s}" for s in subreddits)
            lines.append(f"- **子版块**: {subreddit_str}")

        # 帖子数量
        total_posts = metadata.get("total_posts", 0)
        lines.append(f"- **帖子数量**: {total_posts}")

        # 评论数量
        total_comments = metadata.get("total_comments", 0)
        lines.append(f"- **评论数量**: {total_comments}")

        # 爬取时间
        timestamp = metadata.get("timestamp", "")
        if timestamp:
            lines.append(f"- **爬取时间**: {timestamp}")

        return "\n".join(lines)

    def _format_time_range(self, time_range: str) -> str:
        """格式化时间范围显示"""
        time_range_map = {
            "week": "最近一周",
            "month": "最近一月",
            "year": "最近一年",
            "all": "所有时间"
        }
        return time_range_map.get(time_range, time_range)

    def _merge_posts_and_analysis(
        self,
        posts: list[dict[str, Any]],
        analysis_results: dict[str, dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """合并帖子和分析结果"""
        merged = []
        for post in posts:
            post_id = post.get("id", "")
            analysis = analysis_results.get(post_id, {})
            merged.append({
                "post": post,
                "analysis": analysis
            })
        return merged

    def _extract_priority(self, analysis: dict[str, Any]) -> int:
        """从分析结果中提取优先级

        Args:
            analysis: 分析结果字典

        Returns:
            优先级评分 (0-10)，默认为 0
        """
        if not analysis:
            return 0

        # 支持多种优先级字段名
        priority = analysis.get("priority_rating")
        if priority is None:
            priority = analysis.get("priority")
        if priority is None:
            priority = analysis.get("score")
        if priority is None:
            priority = analysis.get("rating")

        # 确保返回整数
        if priority is not None:
            try:
                return int(priority)
            except (ValueError, TypeError):
                return 0

        return 0

    def _get_post_url(self, post: dict[str, Any]) -> str:
        """获取帖子 URL"""
        return post.get("url", "")

    def _get_post_score(self, post: dict[str, Any]) -> int:
        """获取帖子评分"""
        return post.get("score", 0)

    def _get_post_comments(self, post: dict[str, Any]) -> int:
        """获取帖子评论数"""
        return post.get("num_comments", 0)

    def _get_post_subreddit(self, post: dict[str, Any]) -> str:
        """获取帖子所在子版块"""
        return post.get("subreddit", "")

    def _build_top_posts(self, posts: list[dict[str, Any]]) -> str:
        """构建高潜力 Top N 部分"""
        lines = ["## 高潜力 Top 5", ""]

        if not posts:
            lines.append("*暂无分析结果*")
            return "\n".join(lines)

        for i, item in enumerate(posts, 1):
            post = item.get("post", {})
            analysis = item.get("analysis", {})

            priority = self._extract_priority(analysis)
            title = post.get("title", "无标题")
            url = self._get_post_url(post)
            subreddit = self._get_post_subreddit(post)
            score = self._get_post_score(post)
            comments = self._get_post_comments(post)

            lines.append(f"### {i}. {title}")
            lines.append("")
            lines.append(f"- **优先级**: {priority}/10")
            lines.append(f"- **来源**: r/{subreddit}")
            lines.append(f"- **评分**: {score} | **评论**: {comments}")
            lines.append(f"- **链接**: [{url}]({url})")

            # 添加分析摘要
            summary = analysis.get("summary") or analysis.get("idea_summary") or analysis.get("description")
            if summary:
                lines.append("")
                lines.append(f"**摘要**: {summary}")

            # 添加创业建议
            suggestion = analysis.get("suggestion") or analysis.get("startup_suggestion") or analysis.get("recommendation")
            if suggestion:
                lines.append("")
                lines.append(f"**建议**: {suggestion}")

            lines.append("")

        return "\n".join(lines)

    def _build_full_list(self, posts: list[dict[str, Any]]) -> str:
        """构建完整分析列表"""
        lines = ["## 完整分析列表", ""]

        if not posts:
            lines.append("*暂无分析结果*")
            return "\n".join(lines)

        lines.append("| # | 标题 | 子版块 | 优先级 | 评分 | 评论数 |")
        lines.append("|---|------|--------|--------|------|--------|")

        for i, item in enumerate(posts, 1):
            post = item.get("post", {})
            analysis = item.get("analysis", {})

            title = post.get("title", "无标题")[:50]  # 截断长标题
            if len(post.get("title", "")) > 50:
                title += "..."

            subreddit = self._get_post_subreddit(post)
            priority = self._extract_priority(analysis)
            score = self._get_post_score(post)
            comments = self._get_post_comments(post)

            lines.append(f"| {i} | {title} | r/{subreddit} | {priority}/10 | {score} | {comments} |")

        return "\n".join(lines)