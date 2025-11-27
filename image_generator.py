"""
Image Generator Module
Handles image generation using Nano-Banana and saving images to disk
"""
import base64
import re
import os
import time
import requests
from io import BytesIO
from PIL import Image
from llm_client import LLMClient
from config import OUTPUT_DIR


def generate_and_save_image(image_prompt, filename=None, api_key=None, base_url=None, model_name=None):
    """
    Generate an image using Nano-Banana and save it to disk
    
    Args:
        image_prompt (str): Prompt for image generation
        filename (str): Filename for the saved image (without extension)
        api_key (str): API key for the service
        base_url (str): Base URL for the API
        model_name (str): Name of the model to use
        
    Returns:
        str: Path to the saved image file
    """
    try:
        # Initialize LLM client with provided parameters
        client = LLMClient(api_key=api_key, base_url=base_url)
        
        # Send request to Nano-Banana
        response = client.send_image_request_to_nanobanana(image_prompt, model_name)
        print("请求发送成功")
        
        if not response:
            raise Exception("响应内容为空")
            
        print(f"响应内容预览 (前500字符):\n{'-'*20}\n{response[:500]}\n{'-'*20}")
        
        # Extract image data from response
        image_data = extract_image_from_response(response)
        
        if not image_data:
            raise Exception("No image data found in Nano-Banana response")
            
        # Save image to disk
        image_path = save_image(image_data, filename)
        
        return image_path
        
    except Exception as e:
        raise Exception(f"Error generating image: {str(e)}")


def extract_image_from_response(response):
    """
    从响应中提取图像数据 (URL 或 Base64)
    """
    
    # 1. 优先匹配 Markdown 图片语法: ![alt](url)
    # 这种方式最准确，能提取出完整的 URL，包括查询参数
    markdown_pattern = r'!\[.*?\]\((https?://[^\)]+)\)'
    markdown_matches = re.findall(markdown_pattern, response)
    
    target_url = None
    
    if markdown_matches:
        print(f"  [解析] 发现 Markdown 图片链接: {markdown_matches[0]}")
        target_url = markdown_matches[0]
    else:
        # 2. 如果没有 Markdown，尝试匹配纯 URL
        # 修复后的正则：不再强制要求以图片后缀结尾，而是匹配 http 开头直到遇到空格、换行或括号
        # 这能捕获类似 https://cdn.com/img?token=123 的链接
        url_pattern = r'(https?://[^\s\)]+)'
        url_matches = re.findall(url_pattern, response)
        
        # 过滤掉显然不是图片的 URL (可选，根据实际情况调整)
        valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.webp', 'usercontent', 'cdn', 'blob', 'pfst')
        
        for url in url_matches:
            # 简单的启发式过滤：如果包含常见图片后缀或常见CDN关键字
            if any(ext in url.lower() for ext in valid_extensions):
                print(f"  [解析] 发现潜在图片 URL: {url}")
                target_url = url
                break
    
    # 如果找到了 URL，进行下载
    if target_url:
        try:
            print(f"  [下载] 正在下载: {target_url[:50]}...")
            # 增加 headers 模拟浏览器，防止某些 CDN 拒绝 python-requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            url_response = requests.get(target_url, headers=headers, timeout=30)
            if url_response.status_code == 200:
                print(f"  [下载] 成功，大小: {len(url_response.content)} 字节")
                return url_response.content
            else:
                print(f"  [下载] 失败，状态码: {url_response.status_code}")
        except Exception as e:
            print(f"  [下载] 异常: {str(e)}")

    # 3. 查找 Base64 编码
    print("  [解析] 尝试查找 Base64 数据...")
    b64_pattern = r"data:image/\w+;base64,([A-Za-z0-9+/=]+)"
    match = re.search(b64_pattern, response)
    
    if match:
        base64_data = match.group(1)
        try:
            return base64.b64decode(base64_data)
        except Exception as e:
            print(f"  [Base64] 解码失败: {e}")

    return None


def save_image(image_data, filename=None):
    """
    保存图像数据到文件
    """
    # Create filename if not provided
    if not filename:
        filename = f"generated_image_{int(time.time())}"
        
    # Ensure filename has proper extension
    if not filename.endswith(('.png', '.jpg', '.jpeg')):
        filename += ".png"
        
    # Full path to save image
    image_path = os.path.join(OUTPUT_DIR, filename)
    
    # Try to use PIL to verify and save (but not force resize to 1440*768)
    try:
        image = Image.open(BytesIO(image_data))
        print(f"  [保存] 图片原始尺寸: {image.size}, 格式: {image.format}")
        
        # Save image without resizing to preserve original dimensions
        image.save(image_path, format="PNG")
        print(f"  [保存] 保持原始图片尺寸不变")
        
    except Exception as e:
        print(f"  [保存] PIL 处理失败 ({e})，尝试直接写入原始字节...")
        with open(image_path, 'wb') as f:
            f.write(image_data)
    
    return image_path


def save_code_as_image(code, filename=None):
    """
    Save code as an image (placeholder for future implementation)
    
    Args:
        code (str): Code to save as image
        filename (str): Filename for the saved image
        
    Returns:
        str: Path to the saved image file
    """
    # This would be where we convert code to an image representation
    # For now, we'll just generate an image using Nano-Banana with the code as prompt
    return generate_and_save_image(code, filename)