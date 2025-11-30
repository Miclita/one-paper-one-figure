#!/usr/bin/env python3
"""
PDF to Image Generator Application
此应用程序允许用户上传PDF文件，通过大模型处理，并使用Nano-Banana生成图像。
"""

import sys
import os
import subprocess

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QTextEdit, QFileDialog, 
    QMessageBox, QTabWidget, QComboBox, QScrollArea, QGroupBox,
    QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QFont, QPalette

# 导入自定义模块
from pdf_handler import read_pdf_content, get_pdf_info
from llm_client import LLMClient
from code_parser import extract_last_code_block
from image_generator import generate_and_save_image
from config import API_KEY, BASE_URL, MODEL_NAME, NANO_BANANA_MODEL, PROMPT_TEMPLATES


class WorkerThread(QThread):
    """工作线程，用于在后台处理PDF"""
    log_signal = Signal(str)
    finished_signal = Signal(bool, str)  # (success, message)
    
    def __init__(self, pdf_file_path, api_key, base_url, model_name, nanobanana_model, prompt):
        super().__init__()
        self.pdf_file_path = pdf_file_path
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.nanobanana_model = nanobanana_model
        self.prompt = prompt
        
    def log_message(self, message):
        """发送日志消息到主线程"""
        self.log_signal.emit(message)
        
    def run(self):
        """在后台线程中处理PDF的实际工作"""
        try:
            # 读取PDF内容
            self.log_message("步骤 1/6: 正在读取PDF内容...")
            pdf_content = read_pdf_content(self.pdf_file_path)
            self.log_message(f"✓ PDF内容读取完成，共 {len(pdf_content)} 个字符")
            
            # 初始化LLM客户端
            self.log_message("步骤 2/6: 正在连接到大语言模型...")
            client = LLMClient(
                api_key=self.api_key,
                base_url=self.base_url
            )
            self.log_message("✓ 大语言模型连接成功")
            
            # 发送请求到大语言模型
            self.log_message("步骤 3/6: 正在发送请求到大语言模型...")
            llm_response = client.send_pdf_to_llm(pdf_content, self.prompt, self.model_name)
            self.log_message("✓ 大语言模型响应接收完成")
            
            # 显示LLM响应摘要
            response_length = len(llm_response) if llm_response else 0
            self.log_message(f"  响应长度: {response_length} 字符")
            
            # 提取代码块
            self.log_message("步骤 4/6: 正在提取代码块...")
            code_block = extract_last_code_block(llm_response)
            
            if not code_block:
                self.log_message("⚠ 未在大语言模型响应中找到代码块")
                self.finished_signal.emit(False, "未在大语言模型响应中找到代码块")
                return
                
            self.log_message("✓ 代码块提取完成")
            code_length = len(code_block) if code_block else 0
            self.log_message(f"  代码块长度: {code_length} 字符")
            
            # 使用Nano-Banana生成图像
            self.log_message("步骤 5/6: 正在使用Nano-Banana生成图像...")
            # 直接使用提取的代码块作为图像生成提示词
            image_path = generate_and_save_image(
                code_block,
                api_key=self.api_key,
                base_url=self.base_url,
                model_name=self.nanobanana_model
            )
            self.log_message("✓ 图像生成完成")
            
            # 完成
            self.log_message("步骤 6/6: 图像已成功生成并保存")
            self.log_message(f"保存路径: {image_path}")
            self.finished_signal.emit(True, "处理完成")
        except Exception as e:
            self.log_message(f"✗ 处理过程中出现错误: {str(e)}")
            self.finished_signal.emit(False, str(e))


class PDFImageGeneratorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pdf_file_path = ""
        self.prompt_templates = PROMPT_TEMPLATES
        self.selected_template = list(PROMPT_TEMPLATES.keys())[0]  # 默认选择第一个模板
        
        # API配置变量
        self.api_key = os.getenv("POE_API_KEY", API_KEY)  # 优先使用环境变量
        self.base_url = BASE_URL
        self.model_name = MODEL_NAME
        self.nanobanana_model = NANO_BANANA_MODEL
        
        self.init_ui()
        
    def init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle("PDF to Image Generator")
        self.setGeometry(100, 100, 900, 700)
        self.setMinimumSize(800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 主标题
        title_label = QLabel("PDF to Image Generator")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 创建各个标签页
        self.create_api_settings_tab()
        self.create_file_selection_tab()
        self.create_prompt_settings_tab()
        self.create_result_tab()
        
        # 创建按钮区域
        self.create_button_area(main_layout)
        
        # 默认选中文件选择标签页
        self.tab_widget.setCurrentIndex(1)
        
    def update_title_style(self):
        """根据系统主题更新标题样式"""
        palette = QApplication.palette()
        is_dark_mode = palette.color(QPalette.ColorRole.Window).lightness() < 128
        
        if is_dark_mode:
            # 暗黑模式下的样式
            title_style = "color: #ffffff; margin: 10px;"
        else:
            # 明亮模式下的样式
            title_style = "color: #2c3e50; margin: 10px;"
            
        # 应用样式到标题
        for widget in self.findChildren(QLabel):
            if widget.text() == "PDF to Image Generator" and widget.font().pointSize() == 18:
                widget.setStyleSheet(title_style)
                break
        
    def create_api_settings_tab(self):
        """创建API设置标签页"""
        api_widget = QWidget()
        layout = QVBoxLayout(api_widget)
        layout.setSpacing(10)
        
        # API Key
        api_key_group = QGroupBox("API 设置")
        api_key_layout = QVBoxLayout(api_key_group)
        
        api_key_hbox = QHBoxLayout()
        api_key_label = QLabel("API Key:")
        api_key_label.setFixedWidth(120)
        self.api_key_input = QLineEdit()
        self.api_key_input.setText(self.api_key)
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_key_hbox.addWidget(api_key_label)
        api_key_hbox.addWidget(self.api_key_input)
        api_key_layout.addLayout(api_key_hbox)
        
        # Base URL
        base_url_hbox = QHBoxLayout()
        base_url_label = QLabel("Base URL:")
        base_url_label.setFixedWidth(120)
        self.base_url_input = QLineEdit()
        self.base_url_input.setText(self.base_url)
        base_url_hbox.addWidget(base_url_label)
        base_url_hbox.addWidget(self.base_url_input)
        api_key_layout.addLayout(base_url_hbox)
        
        # Model Name
        model_hbox = QHBoxLayout()
        model_label = QLabel("Model Name:")
        model_label.setFixedWidth(120)
        self.model_input = QLineEdit()
        self.model_input.setText(self.model_name)
        model_hbox.addWidget(model_label)
        model_hbox.addWidget(self.model_input)
        api_key_layout.addLayout(model_hbox)
        
        # Nano-Banana Model
        nanobanana_hbox = QHBoxLayout()
        nanobanana_label = QLabel("Nano-Banana Model:")
        nanobanana_label.setFixedWidth(120)
        self.nanobanana_input = QLineEdit()
        self.nanobanana_input.setText(self.nanobanana_model)
        nanobanana_hbox.addWidget(nanobanana_label)
        nanobanana_hbox.addWidget(self.nanobanana_input)
        api_key_layout.addLayout(nanobanana_hbox)
        
        layout.addWidget(api_key_group)
        layout.addStretch()
        
        self.tab_widget.addTab(api_widget, "API 设置")
        
    def create_file_selection_tab(self):
        """创建文件选择标签页"""
        file_widget = QWidget()
        layout = QVBoxLayout(file_widget)
        layout.setSpacing(10)
        
        # 文件选择区域
        file_group = QGroupBox("文件选择")
        file_layout = QVBoxLayout(file_group)
        
        file_hbox = QHBoxLayout()
        file_label = QLabel("选择的文件:")
        file_label.setFixedWidth(100)
        self.file_path_input = QLineEdit()
        self.file_path_input.setReadOnly(True)
        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self.browse_pdf)
        browse_button.setFixedWidth(80)
        file_hbox.addWidget(file_label)
        file_hbox.addWidget(self.file_path_input)
        file_hbox.addWidget(browse_button)
        file_layout.addLayout(file_hbox)
        
        # PDF信息显示
        self.pdf_info_label = QLabel("")
        self.pdf_info_label.setStyleSheet("color: #7f8c8d;")
        file_layout.addWidget(self.pdf_info_label)
        
        layout.addWidget(file_group)
        layout.addStretch()
        
        self.tab_widget.addTab(file_widget, "文件选择")
        
    def create_prompt_settings_tab(self):
        """创建提示词设置标签页"""
        prompt_widget = QWidget()
        layout = QVBoxLayout(prompt_widget)
        layout.setSpacing(10)
        
        # 模板选择
        template_group = QGroupBox("提示词模板")
        template_layout = QVBoxLayout(template_group)
        
        template_hbox = QHBoxLayout()
        template_label = QLabel("选择提示词模板:")
        template_label.setFixedWidth(120)
        self.template_combo = QComboBox()
        self.template_combo.addItems(list(self.prompt_templates.keys()))
        self.template_combo.currentTextChanged.connect(self.on_template_selected)
        template_hbox.addWidget(template_label)
        template_hbox.addWidget(self.template_combo)
        template_layout.addLayout(template_hbox)
        
        layout.addWidget(template_group)
        
        # 默认提示词显示
        default_prompt_group = QGroupBox("选定模板内容（只读）")
        default_prompt_layout = QVBoxLayout(default_prompt_group)
        self.default_prompt_text = QTextEdit()
        self.default_prompt_text.setReadOnly(True)
        self.default_prompt_text.setMaximumHeight(200)
        # 显示默认模板内容
        first_template = list(self.prompt_templates.keys())[0]
        self.default_prompt_text.setPlainText(self.prompt_templates[first_template])
        default_prompt_layout.addWidget(self.default_prompt_text)
        layout.addWidget(default_prompt_group)
        
        # 自定义提示词
        custom_prompt_group = QGroupBox("自定义提示词")
        custom_prompt_layout = QVBoxLayout(custom_prompt_group)
        self.prompt_text = QTextEdit()
        self.prompt_text.setMaximumHeight(200)
        custom_prompt_layout.addWidget(self.prompt_text)
        layout.addWidget(custom_prompt_group)
        
        layout.addStretch()
        self.tab_widget.addTab(prompt_widget, "提示词设置")
        
    def create_result_tab(self):
        """创建处理结果标签页"""
        result_widget = QWidget()
        layout = QVBoxLayout(result_widget)
        
        # 结果显示区域
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)
        
        self.tab_widget.addTab(result_widget, "处理结果")
        
    def create_button_area(self, main_layout):
        """创建底部按钮区域"""
        button_layout = QHBoxLayout()
        
        # 处理PDF按钮
        self.process_button = QPushButton("处理PDF并生成图像")
        self.process_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        self.process_button.clicked.connect(self.process_pdf)
        button_layout.addWidget(self.process_button)
        
        # 打开目录按钮
        open_dir_button = QPushButton("打开图像目录")
        open_dir_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5dade2;
            }
            QPushButton:pressed {
                background-color: #2c81ba;
            }
        """)
        open_dir_button.clicked.connect(self.open_output_directory)
        button_layout.addWidget(open_dir_button)
        
        # 退出按钮
        exit_button = QPushButton("退出")
        exit_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #ec7063;
            }
            QPushButton:pressed {
                background-color: #c0392b;
            }
        """)
        exit_button.clicked.connect(self.close)
        button_layout.addWidget(exit_button)
        
        main_layout.addLayout(button_layout)
        
    def on_template_selected(self, template_name):
        """当用户选择不同的提示词模板时调用"""
        self.selected_template = template_name
        self.default_prompt_text.setPlainText(self.prompt_templates[template_name])
        
    def browse_pdf(self):
        """浏览并选择PDF文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "选择PDF文件", 
            "", 
            "PDF files (*.pdf);;All files (*.*)"
        )
        if file_path:
            self.pdf_file_path = file_path
            self.file_path_input.setText(file_path)
            # 显示PDF信息
            try:
                pdf_info = get_pdf_info(file_path)
                info_text = f"页数: {pdf_info['pages']}, 大小: {pdf_info['file_size']} 字节"
                self.pdf_info_label.setText(info_text)
                self.pdf_info_label.setStyleSheet("color: #27ae60;")
            except Exception as e:
                self.pdf_info_label.setText(f"无法获取PDF信息: {str(e)}")
                self.pdf_info_label.setStyleSheet("color: #e74c3c;")
                
    def process_pdf(self):
        """处理PDF文件的主要函数"""
        # 切换到处理结果标签页
        self.tab_widget.setCurrentIndex(3)
        
        # 检查必要参数
        if not self.pdf_file_path:
            self.log_message("✗ 错误: 请选择一个PDF文件")
            return
            
        api_key = self.api_key_input.text()
        if not api_key:
            self.log_message("✗ 错误: 请输入API密钥")
            return
            
        # 获取用户自定义提示词，如果没有则使用默认提示词
        user_prompt = self.prompt_text.toPlainText().strip()
        if not user_prompt:
            # 使用选定的模板作为默认提示词
            user_prompt = self.prompt_templates[self.selected_template]
            
        self.result_text.clear()
        self.log_message("开始处理PDF文件...")
        
        # 在新线程中执行处理任务，避免阻塞UI
        self.worker_thread = WorkerThread(
            self.pdf_file_path,
            api_key,
            self.base_url_input.text(),
            self.model_input.text(),
            self.nanobanana_input.text(),
            user_prompt
        )
        self.worker_thread.log_signal.connect(self.log_message)
        self.worker_thread.finished_signal.connect(self.on_process_finished)
        self.worker_thread.start()
        
        # 禁用处理按钮，防止重复点击
        self.process_button.setEnabled(False)
        self.process_button.setText("处理中...")
        
    @Slot(bool, str)
    def on_process_finished(self, success, message):
        """处理完成后回调"""
        self.process_button.setEnabled(True)
        self.process_button.setText("处理PDF并生成图像")
        if success:
            self.log_message("✓ 全部处理完成")
        else:
            self.log_message(f"✗ 处理失败: {message}")
        
    def open_output_directory(self):
        """打开输出目录"""
        try:
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
            if sys.platform == "darwin":  # macOS
                subprocess.Popen(["open", output_dir])
            elif sys.platform == "win32":  # Windows
                subprocess.Popen(["explorer", output_dir])
            else:  # Linux
                subprocess.Popen(["xdg-open", output_dir])
        except Exception as e:
            self.log_message(f"✗ 无法打开目录: {str(e)}")

    @Slot(str)
    def log_message(self, message):
        """在结果文本框中记录消息"""
        self.result_text.append(message)
        # 滚动到底部
        scrollbar = self.result_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


def main():
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = PDFImageGeneratorApp()
    
    # 连接主题变化信号
    app.paletteChanged.connect(window.update_title_style)
    
    # 显示窗口
    window.show()
    
    # 初始更新标题样式
    window.update_title_style()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()