"""
模板渲染模块
负责使用 Jinja2 模板引擎渲染各种页面
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from .config import Config
from .theme import Theme
from .markdown_processor import Post


class RendererError(Exception):
    """渲染器错误"""
    pass


class Renderer:
    """模板渲染器"""
    
    def __init__(self, theme: Theme, config: Config):
        """
        初始化渲染器
        
        Args:
            theme: 主题管理器实例
            config: 配置管理器实例
        """
        self.theme = theme
        self.config = config
        
        # 初始化 Jinja2 环境
        templates_dir = theme.get_templates_dir()
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=True,  # 自动转义 HTML，防止 XSS
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # 注册自定义过滤器
        self._register_filters()
        
        # 注册全局变量
        self._register_globals()
    
    def _register_filters(self) -> None:
        """注册自定义 Jinja2 过滤器"""
        
        def format_date(date: datetime, format_str: Optional[str] = None) -> str:
            """格式化日期"""
            if format_str is None:
                format_str = self.config.get('theme_config.date_format', '%Y-%m-%d')
            return date.strftime(format_str)
        
        def truncate_html(html: str, length: int = 200) -> str:
            """截断 HTML 内容（简单实现）"""
            # 移除 HTML 标签
            import re
            text = re.sub(r'<[^>]+>', '', html)
            if len(text) <= length:
                return text
            return text[:length].rsplit(' ', 1)[0] + '...'
        
        self.env.filters['format_date'] = format_date
        self.env.filters['truncate_html'] = truncate_html
    
    def _register_globals(self) -> None:
        """注册全局变量"""
        # 站点配置
        self.env.globals['site'] = self.config.get_site_config()
        
        # 完整配置（供高级使用）
        self.env.globals['config'] = self.config.data
        
        # 主题信息
        self.env.globals['theme'] = {
            'name': self.theme.name,
            'version': self.theme.version
        }
        
        # 当前年份（用于版权信息等）
        self.env.globals['current_year'] = datetime.now().year
        
        # URL 生成函数
        def url_for_static(path: str) -> str:
            """生成静态资源 URL"""
            # 确保路径以 static/ 开头
            if not path.startswith('static/'):
                path = f'static/{path}'
            # 返回绝对路径（从根目录开始）
            return f'/{path}'
        
        self.env.globals['url_for_static'] = url_for_static
    
    def render_index(self, posts: List[Post], page: int = 1, 
                    posts_per_page: Optional[int] = None) -> str:
        """
        渲染首页
        
        Args:
            posts: 文章列表（已排序）
            page: 当前页码（从 1 开始）
            posts_per_page: 每页文章数，None 表示不分页
            
        Returns:
            渲染后的 HTML 字符串
            
        Raises:
            RendererError: 渲染失败
        """
        try:
            template = self.env.get_template('index.html')
        except TemplateNotFound:
            raise RendererError("找不到首页模板: index.html")
        
        # 处理分页
        pagination = None
        if posts_per_page is not None and posts_per_page > 0:
            total_posts = len(posts)
            total_pages = (total_posts + posts_per_page - 1) // posts_per_page
            
            start_idx = (page - 1) * posts_per_page
            end_idx = start_idx + posts_per_page
            posts = posts[start_idx:end_idx]
            
            pagination = {
                'page': page,
                'total_pages': total_pages,
                'total_posts': total_posts,
                'has_prev': page > 1,
                'has_next': page < total_pages,
                'prev_page': page - 1 if page > 1 else None,
                'next_page': page + 1 if page < total_pages else None
            }
        
        try:
            html = template.render(
                posts=posts,
                pagination=pagination
            )
            return html
        except Exception as e:
            raise RendererError(f"渲染首页失败: {e}")
    
    def render_post(self, post: Post) -> str:
        """
        渲染文章详情页
        
        Args:
            post: 文章对象
            
        Returns:
            渲染后的 HTML 字符串
            
        Raises:
            RendererError: 渲染失败
        """
        try:
            template = self.env.get_template('post.html')
        except TemplateNotFound:
            raise RendererError("找不到文章模板: post.html")
        
        try:
            html = template.render(post=post)
            return html
        except Exception as e:
            raise RendererError(f"渲染文章页失败: {e}")

    def render_archive(self, posts: List[Post]) -> str:
        """
        渲染归档页
        
        归档页按年份和月份组织文章列表
        
        Args:
            posts: 文章列表（已排序）
            
        Returns:
            渲染后的 HTML 字符串
            
        Raises:
            RendererError: 渲染失败
        """
        try:
            template = self.env.get_template('archive.html')
        except TemplateNotFound:
            # 如果没有专门的归档模板，使用首页模板
            try:
                template = self.env.get_template('index.html')
            except TemplateNotFound:
                raise RendererError("找不到归档模板: archive.html 或 index.html")
        
        # 按年份和月份组织文章
        archive_data = self._organize_posts_by_date(posts)
        
        try:
            html = template.render(
                posts=posts,
                archive=archive_data,
                is_archive=True
            )
            return html
        except Exception as e:
            raise RendererError(f"渲染归档页失败: {e}")
    
    def render_tag_page(self, tag: str, posts: List[Post]) -> str:
        """
        渲染标签页
        
        显示特定标签下的所有文章
        
        Args:
            tag: 标签名称
            posts: 该标签下的文章列表
            
        Returns:
            渲染后的 HTML 字符串
            
        Raises:
            RendererError: 渲染失败
        """
        try:
            template = self.env.get_template('tag.html')
        except TemplateNotFound:
            # 如果没有专门的标签模板，使用首页模板
            try:
                template = self.env.get_template('index.html')
            except TemplateNotFound:
                raise RendererError("找不到标签模板: tag.html 或 index.html")
        
        try:
            html = template.render(
                tag=tag,
                posts=posts,
                is_tag_page=True
            )
            return html
        except Exception as e:
            raise RendererError(f"渲染标签页失败: {e}")
    
    def render_tags_index(self, tags_data: Dict[str, List[Post]]) -> str:
        """
        渲染标签索引页
        
        显示所有标签及其文章数量
        
        Args:
            tags_data: 标签到文章列表的映射
            
        Returns:
            渲染后的 HTML 字符串
            
        Raises:
            RendererError: 渲染失败
        """
        try:
            template = self.env.get_template('tags.html')
        except TemplateNotFound:
            # 如果没有专门的标签索引模板，使用首页模板
            try:
                template = self.env.get_template('index.html')
            except TemplateNotFound:
                raise RendererError("找不到标签索引模板: tags.html 或 index.html")
        
        # 准备标签统计数据
        tags_stats = [
            {
                'name': tag,
                'count': len(posts),
                'posts': posts
            }
            for tag, posts in sorted(tags_data.items())
        ]
        
        try:
            html = template.render(
                tags=tags_stats,
                is_tags_index=True
            )
            return html
        except Exception as e:
            raise RendererError(f"渲染标签索引页失败: {e}")
    
    def _organize_posts_by_date(self, posts: List[Post]) -> Dict[int, Dict[int, List[Post]]]:
        """
        按年份和月份组织文章
        
        Args:
            posts: 文章列表
            
        Returns:
            嵌套字典: {year: {month: [posts]}}
        """
        archive: Dict[int, Dict[int, List[Post]]] = {}
        
        for post in posts:
            year = post.date.year
            month = post.date.month
            
            if year not in archive:
                archive[year] = {}
            
            if month not in archive[year]:
                archive[year][month] = []
            
            archive[year][month].append(post)
        
        return archive
    
    def get_all_tags(self, posts: List[Post]) -> Dict[str, List[Post]]:
        """
        从文章列表中提取所有标签
        
        Args:
            posts: 文章列表
            
        Returns:
            标签到文章列表的映射
        """
        tags_map: Dict[str, List[Post]] = {}
        
        for post in posts:
            for tag in post.tags:
                if tag not in tags_map:
                    tags_map[tag] = []
                tags_map[tag].append(post)
        
        return tags_map
