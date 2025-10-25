"""
mblog 异常类定义

定义了 mblog 工具中使用的所有自定义异常类型。
"""


class MblogError(Exception):
    """mblog 基础异常类
    
    所有 mblog 相关的异常都应该继承此类。
    """
    pass


class ProjectExistsError(MblogError):
    """项目已存在异常
    
    当尝试创建的项目目录已经存在时抛出。
    """
    pass


class ConfigError(MblogError):
    """配置文件错误异常
    
    当配置文件格式错误、缺少必需字段或验证失败时抛出。
    """
    pass


class ThemeError(MblogError):
    """主题错误异常
    
    当主题加载失败、结构不符合规范或缺少必需文件时抛出。
    """
    pass


class MarkdownError(MblogError):
    """Markdown 处理错误异常
    
    当 Markdown 文件解析失败、frontmatter 格式错误或转换失败时抛出。
    """
    pass


class GenerationError(MblogError):
    """生成错误异常
    
    当静态文件生成过程中发生错误时抛出。
    """
    pass
