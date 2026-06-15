"""
大模型调用模块
使用通义千问 API 生成题目解答
支持文本和视觉模型
"""
import os
import requests
import base64


PROXY_ENV_KEYS = (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
)


def _disable_proxy_env() -> None:
    for key in PROXY_ENV_KEYS:
        os.environ.pop(key, None)
    os.environ["NO_PROXY"] = "*"
    os.environ["no_proxy"] = "*"


def _request(method: str, url: str, **kwargs):
    """发送请求时忽略系统代理环境变量，避免国内直连场景被错误代理劫持。"""
    _disable_proxy_env()
    kwargs.setdefault("proxies", {"http": None, "https": None})
    with requests.Session() as session:
        session.trust_env = False
        session.proxies.clear()
        return session.request(method, url, **kwargs)


def get_answer_from_qwen(question_text: str, subject: str = "综合", api_key: str = None) -> str:
    """
    调用通义千问 API 生成题目解答（纯文本模式）
    
    参数:
        question_text: 题目文本（Markdown 格式）
        subject: 学科类型（数学/语文/英语/物理/化学等）
        api_key: 通义千问 API Key（可选，默认使用环境变量）
    
    返回:
        解答文本
    """
    try:
        # 如果未提供 API Key，从环境变量获取
        if api_key is None:
            api_key = os.getenv("DASHSCOPE_API_KEY")
        
        if not api_key:
            raise ValueError("请设置 DASHSCOPE_API_KEY 环境变量或在调用时传入 api_key")
        
        # 构建提示词
        prompt = f"""你是一位经验丰富的高中{subject}教师，请以专业、清晰的方式解答以下题目。

要求：
1. 先分析题目考点和解题思路
2. 给出详细的解题步骤
3. 最后给出答案
4. 如果有多种解法，可以简要说明
5. 使用 LaTeX 格式书写数学公式

题目内容：
{question_text}

请开始解答："""

        # 调用通义千问 API
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "qwen-turbo",
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            "parameters": {
                "result_format": "text",
                "temperature": 0.7,
                "top_p": 0.8
            }
        }
        
        response = _request("POST", url, json=data, headers=headers, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        # 提取回答内容
        if "output" in result and "text" in result["output"]:
            return result["output"]["text"]
        else:
            raise Exception(f"API 返回格式异常: {result}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"调用大模型 API 失败: {str(e)}")
    except Exception as e:
        raise Exception(f"生成解答失败: {str(e)}")


def get_answer_from_image(image_path: str, subject: str = "综合", api_key: str = None) -> str:
    """
    调用通义千问 VL（视觉语言模型）直接识别图片并解答
    
    参数:
        image_path: 图片文件路径
        subject: 学科类型
        api_key: 通义千问 API Key
    
    返回:
        解答文本
    """
    try:
        if api_key is None:
            api_key = os.getenv("DASHSCOPE_API_KEY")
        
        if not api_key:
            raise ValueError("请设置 DASHSCOPE_API_KEY 环境变量")
        
        # 读取图片并转换为 base64
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # 构建提示词
        prompt = f"""你是一位经验丰富的高中{subject}教师。请完成以下任务：

1. 识别图片中的题目内容
2. 以专业、清晰的方式解答题目
3. 给出详细的解题步骤和最终答案
4. 使用 LaTeX 格式书写数学公式

请先输出识别的题目内容，然后给出详细解答。"""

        # 调用通义千问 VL API
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "qwen-vl-plus",  # 使用视觉语言模型
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "image": f"data:image/jpeg;base64,{image_data}"
                            },
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            },
            "parameters": {
                "result_format": "message"
            }
        }
        
        print("正在调用通义千问 VL 模型...")
        response = _request("POST", url, json=data, headers=headers, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        print(f"VL API 响应状态: {result.get('output', {}).get('choices', [{}])[0].get('message', {}).get('role', 'unknown')}")
        
        # 提取回答内容
        if "output" in result and "choices" in result["output"]:
            choices = result["output"]["choices"]
            if choices and len(choices) > 0:
                message = choices[0].get("message", {})
                content = message.get("content", [])
                
                # VL 模型返回的内容可能是列表
                if isinstance(content, list):
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict) and "text" in item:
                            text_parts.append(item["text"])
                    return "\n".join(text_parts)
                elif isinstance(content, str):
                    return content
        
        raise Exception(f"API 返回格式异常: {result}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"调用 VL API 失败: {str(e)}")
    except Exception as e:
        raise Exception(f"图片识别与解答失败: {str(e)}")


def detect_subject(question_text: str) -> str:
    """
    根据题目内容自动检测学科类型
    
    参数:
        question_text: 题目文本
    
    返回:
        学科类型字符串
    """
    text_lower = question_text.lower()
    
    # 简单的关键词匹配
    if any(keyword in text_lower for keyword in ['数列', '函数', '几何', '概率', '方程', '不等式']):
        return "数学"
    elif any(keyword in text_lower for keyword in ['文言文', '古诗', '阅读', '作文', '修辞']):
        return "语文"
    elif any(keyword in text_lower for keyword in ['grammar', 'vocabulary', 'reading comprehension']):
        return "英语"
    elif any(keyword in text_lower for keyword in ['力学', '电磁', '光学', '热学']):
        return "物理"
    elif any(keyword in text_lower for keyword in ['化学反应', '元素', '化合物', '方程式']):
        return "化学"
    else:
        return "综合"
