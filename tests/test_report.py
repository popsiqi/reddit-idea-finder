"""报告生成模块测试"""
import pytest
import tempfile
from pathlib import Path
from generator.report import ReportGenerator


@pytest.fixture
def sample_crawl_data():
    """示例爬取数据"""
    return {
        "crawl_metadata": {
            "timestamp": "2024-04-16T12:00:00+00:00",
            "subreddits": ["SomebodyMakeThis", "AppIdeas"],
            "time_range": "week",
            "total_posts": 3,
            "total_comments": 150
        },
        "posts": [
            {
                "id": "abc123",
                "subreddit": "SomebodyMakeThis",
                "title": "An app that helps you find parking spots",
                "content": "I wish there was an app...",
                "author": "user1",
                "created_utc": 1713264000.0,
                "score": 500,
                "upvote_ratio": 0.95,
                "num_comments": 50,
                "url": "https://reddit.com/r/SomebodyMakeThis/comments/abc123",
                "comments": []
            },
            {
                "id": "def456",
                "subreddit": "AppIdeas",
                "title": "A meal planning app with AI suggestions",
                "content": "Looking for ideas...",
                "author": "user2",
                "created_utc": 1713184000.0,
                "score": 300,
                "upvote_ratio": 0.90,
                "num_comments": 30,
                "url": "https://reddit.com/r/AppIdeas/comments/def456",
                "comments": []
            },
            {
                "id": "ghi789",
                "subreddit": "SomebodyMakeThis",
                "title": "A tool to track job applications",
                "content": "Job hunting is hard...",
                "author": "user3",
                "created_utc": 1713104000.0,
                "score": 200,
                "upvote_ratio": 0.88,
                "num_comments": 20,
                "url": "https://reddit.com/r/SomebodyMakeThis/comments/ghi789",
                "comments": []
            }
        ]
    }


@pytest.fixture
def sample_analysis_results():
    """示例分析结果"""
    return {
        "abc123": {
            "priority_rating": 8,
            "summary": "High demand parking app idea with monetization potential",
            "suggestion": "Focus on real-time data and partnerships with parking garages"
        },
        "def456": {
            "priority_rating": 6,
            "summary": "AI meal planning with good market fit",
            "suggestion": "Consider subscription model with grocery integration"
        },
        "ghi789": {
            "priority_rating": 9,
            "summary": "Job application tracker with high user pain point",
            "suggestion": "Add AI resume optimization feature"
        }
    }


def test_report_generator_init():
    """测试报告生成器初始化"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = ReportGenerator(tmpdir)
        assert generator.output_dir == Path(tmpdir)
        assert generator.output_dir.exists()


def test_report_generator_creates_output_dir():
    """测试自动创建输出目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "reports" / "nested"
        generator = ReportGenerator(output_path)
        assert generator.output_dir.exists()


def test_generate_report(sample_crawl_data, sample_analysis_results):
    """测试生成报告"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = ReportGenerator(tmpdir)
        report_path = generator.generate(sample_crawl_data, sample_analysis_results, top_n=5)

        assert report_path.exists()
        assert report_path.suffix == ".md"
        assert report_path.name.startswith("startup_ideas_")


def test_generate_report_content(sample_crawl_data, sample_analysis_results):
    """测试报告内容正确性"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = ReportGenerator(tmpdir)
        report_path = generator.generate(sample_crawl_data, sample_analysis_results, top_n=5)

        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 检查标题
        assert "创业机会发现报告" in content

        # 检查概览部分
        assert "## 概览" in content
        assert "SomebodyMakeThis" in content
        assert "AppIdeas" in content
        assert "3" in content  # 帖子数量
        assert "150" in content  # 评论数量

        # 检查高潜力部分
        assert "## 高潜力 Top 5" in content

        # 检查完整列表
        assert "## 完整分析列表" in content


def test_extract_priority():
    """测试优先级提取"""
    generator = ReportGenerator("/tmp")

    # 测试 priority_rating
    assert generator._extract_priority({"priority_rating": 8}) == 8

    # 测试 priority
    assert generator._extract_priority({"priority": 7}) == 7

    # 测试 score
    assert generator._extract_priority({"score": 6}) == 6

    # 测试 rating
    assert generator._extract_priority({"rating": 5}) == 5

    # 测试空字典
    assert generator._extract_priority({}) == 0

    # 测试 None
    assert generator._extract_priority(None) == 0

    # 测试无效值
    assert generator._extract_priority({"priority_rating": "invalid"}) == 0


def test_get_post_url():
    """测试获取帖子 URL"""
    generator = ReportGenerator("/tmp")

    post = {"url": "https://reddit.com/r/test/comments/abc"}
    assert generator._get_post_url(post) == "https://reddit.com/r/test/comments/abc"

    # 测试空帖子
    assert generator._get_post_url({}) == ""


def test_get_post_score():
    """测试获取帖子评分"""
    generator = ReportGenerator("/tmp")

    post = {"score": 500}
    assert generator._get_post_score(post) == 500

    # 测试默认值
    assert generator._get_post_score({}) == 0


def test_get_post_comments():
    """测试获取帖子评论数"""
    generator = ReportGenerator("/tmp")

    post = {"num_comments": 50}
    assert generator._get_post_comments(post) == 50

    # 测试默认值
    assert generator._get_post_comments({}) == 0


def test_get_post_subreddit():
    """测试获取帖子子版块"""
    generator = ReportGenerator("/tmp")

    post = {"subreddit": "SomebodyMakeThis"}
    assert generator._get_post_subreddit(post) == "SomebodyMakeThis"

    # 测试默认值
    assert generator._get_post_subreddit({}) == ""


def test_report_sorted_by_priority(sample_crawl_data, sample_analysis_results):
    """测试报告按优先级排序"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = ReportGenerator(tmpdir)
        report_path = generator.generate(sample_crawl_data, sample_analysis_results, top_n=5)

        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()

        # ghi789 (priority 9) 应该在第一个
        # abc123 (priority 8) 应该在第二个
        # def456 (priority 6) 应该在第三个
        # 找到各个标题在内容中的位置
        pos_job = content.find("job applications")
        pos_parking = content.find("parking spots")
        pos_meal = content.find("meal planning")

        # 按优先级排序: job(9) > parking(8) > meal(6)
        assert pos_job < pos_parking < pos_meal


def test_report_top_n_limit(sample_crawl_data, sample_analysis_results):
    """测试 Top N 限制"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = ReportGenerator(tmpdir)
        report_path = generator.generate(sample_crawl_data, sample_analysis_results, top_n=2)

        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 检查高潜力部分只有 2 个条目
        # 通过统计 "### " 的数量（排除标题部分）
        # 高潜力部分应该在 "## 高潜力 Top 5" 之后
        top_section_start = content.find("## 高潜力 Top 5")
        full_list_start = content.find("## 完整分析列表")
        top_section = content[top_section_start:full_list_start]

        # 应该只有 2 个条目 (### 1. 和 ### 2.)
        assert top_section.count("### ") == 2


def test_format_time_range():
    """测试时间范围格式化"""
    generator = ReportGenerator("/tmp")

    assert generator._format_time_range("week") == "最近一周"
    assert generator._format_time_range("month") == "最近一月"
    assert generator._format_time_range("year") == "最近一年"
    assert generator._format_time_range("all") == "所有时间"
    assert generator._format_time_range("unknown") == "unknown"


def test_empty_data():
    """测试空数据处理"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = ReportGenerator(tmpdir)
        empty_crawl_data = {
            "crawl_metadata": {
                "timestamp": "2024-04-16T12:00:00+00:00",
                "subreddits": [],
                "time_range": "week",
                "total_posts": 0,
                "total_comments": 0
            },
            "posts": []
        }
        empty_analysis = {}

        report_path = generator.generate(empty_crawl_data, empty_analysis)
        assert report_path.exists()

        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "*暂无分析结果*" in content


def test_merge_posts_and_analysis():
    """测试帖子和分析结果合并"""
    generator = ReportGenerator("/tmp")

    posts = [
        {"id": "abc", "title": "Post A"},
        {"id": "def", "title": "Post B"}
    ]
    analysis = {
        "abc": {"priority_rating": 8},
        "def": {"priority_rating": 6}
    }

    merged = generator._merge_posts_and_analysis(posts, analysis)

    assert len(merged) == 2
    assert merged[0]["post"]["id"] == "abc"
    assert merged[0]["analysis"]["priority_rating"] == 8
    assert merged[1]["post"]["id"] == "def"
    assert merged[1]["analysis"]["priority_rating"] == 6


def test_missing_analysis(sample_crawl_data):
    """测试缺失分析结果的情况"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = ReportGenerator(tmpdir)

        # 只有一个帖子有分析结果
        partial_analysis = {
            "abc123": {"priority_rating": 8, "summary": "Test"}
        }

        report_path = generator.generate(sample_crawl_data, partial_analysis)
        assert report_path.exists()

        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 应该仍然包含所有帖子
        assert "parking spots" in content
        assert "meal planning" in content
        assert "job applications" in content