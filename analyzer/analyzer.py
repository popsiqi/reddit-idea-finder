"""创业点子分析逻辑"""
from typing import Any
from analyzer.claude_client import ClaudeClient


class Analyzer:
    """创业点子分析器"""

    ANALYSIS_PROMPT_TEMPLATE = """请分析以下 Reddit 帖子作为一个创业机会的可行性。

帖子标题：{title}
帖子内容：{content}
子版块：r/{subreddit}
热度：⬆ {score} · 💬 {num_comments}

评论摘要（前5条最高赞评论）：
{top_comments}

请从以下维度进行分析，并用中文回答：

1. **可行性分析**
   - 技术难度：低/中/高
   - 实现周期：1-2周/2-4周/1-3月/3月以上
   - 所需技能/资源

2. **市场潜力**
   - 目标用户群体
   - 竞品情况（简要）
   - 变现可能性

3. **落地建议**
   - 优先级评分：1-5星（⭐ 到 ⭐⭐⭐⭐⭐）
   - 推荐理由
   - 潜在风险

请用结构化的格式输出。"""

    def __init__(self, client: ClaudeClient):
        """初始化分析器

        Args:
            client: Claude 客户端
        """
        self.client = client

    def analyze_post(self, post_data: dict[str, Any]) -> dict[str, Any]:
        """分析单个帖子

        Args:
            post_data: 帖子数据字典

        Returns:
            分析结果字典
        """
        # 获取前5条最高赞评论
        comments = post_data.get("comments", [])
        top_comments = sorted(comments, key=lambda c: c.get("score", 0), reverse=True)[:5]
        top_comments_text = "\n".join([
            f"- [{c.get('score', 0)}⬆] {c.get('body', '')[:200]}..."
            for c in top_comments
        ]) if top_comments else "无评论"

        prompt = self.ANALYSIS_PROMPT_TEMPLATE.format(
            title=post_data.get("title", ""),
            content=post_data.get("content", ""),
            subreddit=post_data.get("subreddit", ""),
            score=post_data.get("score", 0),
            num_comments=post_data.get("num_comments", 0),
            top_comments=top_comments_text
        )

        analysis_text = self.client.analyze(prompt)

        return {
            "post_id": post_data.get("id"),
            "post_title": post_data.get("title"),
            "analysis": analysis_text
        }

    def analyze_posts(
        self,
        posts: list[dict[str, Any]],
        top_n: int = 15,
        progress_callback: callable | None = None
    ) -> list[dict[str, Any]]:
        """分析多个帖子（按热度筛选 Top N）

        Args:
            posts: 帖子数据列表
            top_n: 分析热度 Top N 的帖子
            progress_callback: 进度回调函数

        Returns:
            分析结果列表
        """
        # 按热度排序
        sorted_posts = sorted(posts, key=lambda p: p.get("score", 0), reverse=True)
        top_posts = sorted_posts[:top_n]

        results = []
        for i, post in enumerate(top_posts):
            try:
                result = self.analyze_post(post)
                results.append(result)

                if progress_callback:
                    progress_callback(i + 1, top_n)
            except Exception as e:
                # 跳过失败的分析，记录错误
                results.append({
                    "post_id": post.get("id"),
                    "post_title": post.get("title"),
                    "analysis": f"分析失败: {str(e)}"
                })

        return results

    def extract_priority(self, analysis_text: str) -> int:
        """从分析文本中提取优先级评分

        Args:
            analysis_text: 分析文本

        Returns:
            优先级评分 (1-5)
        """
        # 简单的星级提取逻辑
        if "⭐⭐⭐⭐⭐" in analysis_text:
            return 5
        elif "⭐⭐⭐⭐" in analysis_text:
            return 4
        elif "⭐⭐⭐" in analysis_text:
            return 3
        elif "⭐⭐" in analysis_text:
            return 2
        elif "⭐" in analysis_text:
            return 1
        return 0