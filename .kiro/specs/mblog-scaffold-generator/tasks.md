# 实现计划

- [x] 1. 设置项目结构和核心接口
  - 创建 mblog 包的目录结构
  - 定义异常类和基础接口
  - 创建 `__init__.py` 和 `__main__.py`
  - _需求: 7.1, 7.2_

- [x] 2. 实现生成运行时模块
  - [x] 2.1 实现配置管理模块
    - 编写 `templates/runtime/config.py`
    - 实现 Config 类，支持加载和验证 JSON 配置
    - 编写配置加载和获取方法
    - _需求: 5.1, 5.2, 5.3, 5.4_

  - [x] 2.2 实现 Markdown 处理模块
    - 编写 `templates/runtime/markdown_processor.py`
    - 实现 Post 数据模型
    - 实现 frontmatter 解析功能
    - 实现 Markdown 到 HTML 转换
    - 实现 slug 生成逻辑
    - _需求: 2.1, 2.2, 2.3_

  - [x] 2.3 实现主题管理模块
    - 编写 `templates/runtime/theme.py`
    - 实现 Theme 类，支持加载主题
    - 实现主题结构验证
    - 实现模板和静态资源路径获取
    - _需求: 3.1, 3.2, 3.3, 3.5_

  - [x] 2.4 实现模板渲染模块
    - 编写 `templates/runtime/renderer.py`
    - 集成 Jinja2 模板引擎
    - 实现首页渲染方法
    - 实现文章详情页渲染方法
    - 实现标签页和归档页渲染方法
    - _需求: 4.2, 4.4_

  - [x] 2.5 实现静态文件生成模块
    - 编写 `templates/runtime/generator.py`
    - 实现输出目录准备逻辑
    - 实现页面生成流程
    - 实现静态资源复制功能
    - 实现文章列表和详情页生成
    - _需求: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 3. 创建项目模板文件
  - [x] 3.1 创建 gen.py 模板
    - 编写 `templates/project/gen.py.template`
    - 实现调用 _mblog 运行时的主函数
    - 添加错误处理和友好的输出信息
    - _需求: 4.1, 4.6_

  - [x] 3.2 创建配置文件模板
    - 编写 `templates/project/config.json.template`
    - 定义默认的站点配置
    - 定义默认的构建配置
    - 定义默认的主题配置
    - _需求: 5.1, 5.2_

  - [x] 3.3 创建示例文章模板
    - 编写 `templates/project/welcome.md.template`
    - 包含完整的 frontmatter 示例
    - 包含常用 Markdown 语法示例
    - _需求: 2.1, 2.2_

  - [x] 3.4 创建 requirements.txt 模板
    - 编写 `templates/project/requirements.txt.template`
    - 列出所有必需的 Python 依赖
    - _需求: 4.1_

  - [x] 3.5 创建 GitHub Actions 工作流模板
    - 编写 `templates/project/deploy.yml.template`
    - 配置 Python 环境设置
    - 配置依赖安装步骤
    - 配置生成和部署步骤
    - _需求: 6.1, 6.2, 6.3_

- [x] 4. 创建默认主题
  - [x] 4.1 创建主题元数据
    - 编写 `templates/themes/default/theme.json`
    - 定义主题名称、版本和模板映射
    - _需求: 3.1, 3.5_

  - [x] 4.2 创建基础模板
    - 编写 `templates/themes/default/templates/base.html`
    - 实现页面基础结构和导航
    - 定义模板块（block）供其他模板继承
    - _需求: 3.2_

  - [x] 4.3 创建首页模板
    - 编写 `templates/themes/default/templates/index.html`
    - 实现文章列表展示
    - 实现分页功能（如果配置启用）
    - _需求: 3.2, 4.4_

  - [x] 4.4 创建文章详情页模板
    - 编写 `templates/themes/default/templates/post.html`
    - 实现文章内容展示
    - 实现元数据（日期、标签、作者）展示
    - _需求: 3.2, 4.4_

  - [x] 4.5 创建默认样式
    - 编写 `templates/themes/default/static/css/style.css`
    - 实现响应式布局
    - 实现代码高亮样式
    - 实现基础排版样式
    - _需求: 3.3_

  - [x] 4.6 创建默认脚本（可选）
    - 编写 `templates/themes/default/static/js/main.js`
    - 实现基础交互功能
    - _需求: 3.3_

- [x] 5. 实现项目初始化模块
  - [x] 5.1 实现目录创建逻辑
    - 编写 `mblog/initializer.py` 的目录结构创建方法
    - 实现目标目录存在性检查
    - 创建所有必需的目录
    - _需求: 1.1, 1.2, 1.4_

  - [x] 5.2 实现运行时复制逻辑
    - 实现从 templates/runtime 复制到 _mblog/ 的功能
    - 确保所有运行时文件正确复制
    - _需求: 1.2_

  - [x] 5.3 实现模板文件生成逻辑
    - 实现从模板生成 gen.py
    - 实现从模板生成 config.json
    - 实现从模板生成 requirements.txt
    - 实现从模板生成示例文章
    - 实现从模板生成工作流文件
    - _需求: 1.2, 1.3_

  - [x] 5.4 实现主题复制逻辑
    - 实现从 templates/themes/default 复制到 theme/ 的功能
    - 确保主题结构完整
    - _需求: 1.2, 3.1_

  - [x] 5.5 实现初始化成功反馈
    - 输出成功消息
    - 提示用户下一步操作
    - _需求: 1.3_

- [x] 6. 实现 CLI 模块
  - [x] 6.1 实现命令行参数解析
    - 编写 `mblog/cli.py` 的参数解析逻辑
    - 使用 argparse 定义命令和选项
    - 实现 new 命令的参数定义
    - _需求: 7.1, 7.2_

  - [x] 6.2 实现 new 命令处理器
    - 实现 handle_new 方法
    - 调用 ProjectInitializer 创建项目
    - 处理错误情况并返回适当的退出码
    - _需求: 1.1, 1.3, 1.4, 7.5, 7.6_

  - [x] 6.3 实现帮助和版本信息
    - 实现 show_help 方法
    - 实现 show_version 方法
    - 实现无参数时的默认行为
    - _需求: 7.1, 7.2, 7.3_

  - [x] 6.4 实现错误处理
    - 捕获所有异常并显示友好的错误消息
    - 实现无效命令的错误提示
    - 确保正确的退出码
    - _需求: 7.4, 7.5, 7.6_

  - [x] 6.5 实现主入口点
    - 编写 `mblog/__main__.py`
    - 实现 main 函数调用 CLI
    - _需求: 7.1_

- [x] 7. 创建包配置和安装脚本
  - [x] 7.1 创建 setup.py
    - 定义包元数据
    - 配置命令行入口点
    - 定义依赖关系
    - 配置包数据（包含 templates 目录）
    - _需求: 7.1_

  - [x] 7.2 创建 pyproject.toml
    - 定义构建系统要求
    - 配置项目元数据
    - _需求: 7.1_

  - [x] 7.3 创建 mblog 的 requirements.txt
    - 列出 mblog 工具本身的依赖（如果有）
    - _需求: 7.1_

- [ ] 8. 编写单元测试
  - [x] 8.1 测试配置管理模块
    - 编写 `tests/test_config.py`
    - 测试配置加载功能
    - 测试配置验证功能
    - 测试配置获取方法
    - _需求: 5.3, 5.4_

  - [x] 8.2 测试 Markdown 处理模块
    - 编写 `tests/test_markdown_processor.py`
    - 测试 frontmatter 解析
    - 测试 Markdown 转 HTML
    - 测试 slug 生成
    - 准备测试用的 Markdown 文件
    - _需求: 2.1, 2.2, 2.3_

  - [x] 8.3 测试主题管理模块
    - 编写 `tests/test_theme.py`
    - 测试主题加载
    - 测试主题结构验证
    - 准备测试用的主题文件
    - _需求: 3.1, 3.2, 3.5_

  - [x] 8.4 测试项目初始化模块
    - 编写 `tests/test_initializer.py`
    - 测试项目创建流程
    - 测试目录已存在的错误处理
    - 验证生成的文件结构
    - _需求: 1.1, 1.2, 1.3, 1.4_

  - [x] 8.5 测试 CLI 模块
    - 编写 `tests/test_cli.py`
    - 测试命令解析
    - 测试 new 命令
    - 测试帮助和版本信息
    - 测试错误处理
    - _需求: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

- [x] 9. 编写集成测试
  - [x] 9.1 测试完整的项目创建流程
    - 编写 `tests/test_integration.py`
    - 测试从 `mblog new` 到项目创建完成
    - 验证所有文件和目录正确生成
    - _需求: 1.1, 1.2, 1.3_

  - [x] 9.2 测试生成的项目可以独立运行
    - 在临时目录创建测试项目
    - 运行 gen.py 生成静态文件
    - 验证输出目录和文件
    - _需求: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [x] 9.3 测试主题切换和自定义
    - 创建自定义主题
    - 修改配置切换主题
    - 验证生成结果使用了新主题
    - _需求: 3.4_

- [x] 10. 创建文档和示例
  - [x] 10.1 编写 README.md
    - 介绍 mblog 工具
    - 提供安装说明
    - 提供快速开始指南
    - 提供命令参考
    - _需求: 7.1, 7.2_

  - [x] 10.2 编写主题开发文档
    - 说明主题结构规范
    - 说明模板变量
    - 提供主题开发示例
    - _需求: 3.2, 3.5_

  - [x] 10.3 编写配置文档
    - 说明所有配置项
    - 提供配置示例
    - _需求: 5.2, 5.5_

  - [x] 10.4 编写部署文档
    - 说明如何部署到 GitHub Pages
    - 说明如何部署到其他平台
    - _需求: 6.1, 6.2, 6.3_
