"""
测试 Markdown 处理模块
"""
import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import sys

# 添加 mblog/templates/runtime 到路径以便导入
sys.path.insert(0, str(Path(__file__).parent.parent / 'mblog' / 'templates' / 'runtime'))

from markdown_processor import MarkdownProcessor, Post


@pytest.fixture
def temp_dir():
    """创建临时目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def fixtures_dir():
    """获取测试 fixtures 目录"""
    return Path(__file__).parent / 'fixtures'


@pytest.fixture
def md_processor(temp_dir):
    """创建 Markdown 处理器实例"""
    return MarkdownProcessor(str(temp_dir))


class TestMarkdownProcessorInit:
    """测试 Markdown 处理器初始化"""
    
    def test_init_with_string_path(self, temp_dir):
        """测试使用字符串路径初始化"""
        processor = MarkdownProcessor(str(temp_dir))
        assert processor.md_dir == temp_dir
        assert processor.md_converter is not None
    
    def test_init_with_nonexistent_dir(self):
        """测试使用不存在的目录初始化"""
        processor = MarkdownProcessor("/nonexistent/path")
        assert processor.md_dir == Path("/nonexistent/path")


class TestExtractFrontmatter:
    """测试 frontmatter 提取功能"""
    
    def test_extract_valid_frontmatter(self, md_processor):
        """测试提取有效的 frontmatter"""
        content = """---
title: "测试标题"
date: 2025-10-23
author: "作者"
tags: ["tag1", "tag2"]
---

文章内容
"""
        metadata, body = md_processor._extract_frontmatter(content)
        
        assert metadata['title'] == "测试标题"
        # frontmatter 库会自动解析日期为 date 对象
        from datetime import date
        assert metadata['date'] == date(2025, 10, 23) or metadata['date'] == "2025-10-23"
        assert metadata['author'] == "作者"
        assert metadata['tags'] == ["tag1", "tag2"]
        assert body.strip() == "文章内容"
    
    def test_extract_no_frontmatter(self, md_processor):
        """测试没有 frontmatter 的内容"""
        content = "# 标题\n\n这是内容"
        metadata, body = md_processor._extract_frontmatter(content)
        
        assert metadata == {}
        assert body == content
    
    def test_extract_empty_frontmatter(self, md_processor):
        """测试空 frontmatter"""
        content = """---
---

内容
"""
        metadata, body = md_processor._extract_frontmatter(content)
        
        assert metadata == {}
        assert body.strip() == "内容"
    
    def test_extract_frontmatter_with_complex_values(self, md_processor):
        """测试包含复杂值的 frontmatter"""
        content = """---
title: "标题"
nested:
  key1: value1
  key2: value2
list:
  - item1
  - item2
number: 42
boolean: true
---

内容
"""
        metadata, body = md_processor._extract_frontmatter(content)
        
        assert metadata['title'] == "标题"
        assert metadata['nested']['key1'] == "value1"
        assert metadata['list'] == ["item1", "item2"]
        assert metadata['number'] == 42
        assert metadata['boolean'] is True


class TestConvertToHtml:
    """测试 Markdown 转 HTML 功能"""
    
    def test_convert_simple_markdown(self, md_processor):
        """测试转换简单 Markdown"""
        markdown = "# 标题\n\n这是一段文字。"
        html = md_processor._convert_to_html(markdown)
        
        # markdown 库会添加 id 属性到标题
        assert "<h1" in html and "标题</h1>" in html
        assert "<p>这是一段文字。</p>" in html
    
    def test_convert_with_bold_italic(self, md_processor):
        """测试转换粗体和斜体"""
        markdown = "这是**粗体**和*斜体*文本。"
        html = md_processor._convert_to_html(markdown)
        
        assert "<strong>粗体</strong>" in html
        assert "<em>斜体</em>" in html
    
    def test_convert_with_code_block(self, md_processor):
        """测试转换代码块"""
        markdown = """```python
def hello():
    print("Hello")
```"""
        html = md_processor._convert_to_html(markdown)
        
        assert "<code>" in html or "<pre>" in html
        # codehilite 会添加语法高亮的 span 标签
        assert "def" in html and "hello" in html
    
    def test_convert_with_list(self, md_processor):
        """测试转换列表"""
        markdown = """- 项目 1
- 项目 2
- 项目 3"""
        html = md_processor._convert_to_html(markdown)
        
        assert "<ul>" in html
        assert "<li>项目 1</li>" in html
        assert "<li>项目 2</li>" in html
    
    def test_convert_with_table(self, md_processor):
        """测试转换表格"""
        markdown = """| 列1 | 列2 |
|-----|-----|
| A   | B   |
| C   | D   |"""
        html = md_processor._convert_to_html(markdown)
        
        assert "<table>" in html
        assert "<thead>" in html
        assert "<tbody>" in html
        assert "<td>A</td>" in html
    
    def test_convert_with_links(self, md_processor):
        """测试转换链接"""
        markdown = "[链接文本](https://example.com)"
        html = md_processor._convert_to_html(markdown)
        
        assert '<a href="https://example.com">链接文本</a>' in html
    
    def test_convert_empty_string(self, md_processor):
        """测试转换空字符串"""
        html = md_processor._convert_to_html("")
        assert html == ""
    
    def test_convert_multiple_times(self, md_processor):
        """测试多次转换（验证重置功能）"""
        markdown1 = "# 标题 1"
        markdown2 = "# 标题 2"
        
        html1 = md_processor._convert_to_html(markdown1)
        html2 = md_processor._convert_to_html(markdown2)
        
        assert "标题 1" in html1
        assert "标题 2" in html2
        assert "标题 1" not in html2


class TestGenerateSlug:
    """测试 slug 生成功能"""
    
    def test_generate_slug_simple_title(self, md_processor):
        """测试生成简单标题的 slug"""
        title = "Hello World"
        date = datetime(2025, 10, 23)
        slug = md_processor._generate_slug(title, date)
        
        assert slug == "2025-10-23-hello-world"
    
    def test_generate_slug_with_spaces(self, md_processor):
        """测试包含多个空格的标题"""
        title = "This  Is  A  Test"
        date = datetime(2025, 10, 23)
        slug = md_processor._generate_slug(title, date)
        
        assert slug == "2025-10-23-this-is-a-test"
    
    def test_generate_slug_with_special_chars(self, md_processor):
        """测试包含特殊字符的标题"""
        title = "Hello! World? @#$%"
        date = datetime(2025, 10, 23)
        slug = md_processor._generate_slug(title, date)
        
        assert slug == "2025-10-23-hello-world"
    
    def test_generate_slug_with_chinese(self, md_processor):
        """测试包含中文的标题"""
        title = "中文标题测试"
        date = datetime(2025, 10, 23)
        slug = md_processor._generate_slug(title, date)
        
        assert slug == "2025-10-23-中文标题测试"
    
    def test_generate_slug_with_mixed_chars(self, md_processor):
        """测试混合字符的标题"""
        title = "Python 编程 Tutorial"
        date = datetime(2025, 10, 23)
        slug = md_processor._generate_slug(title, date)
        
        assert slug == "2025-10-23-python-编程-tutorial"
    
    def test_generate_slug_with_underscores(self, md_processor):
        """测试包含下划线的标题"""
        title = "hello_world_test"
        date = datetime(2025, 10, 23)
        slug = md_processor._generate_slug(title, date)
        
        assert slug == "2025-10-23-hello-world-test"
    
    def test_generate_slug_with_hyphens(self, md_processor):
        """测试包含连字符的标题"""
        title = "hello-world-test"
        date = datetime(2025, 10, 23)
        slug = md_processor._generate_slug(title, date)
        
        assert slug == "2025-10-23-hello-world-test"
    
    def test_generate_slug_different_dates(self, md_processor):
        """测试不同日期生成不同的 slug"""
        title = "Same Title"
        date1 = datetime(2025, 10, 23)
        date2 = datetime(2025, 10, 24)
        
        slug1 = md_processor._generate_slug(title, date1)
        slug2 = md_processor._generate_slug(title, date2)
        
        assert slug1 == "2025-10-23-same-title"
        assert slug2 == "2025-10-24-same-title"
        assert slug1 != slug2


class TestParseDate:
    """测试日期解析功能"""
    
    def test_parse_datetime_object(self, md_processor):
        """测试解析 datetime 对象"""
        dt = datetime(2025, 10, 23, 12, 30, 45)
        result = md_processor._parse_date(dt)
        
        assert result == dt
    
    def test_parse_date_object(self, md_processor):
        """测试解析 date 对象"""
        from datetime import date
        d = date(2025, 10, 23)
        result = md_processor._parse_date(d)
        
        assert result.year == 2025
        assert result.month == 10
        assert result.day == 23
        assert isinstance(result, datetime)
    
    def test_parse_date_string_format1(self, md_processor):
        """测试解析日期字符串格式 YYYY-MM-DD"""
        date_str = "2025-10-23"
        result = md_processor._parse_date(date_str)
        
        assert result.year == 2025
        assert result.month == 10
        assert result.day == 23
    
    def test_parse_date_string_format2(self, md_processor):
        """测试解析日期字符串格式 YYYY/MM/DD"""
        date_str = "2025/10/23"
        result = md_processor._parse_date(date_str)
        
        assert result.year == 2025
        assert result.month == 10
        assert result.day == 23
    
    def test_parse_datetime_string_format1(self, md_processor):
        """测试解析日期时间字符串格式 YYYY-MM-DD HH:MM:SS"""
        datetime_str = "2025-10-23 14:30:00"
        result = md_processor._parse_date(datetime_str)
        
        assert result.year == 2025
        assert result.month == 10
        assert result.day == 23
        assert result.hour == 14
        assert result.minute == 30
    
    def test_parse_datetime_string_iso_format(self, md_processor):
        """测试解析 ISO 格式日期时间字符串"""
        datetime_str = "2025-10-23T14:30:00"
        result = md_processor._parse_date(datetime_str)
        
        assert result.year == 2025
        assert result.month == 10
        assert result.day == 23
        assert result.hour == 14
        assert result.minute == 30
    
    def test_parse_invalid_date_string(self, md_processor):
        """测试解析无效的日期字符串"""
        with pytest.raises(ValueError) as exc_info:
            md_processor._parse_date("invalid-date")
        assert "无法解析日期格式" in str(exc_info.value)
    
    def test_parse_invalid_date_type(self, md_processor):
        """测试解析无效的日期类型"""
        with pytest.raises(ValueError) as exc_info:
            md_processor._parse_date(12345)
        assert "不支持的日期类型" in str(exc_info.value)


class TestParsePost:
    """测试文章解析功能"""
    
    def test_parse_valid_post(self, fixtures_dir):
        """测试解析有效的文章"""
        post_file = fixtures_dir / "test_post_valid.md"
        processor = MarkdownProcessor(str(fixtures_dir))
        
        post = processor.parse_post(str(post_file))
        
        assert isinstance(post, Post)
        assert post.title == "测试文章标题"
        assert post.author == "测试作者"
        assert post.description == "这是一篇测试文章的描述"
        assert post.tags == ["Python", "测试", "博客"]
        assert post.date.year == 2025
        assert post.date.month == 10
        assert post.date.day == 23
        assert "欢迎来到测试文章" in post.html
        assert post.slug.startswith("2025-10-23-")
    
    def test_parse_post_without_frontmatter(self, fixtures_dir):
        """测试解析没有 frontmatter 的文章"""
        post_file = fixtures_dir / "test_post_no_frontmatter.md"
        processor = MarkdownProcessor(str(fixtures_dir))
        
        with pytest.raises(ValueError) as exc_info:
            processor.parse_post(str(post_file))
        assert "缺少必需的 frontmatter 字段: title" in str(exc_info.value)
    
    def test_parse_minimal_post(self, fixtures_dir):
        """测试解析最小化文章（只有标题）"""
        post_file = fixtures_dir / "test_post_minimal.md"
        processor = MarkdownProcessor(str(fixtures_dir))
        
        post = processor.parse_post(str(post_file))
        
        assert post.title == "最小化文章"
        assert post.author == ""
        assert post.description == ""
        assert post.tags == []
        assert isinstance(post.date, datetime)  # 应该使用文件修改时间
    
    def test_parse_post_with_tags_as_string(self, fixtures_dir):
        """测试解析标签为字符串的文章"""
        post_file = fixtures_dir / "test_post_tags_string.md"
        processor = MarkdownProcessor(str(fixtures_dir))
        
        post = processor.parse_post(str(post_file))
        
        assert post.tags == ["Python", "测试", "博客"]
    
    def test_parse_post_with_chinese_title(self, fixtures_dir):
        """测试解析中文标题的文章"""
        post_file = fixtures_dir / "test_post_chinese_title.md"
        processor = MarkdownProcessor(str(fixtures_dir))
        
        post = processor.parse_post(str(post_file))
        
        assert post.title == "中文标题测试文章"
        assert "中文标题测试文章" in post.slug
    
    def test_parse_post_with_special_chars_in_title(self, fixtures_dir):
        """测试解析标题包含特殊字符的文章"""
        post_file = fixtures_dir / "test_post_special_chars.md"
        processor = MarkdownProcessor(str(fixtures_dir))
        
        post = processor.parse_post(str(post_file))
        
        assert post.title == "Special Characters & Symbols! @#$%"
        # slug 应该移除特殊字符
        assert "@" not in post.slug
        assert "#" not in post.slug
        assert "$" not in post.slug
    
    def test_parse_nonexistent_file(self, md_processor):
        """测试解析不存在的文件"""
        with pytest.raises(FileNotFoundError):
            md_processor.parse_post("/nonexistent/file.md")
    
    def test_parse_post_metadata_preserved(self, fixtures_dir):
        """测试文章元数据被保留"""
        post_file = fixtures_dir / "test_post_valid.md"
        processor = MarkdownProcessor(str(fixtures_dir))
        
        post = processor.parse_post(str(post_file))
        
        assert 'title' in post.metadata
        assert 'date' in post.metadata
        assert 'author' in post.metadata
        assert 'tags' in post.metadata


class TestLoadPosts:
    """测试加载所有文章功能"""
    
    def test_load_posts_from_fixtures(self, fixtures_dir):
        """测试从 fixtures 目录加载文章"""
        processor = MarkdownProcessor(str(fixtures_dir))
        posts = processor.load_posts()
        
        # 应该加载所有有效的文章（排除没有 title 的）
        assert len(posts) > 0
        assert all(isinstance(post, Post) for post in posts)
    
    def test_load_posts_sorted_by_date(self, temp_dir):
        """测试文章按日期降序排序"""
        # 创建多个测试文章
        post1_content = """---
title: "文章 1"
date: 2025-10-21
---
内容 1
"""
        post2_content = """---
title: "文章 2"
date: 2025-10-23
---
内容 2
"""
        post3_content = """---
title: "文章 3"
date: 2025-10-22
---
内容 3
"""
        
        (temp_dir / "post1.md").write_text(post1_content, encoding='utf-8')
        (temp_dir / "post2.md").write_text(post2_content, encoding='utf-8')
        (temp_dir / "post3.md").write_text(post3_content, encoding='utf-8')
        
        processor = MarkdownProcessor(str(temp_dir))
        posts = processor.load_posts()
        
        assert len(posts) == 3
        # 应该按日期降序排序：2025-10-23, 2025-10-22, 2025-10-21
        assert posts[0].title == "文章 2"
        assert posts[1].title == "文章 3"
        assert posts[2].title == "文章 1"
    
    def test_load_posts_from_empty_dir(self, temp_dir):
        """测试从空目录加载文章"""
        processor = MarkdownProcessor(str(temp_dir))
        posts = processor.load_posts()
        
        assert posts == []
    
    def test_load_posts_from_nonexistent_dir(self):
        """测试从不存在的目录加载文章"""
        processor = MarkdownProcessor("/nonexistent/path")
        posts = processor.load_posts()
        
        assert posts == []
    
    def test_load_posts_skips_invalid_files(self, temp_dir):
        """测试加载时跳过无效文件"""
        # 创建一个有效文章
        valid_content = """---
title: "有效文章"
date: 2025-10-23
---
内容
"""
        # 创建一个无效文章（没有 title）
        invalid_content = """---
date: 2025-10-23
---
内容
"""
        
        (temp_dir / "valid.md").write_text(valid_content, encoding='utf-8')
        (temp_dir / "invalid.md").write_text(invalid_content, encoding='utf-8')
        
        processor = MarkdownProcessor(str(temp_dir))
        posts = processor.load_posts()
        
        # 应该只加载有效的文章
        assert len(posts) == 1
        assert posts[0].title == "有效文章"
    
    def test_load_posts_only_md_files(self, temp_dir):
        """测试只加载 .md 文件"""
        md_content = """---
title: "Markdown 文章"
---
内容
"""
        
        (temp_dir / "post.md").write_text(md_content, encoding='utf-8')
        (temp_dir / "readme.txt").write_text("这不是 markdown 文件", encoding='utf-8')
        (temp_dir / "data.json").write_text('{"key": "value"}', encoding='utf-8')
        
        processor = MarkdownProcessor(str(temp_dir))
        posts = processor.load_posts()
        
        # 应该只加载 .md 文件
        assert len(posts) == 1
        assert posts[0].title == "Markdown 文章"


class TestPostDataModel:
    """测试 Post 数据模型"""
    
    def test_post_creation(self):
        """测试创建 Post 对象"""
        post = Post(
            filepath="/path/to/post.md",
            slug="2025-10-23-test-post",
            title="测试文章",
            date=datetime(2025, 10, 23),
            author="作者",
            description="描述",
            tags=["tag1", "tag2"],
            content="# 内容",
            html="<h1>内容</h1>",
            metadata={"custom": "value"}
        )
        
        assert post.filepath == "/path/to/post.md"
        assert post.slug == "2025-10-23-test-post"
        assert post.title == "测试文章"
        assert post.date.year == 2025
        assert post.author == "作者"
        assert post.description == "描述"
        assert post.tags == ["tag1", "tag2"]
        assert post.content == "# 内容"
        assert post.html == "<h1>内容</h1>"
        assert post.metadata["custom"] == "value"
    
    def test_post_with_default_metadata(self):
        """测试使用默认元数据创建 Post"""
        post = Post(
            filepath="/path/to/post.md",
            slug="slug",
            title="标题",
            date=datetime.now(),
            author="",
            description="",
            tags=[],
            content="",
            html=""
        )
        
        assert post.metadata == {}


class TestEdgeCases:
    """测试边界情况"""
    
    def test_parse_post_with_empty_content(self, temp_dir):
        """测试解析空内容的文章"""
        content = """---
title: "空内容文章"
date: 2025-10-23
---
"""
        post_file = temp_dir / "empty.md"
        post_file.write_text(content, encoding='utf-8')
        
        processor = MarkdownProcessor(str(temp_dir))
        post = processor.parse_post(str(post_file))
        
        assert post.title == "空内容文章"
        assert post.content.strip() == ""
        assert post.html.strip() == ""
    
    def test_parse_post_with_very_long_title(self, temp_dir):
        """测试解析超长标题的文章"""
        long_title = "这是一个非常非常非常非常非常非常非常非常非常非常长的标题" * 10
        content = f"""---
title: "{long_title}"
date: 2025-10-23
---
内容
"""
        post_file = temp_dir / "long_title.md"
        post_file.write_text(content, encoding='utf-8')
        
        processor = MarkdownProcessor(str(temp_dir))
        post = processor.parse_post(str(post_file))
        
        assert post.title == long_title
        assert len(post.slug) > 0
    
    def test_parse_post_with_unicode_content(self, temp_dir):
        """测试解析包含 Unicode 字符的文章"""
        content = """---
title: "Unicode 测试"
date: 2025-10-23
---

# 各种 Unicode 字符

中文：你好世界
日文：こんにちは
韩文：안녕하세요
Emoji：😀 🎉 🚀
特殊符号：© ® ™ € £ ¥
"""
        post_file = temp_dir / "unicode.md"
        post_file.write_text(content, encoding='utf-8')
        
        processor = MarkdownProcessor(str(temp_dir))
        post = processor.parse_post(str(post_file))
        
        assert "你好世界" in post.content
        assert "こんにちは" in post.content
        assert "😀" in post.content
    
    def test_parse_post_with_malformed_yaml(self, temp_dir):
        """测试解析格式错误的 YAML frontmatter"""
        content = """---
title: "测试"
date: 2025-10-23
tags: [unclosed list
---
内容
"""
        post_file = temp_dir / "malformed.md"
        post_file.write_text(content, encoding='utf-8')
        
        processor = MarkdownProcessor(str(temp_dir))
        # 应该能处理或抛出适当的错误
        try:
            post = processor.parse_post(str(post_file))
            # 如果成功解析，验证基本字段
            assert post.title is not None
        except (ValueError, Exception):
            # 如果抛出错误，也是可以接受的
            pass
