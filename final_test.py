#!/usr/bin/env python3
"""
最终测试程序 - 验证主程序的修复
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入必要的模块
from image_generator import generate_and_save_image

def test_image_generation():
    """测试图像生成和保存功能"""
    print("开始测试图像生成和保存功能...")
    
    try:
        # 使用测试提示词
        test_prompt = "画一个简单的笑脸"
        
        # 从环境变量或配置文件获取API设置
        from config import API_KEY, BASE_URL, NANO_BANANA_MODEL
        import os
        api_key = os.getenv("POE_API_KEY", API_KEY)
        base_url = BASE_URL
        model_name = NANO_BANANA_MODEL
        
        print(f"API Key: {'*' * len(api_key) if api_key else '未设置'}")
        print(f"Base URL: {base_url}")
        print(f"Model Name: {model_name}")
        print(f"Prompt: {test_prompt}")
        
        # 生成并保存图像
        print("正在生成图像...")
        image_path = generate_and_save_image(
            test_prompt,
            filename="final_test_image",
            api_key=api_key,
            base_url=base_url,
            model_name=model_name
        )
        
        print(f"✓ 图像生成成功: {image_path}")
        
        # 验证文件存在
        if os.path.exists(image_path):
            file_size = os.path.getsize(image_path)
            print(f"✓ 文件验证通过: 大小 {file_size} 字节")
            return True
        else:
            print("✗ 文件验证失败: 文件不存在")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("最终测试程序")
    print("=" * 30)
    
    if test_image_generation():
        print("\n🎉 所有测试通过！主程序应该可以正常工作了。")
    else:
        print("\n❌ 测试失败，请检查错误信息。")