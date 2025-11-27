#!/usr/bin/env python3
"""
PDF to Image Generator Application
此应用程序允许用户上传PDF文件，通过大模型处理，并使用Nano-Banana生成图像。
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
import sys
import subprocess

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入自定义模块
from pdf_handler import read_pdf_content, get_pdf_info
from llm_client import LLMClient
from code_parser import extract_last_code_block
from image_generator import generate_and_save_image
from config import API_KEY, BASE_URL, MODEL_NAME, NANO_BANANA_MODEL, PROMPT_TEMPLATES


class PDFImageGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to Image Generator")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)  # 设置最小窗口尺寸
        
        # 设置主题样式
        self.style = ttk.Style("cosmo")  # 使用cosmo主题
        
        # 文件路径变量
        self.pdf_file_path = tk.StringVar()
        self.api_key = tk.StringVar(value=os.getenv("POE_API_KEY", API_KEY))  # 优先使用环境变量
        self.base_url = tk.StringVar(value=BASE_URL)
        self.model_name = tk.StringVar(value=MODEL_NAME)
        self.nanobanana_model = tk.StringVar(value=NANO_BANANA_MODEL)
        
        # 提示词模板变量
        self.prompt_templates = PROMPT_TEMPLATES
        self.selected_template = tk.StringVar(value=list(PROMPT_TEMPLATES.keys())[0])  # 默认选择第一个模板
        
        # 创建UI
        self.create_widgets()
        
        # 设置默认选中的标签页为"文件选择"
        self.notebook.select(1)  # 选择索引为1的标签页（文件选择）

        
    def create_widgets(self):
        # 主标题
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, pady=10)
        
        title_label = ttk.Label(
            title_frame, 
            text="PDF to Image Generator", 
            font=("Arial", 18, "bold"),
            bootstyle="primary"
        )
        title_label.pack()
        
        # 创建 Notebook 用于分隔不同功能区域
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        # 绑定标签页切换事件
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # API设置标签页
        api_frame = ttk.Frame(self.notebook)
        self.notebook.add(api_frame, text="API 设置")
        
        # API Key
        api_key_frame = ttk.Frame(api_frame)
        api_key_frame.pack(fill=X, padx=10, pady=5)
        ttk.Label(api_key_frame, text="API Key:", width=20).pack(side=LEFT)
        ttk.Entry(api_key_frame, textvariable=self.api_key, show="*").pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))
        
        # Base URL
        base_url_frame = ttk.Frame(api_frame)
        base_url_frame.pack(fill=X, padx=10, pady=5)
        ttk.Label(base_url_frame, text="Base URL:", width=20).pack(side=LEFT)
        ttk.Entry(base_url_frame, textvariable=self.base_url).pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))
        
        # Model Name
        model_frame = ttk.Frame(api_frame)
        model_frame.pack(fill=X, padx=10, pady=5)
        ttk.Label(model_frame, text="Model Name:", width=20).pack(side=LEFT)
        ttk.Entry(model_frame, textvariable=self.model_name).pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))
        
        # Nano-Banana Model
        nanobanana_frame = ttk.Frame(api_frame)
        nanobanana_frame.pack(fill=X, padx=10, pady=5)
        ttk.Label(nanobanana_frame, text="Nano-Banana Model:", width=20).pack(side=LEFT)
        ttk.Entry(nanobanana_frame, textvariable=self.nanobanana_model).pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))
        
        # 文件选择标签页
        file_frame = ttk.Frame(self.notebook)
        self.notebook.add(file_frame, text="文件选择")
        
        # 文件路径显示
        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.pack(fill=X, padx=10, pady=10)
        ttk.Label(file_select_frame, text="选择的文件:", width=15).pack(side=LEFT)
        ttk.Entry(file_select_frame, textvariable=self.pdf_file_path, state="readonly").pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))
        ttk.Button(file_select_frame, text="浏览...", command=self.browse_pdf, bootstyle="info").pack(side=LEFT)
        
        # PDF信息显示
        self.pdf_info_label = ttk.Label(file_frame, text="", bootstyle="secondary")
        self.pdf_info_label.pack(padx=10, pady=5)
        
        # 提示词标签页
        prompt_frame = ttk.Frame(self.notebook)
        self.notebook.add(prompt_frame, text="提示词设置")
        
        # 模板选择
        template_frame = ttk.Frame(prompt_frame)
        template_frame.pack(fill=X, padx=10, pady=5)
        
        ttk.Label(template_frame, text="选择提示词模板:", width=15).pack(side=LEFT)
        self.template_combobox = ttk.Combobox(
            template_frame, 
            textvariable=self.selected_template,
            values=list(self.prompt_templates.keys()),
            state="readonly"
        )
        self.template_combobox.pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))
        self.template_combobox.bind("<<ComboboxSelected>>", self.on_template_selected)
        
        # 内置提示词说明
        prompt_info = ttk.Label(
            prompt_frame, 
            text="内置提示词（请在下方输入您的自定义提示词，留空将使用选定的模板）:",
            bootstyle="secondary"
        )
        prompt_info.pack(anchor=W, padx=10, pady=(10, 5))
        
        # 默认提示词显示（不可编辑）
        default_prompt_label = ttk.Label(
            prompt_frame, 
            text="选定模板内容:", 
            font=("Arial", 10, "bold")
        )
        default_prompt_label.pack(anchor=W, padx=10, pady=5)
        
        self.default_prompt_text = scrolledtext.ScrolledText(
            prompt_frame, 
            height=8,
            bg="#f8f8f8"
        )
        self.default_prompt_text.pack(fill=BOTH, expand=YES, padx=10, pady=5)
        
        # 显示默认模板内容
        first_template = list(self.prompt_templates.keys())[0]
        self.default_prompt_text.insert(tk.END, self.prompt_templates[first_template])
        self.default_prompt_text.config(state=tk.DISABLED)  # 设置为只读
        
        ttk.Label(
            prompt_frame, 
            text="自定义提示词:", 
            font=("Arial", 10, "bold")
        ).pack(anchor=W, padx=10, pady=(10, 5))
        
        self.prompt_text = scrolledtext.ScrolledText(prompt_frame, height=6)
        self.prompt_text.pack(fill=BOTH, expand=YES, padx=10, pady=5)
        
        # 结果显示标签页
        result_frame = ttk.Frame(self.notebook)
        self.notebook.add(result_frame, text="处理结果")
        
        self.result_text = scrolledtext.ScrolledText(result_frame)
        self.result_text.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        # 操作按钮框架
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        ttk.Button(
            button_frame, 
            text="处理PDF并生成图像", 
            command=self.process_pdf,
            bootstyle="success"
        ).pack(side=LEFT, padx=5)
        
        # 打开输出目录按钮（常驻）
        self.open_dir_button = ttk.Button(
            button_frame, 
            text="打开图像目录", 
            command=lambda: self.open_output_directory(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')),
            bootstyle="info"
        )
        self.open_dir_button.pack(side=LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="退出", 
            command=self.root.quit,
            bootstyle="danger"
        ).pack(side=RIGHT, padx=5)
        
    def on_template_selected(self, event):
        """当用户选择不同的提示词模板时调用"""
        selected = self.selected_template.get()
        self.default_prompt_text.config(state=tk.NORMAL)  # 临时启用编辑
        self.default_prompt_text.delete(1.0, tk.END)
        self.default_prompt_text.insert(tk.END, self.prompt_templates[selected])
        self.default_prompt_text.config(state=tk.DISABLED)  # 重新设为只读
        
    def on_tab_changed(self, event):
        """标签页切换事件处理"""
        # 获取当前选中的标签页索引
        selected_tab_index = self.notebook.index(self.notebook.select())
        
        # 更新标签页样式以突出显示当前选中项
        for i in range(self.notebook.index("end")):
            tab_id = self.notebook.tabs()[i]
            if i == selected_tab_index:
                # 当前选中的标签页使用强调样式
                pass  # ttkbootstrap 的 notebook 不支持动态更改标签页样式
            else:
                # 其他标签页使用默认样式
                pass  # ttkbootstrap 的 notebook 不支持动态更改标签页样式

    def browse_pdf(self):
        """浏览并选择PDF文件"""
        file_path = filedialog.askopenfilename(
            title="选择PDF文件",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            self.pdf_file_path.set(file_path)
            # 显示PDF信息
            try:
                pdf_info = get_pdf_info(file_path)
                info_text = f"页数: {pdf_info['pages']}, 大小: {pdf_info['file_size']} 字节"
                self.pdf_info_label.config(text=info_text)
            except Exception as e:
                self.pdf_info_label.config(text=f"无法获取PDF信息: {str(e)}", bootstyle="danger")
            
    def process_pdf(self):
        """处理PDF文件的主要函数"""
        # 切换到处理结果标签页
        self.notebook.select(3)  # 选择索引为3的标签页（处理结果）
        
        # 检查必要参数
        if not self.pdf_file_path.get():
            self.log_message("✗ 错误: 请选择一个PDF文件")
            return
            
        if not self.api_key.get():
            self.log_message("✗ 错误: 请输入API密钥")
            return
            
        # 获取用户自定义提示词，如果没有则使用默认提示词
        user_prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not user_prompt:
            # 使用选定的模板作为默认提示词
            selected_template = self.selected_template.get()
            user_prompt = self.prompt_templates[selected_template]
            
        self.result_text.delete(1.0, tk.END)
        self.log_message("开始处理PDF文件...")
        
        try:
            # 在新线程中执行处理任务，避免阻塞UI
            import threading
            thread = threading.Thread(target=self._process_pdf_thread)
            thread.daemon = True
            thread.start()
        except Exception as e:
            self.log_message(f"✗ 处理过程中出现错误: {str(e)}")
            
    def _process_pdf_thread(self):
        """在后台线程中处理PDF的实际工作"""
        # 获取用户自定义提示词，如果没有则使用默认提示词
        user_prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not user_prompt:
            # 使用选定的模板作为默认提示词
            selected_template = self.selected_template.get()
            user_prompt = self.prompt_templates[selected_template]
            
        try:
            # 读取PDF内容
            self.log_message("步骤 1/6: 正在读取PDF内容...")
            pdf_content = read_pdf_content(self.pdf_file_path.get())
            self.log_message(f"✓ PDF内容读取完成，共 {len(pdf_content)} 个字符")
            
            # 初始化LLM客户端
            self.log_message("步骤 2/6: 正在连接到大语言模型...")
            client = LLMClient(
                api_key=self.api_key.get(),
                base_url=self.base_url.get()
            )
            self.log_message("✓ 大语言模型连接成功")
            
            # 发送请求到大语言模型
            self.log_message("步骤 3/6: 正在发送请求到大语言模型...")
            llm_response = client.send_pdf_to_llm(pdf_content, user_prompt, self.model_name.get())
            self.log_message("✓ 大语言模型响应接收完成")
            
            # 显示LLM响应摘要
            response_length = len(llm_response) if llm_response else 0
            self.log_message(message=f"  响应长度: {response_length} 字符")
            
            # 输出第一步大模型响应返回的结果
            self.log_message("  大模型完整响应:")
            self.result_text.insert(tk.END, "大模型完整响应:\n")
            self.result_text.insert(tk.END, "=" * 50 + "\n")
            self.result_text.insert(tk.END, (llm_response or "") + "\n")
            self.result_text.insert(tk.END, "=" * 50 + "\n\n")
            self.result_text.see(tk.END)  # 滚动到底部
            self.root.update()
            
            # 提取代码块
            self.log_message("步骤 4/6: 正在提取代码块...")
            code_block = extract_last_code_block(llm_response)
            
            if not code_block:
                self.log_message("⚠ 未在大语言模型响应中找到代码块")
                # 显示完整响应供用户查看
                self.result_text.insert(tk.END, "\n完整的大语言模型响应:\n")
                self.result_text.insert(tk.END, "=" * 50 + "\n")
                self.result_text.insert(tk.END, (llm_response or "") + "\n")
                self.result_text.insert(tk.END, "=" * 50 + "\n\n")
                raise Exception("未在大语言模型响应中找到代码块")
                
            self.log_message("✓ 代码块提取完成")
            code_length = len(code_block) if code_block else 0
            self.log_message(f"  代码块长度: {code_length} 字符")
            
            # 显示提取的代码块
            self.result_text.insert(tk.END, "提取的代码块:\n")
            self.result_text.insert(tk.END, "=" * 50 + "\n")
            self.result_text.insert(tk.END, (code_block or "") + "\n")
            self.result_text.insert(tk.END, "=" * 50 + "\n\n")
            
            # 使用Nano-Banana生成图像
            self.log_message("步骤 5/6: 正在使用Nano-Banana生成图像...")
            # 直接使用提取的代码块作为图像生成提示词
            image_path = generate_and_save_image(
                code_block,
                api_key=self.api_key.get(),
                base_url=self.base_url.get(),
                model_name=self.nanobanana_model.get()
            )
            self.log_message("✓ 图像生成完成")
            
            # 完成
            self.log_message("步骤 6/6: 图像已成功生成并保存")
            self.log_message(f"保存路径: {image_path}")
        except Exception as e:
            self.log_message(f"✗ 处理过程中出现错误: {str(e)}")
            
    def open_output_directory(self, directory_path):
        """打开输出目录"""
        try:
            if sys.platform == "darwin":  # macOS
                subprocess.Popen(["open", directory_path])
            elif sys.platform == "win32":  # Windows
                subprocess.Popen(["explorer", directory_path])
            else:  # Linux
                subprocess.Popen(["xdg-open", directory_path])
        except Exception as e:
            self.log_message(f"✗ 无法打开目录: {str(e)}")

    def log_message(self, message):
        """在结果文本框中记录消息并刷新界面"""
        # 根据消息类型设置颜色
        if message.startswith("✓"):
            tag = "success"
            self.result_text.tag_configure("success", foreground="green")
        elif message.startswith("✗"):
            tag = "error"
            self.result_text.tag_configure("error", foreground="red")
        elif message.startswith("⚠"):
            tag = "warning"
            self.result_text.tag_configure("warning", foreground="orange")
        elif message.startswith("步骤"):
            tag = "step"
            self.result_text.tag_configure("step", foreground="blue", font=("Arial", 10, "bold"))
        else:
            tag = "normal"
            self.result_text.tag_configure("normal", foreground="black")
            
        self.result_text.insert(tk.END, message + "\n", tag)
        self.result_text.see(tk.END)  # 滚动到底部
        self.root.update()


def main():
    root = ttk.Window(themename="cosmo")  # 使用ttkbootstrap创建主窗口
    app = PDFImageGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()