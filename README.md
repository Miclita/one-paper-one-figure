# PDF to Image Generator

一个将 PDF 文件上传到大语言模型（如 Kimi、Gemini 等）进行处理，并使用 Nano-Banana 生成图像的工具，使用 POE API 进行处理。

## 功能特点

- 简单易用的现代化图形界面（采用 PySide6 框架，支持 macOS 明亮/暗黑主题自动适配）
- 支持 PDF 文件上传和处理
- 可配置的大语言模型 API（支持 Kimi、Gemini 等多种模型）
- 自动提取大语言模型返回结果中的代码块
- 使用 Nano-Banana 生成图像并保存
- 实时进度反馈和详细日志显示
- 内置专业的学术海报生成提示词，支持自定义提示词
- 响应式布局，支持不同屏幕尺寸

## 安装说明

1. 克隆或下载此仓库
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
   
   如果出现 "No module named 'PyPDF2'" 错误，请尝试以下命令之一：
   ```bash
   # 方法1：直接安装PyPDF2
   pip install PyPDF2
   
   # 方法2：如果使用conda
   conda install -c conda-forge pypdf2
   
   # 方法3：安装特定版本
   pip install PyPDF2==3.0.1
   ```
   
3. 设置系统环境变量 `POE_API_KEY`：
   ```bash
   export POE_API_KEY="your_actual_api_key_here"
   ```

## 使用方法

### 方法一：命令行运行
```bash
python main.py
```

### 方法二：创建 Mac 应用程序包
运行以下命令创建 .app 包：
```bash
python setup.py py2app
```

创建后，您可以在 `dist` 目录中找到 `PDF2Image.app`，可以双击运行。

## 配置选项

可以通过系统环境变量配置以下参数：

- `POE_API_KEY`: 您的 POE API 密钥
- `BASE_URL`: API 基础 URL (默认: https://api.poe.com/v1)
- `MODEL_NAME`: 用于 PDF 处理的大语言模型名称 (默认: kimi-k2-thinking)
- `NANO_BANANA_MODEL`: 用于图像生成的 Nano-Banana 模型名称 (默认: nano-banana-pro)

## 工作原理

1. 用户选择 PDF 文件并在 UI 中输入自定义提示词（可选）
2. 应用读取 PDF 内容并发送到指定的大语言模型
3. 解析大语言模型返回结果中的最后一个代码块
4. 将代码块作为提示词发送给 Nano-Banana 进行图像生成
5. 保存生成的图像到输出目录，保持原始图像尺寸

## 内置专业提示词

应用程序内置了多个专业的学术海报生成提示词，专为生成高质量的科研论文图形摘要而设计。包括：

1. **Nature风** - 仿 Nature、Science 期刊风格的专业学术海报
2. **2D扁平** - 现代化扁平设计风格的图形摘要

这些提示词指导大语言模型：
1. 提取论文的关键信息（标题、作者、机构、发表 venue 等）
2. 分析论文的背景问题、解决方案和实验结果
3. 生成符合顶级期刊风格的科学海报提示词

该提示词可以帮助您将学术论文转换为专业的图形摘要，适用于学术报告、会议展示等场景。

## 界面说明

应用界面采用了现代化的 PySide6 界面框架，包括以下几个主要标签页：

1. **API 设置标签页** - 配置 API 密钥、基础 URL 和模型名称
2. **文件选择标签页** - 浏览并选择要处理的 PDF 文件
3. **提示词设置标签页** - 显示默认提示词并允许输入自定义提示词
4. **处理结果标签页** - 显示详细的处理进度和结果

应用提供了清晰的进度反馈，包括：
- 步骤编号和总步骤数（如"步骤 1/6"）
- 每个步骤的状态指示（✓ 表示成功，✗ 表示错误，⚠ 表示警告）
- 详细的日志信息帮助了解处理过程

应用默认显示文件选择标签页，并在执行操作后自动跳转到处理结果页，同时允许在程序运行过程中切换标签页。

## 依赖项

- Python 3.6+
- PySide6
- openai Python SDK
- PyPDF2
- Pillow
- python-dotenv

## 故障排除

### No module named 'PyPDF2'
如果遇到此错误，请确保已正确安装依赖项：
```bash
pip install -r requirements.txt
```

如果仍然存在问题，请尝试：
```bash
pip install PyPDF2
```

### 关于 GUI 框架的说明
项目现已使用 PySide6 重构 GUI 界面，相比之前的 ttkbootstrap/Tkinter 提供了更好的交互流畅性和现代化外观，同时支持 macOS 明亮/暗黑主题的自动适配。

### API 密钥配置
您需要通过设置系统环境变量来配置 API 密钥：
```bash
export POE_API_KEY="your_actual_api_key_here"
```

注意：不再支持通过 `.env` 文件配置 API 密钥。

## 许可证

MIT License