"""
MinerU 图片识别模块
用于将题目图片转换为 Markdown 文本
"""
import os
import tempfile
import subprocess
import json


def parse_image_to_markdown(image_path: str, api_token: str = None) -> str:
    """
    将图片转换为 Markdown 文本
    
    参数:
        image_path: 图片文件路径
        api_token: MinerU API Token（可选，默认使用环境变量）
    
    返回:
        Markdown 格式的文本内容
    """
    try:
        # 如果未提供 token，从环境变量获取
        if api_token is None:
            api_token = os.getenv("MINERU_API_TOKEN")
        
        if not api_token:
            raise ValueError("请设置 MINERU_API_TOKEN 环境变量或在调用时传入 token")
        
        # 创建临时输出目录
        output_dir = tempfile.mkdtemp()
        
        # 调用 MinerU API
        return _call_mineru_api(image_path, api_token, output_dir)
        
    except Exception as e:
        raise Exception(f"MinerU 识别失败: {str(e)}")


def _call_mineru_api(image_path: str, api_token: str, output_dir: str) -> str:
    """
    调用 MinerU 进行图片识别
    使用 uvx 命令行工具
    """
    import subprocess
    import json
    
    try:
        print(f"正在使用 MinerU 识别图片...")
        print(f"图片路径: {image_path}")
        print(f"输出目录: {output_dir}")
        
        # 构建 uvx 命令
        cmd = [
            "uvx",
            "mineru-open-mcp",
            f"MINERU_API_TOKEN={api_token}"
        ]
        
        # 注意：uvx mineru-open-mcp 是一个 MCP server，不能直接这样调用
        # 我们需要使用另一种方式 - 直接调用 mineru 的 Python SDK
        
        # 尝试使用 mineru 官方 SDK
        return _call_mineru_sdk(image_path, api_token, output_dir)
                
    except Exception as e:
        raise Exception(f"MinerU 调用失败: {str(e)}")


def _call_mineru_sdk(image_path: str, api_token: str, output_dir: str) -> str:
    """
    使用 MinerU Python SDK 进行识别
    """
    try:
        # 尝试导入 mineru 包
        from magic_pdf.libs.pdf_check import detect_invalid_chars_by_pymupdf
        
        # 如果导入成功，说明已安装 magic-pdf
        print("检测到 magic-pdf 已安装")
        
        # 使用 magic-pdf 处理图片
        from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
        from magic_pdf.rapidocr_local import RapidOCR
        
        # 这里需要根据实际的 magic-pdf API 来调用
        # 暂时返回提示信息
        return "MinerU SDK 调用需要进一步配置"
        
    except ImportError:
        # 如果未安装 magic-pdf，使用备用方案
        print("magic-pdf 未安装，使用备用方案")
        return _use_backup_method(image_path, api_token)


def _use_backup_method(image_path: str, api_token: str) -> str:
    """
    备用方案：使用其他 OCR 服务
    这里可以使用百度 OCR、腾讯 OCR 等
    """
    # 暂时返回提示
    return """
# 识别结果

**提示：** MinerU API 调用需要特殊配置。

当前演示模式显示模拟数据。

如需使用真实识别功能，请：
1. 安装 magic-pdf: `pip install magic-pdf`
2. 或配置其他 OCR 服务

---

## 示例题目

这是一道数学题目的示例内容...
    """


def parse_images_batch(image_paths: list, api_token: str = None) -> list:
    """
    批量解析多张图片
    
    参数:
        image_paths: 图片文件路径列表
        api_token: MinerU API Token
    
    返回:
        Markdown 文本列表
    """
    results = []
    for image_path in image_paths:
        try:
            markdown = parse_image_to_markdown(image_path, api_token)
            results.append({
                "image": image_path,
                "markdown": markdown,
                "success": True
            })
        except Exception as e:
            results.append({
                "image": image_path,
                "error": str(e),
                "success": False
            })
    
    return results
