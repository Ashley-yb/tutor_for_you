"""
MinerU 图片识别模块
用于将题目图片转换为 Markdown 文本
使用 MinerU HTTP API
"""
import os
import time
import requests
import zipfile
import tempfile
from pathlib import Path
from uuid import uuid4


DEBUG_LOG_PATH = Path(__file__).with_name("mineru_debug.log")
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


def _debug(message: str) -> None:
    safe_message = message.replace("\r", " ").replace("\n", " ")
    print(safe_message)
    try:
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {safe_message}\n")
    except OSError:
        pass


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
        
        # 通过 MinerU 批量文件接口获取预签名上传地址，上传后用 batch_id 查询结果。
        _debug("正在上传文件到 MinerU...")
        batch_id = _upload_file_to_mineru(image_path, api_token)
        
        # 轮询查询任务结果
        _debug(f"正在等待解析完成 (batch_id: {batch_id})...")
        result_zip_url = _poll_batch_result(batch_id, api_token)
        
        # 下载并提取 Markdown 内容
        _debug("正在下载解析结果...")
        markdown_content = _download_and_extract_markdown(result_zip_url)
        
        return markdown_content
        
    except Exception as e:
        raise Exception(f"MinerU 识别失败: {str(e)}")


def _upload_file_to_mineru(image_path: str, api_token: str) -> str:
    """
    使用 MinerU 批量文件接口获取预签名 URL 并上传文件。
    
    返回:
        batch_id: 后续查询解析结果使用
    """
    try:
        if not os.path.exists(image_path):
            raise Exception(f"文件不存在: {image_path}")
        
        file_name = Path(image_path).name
        file_size = os.path.getsize(image_path)
        _debug(f"文件大小: {file_size} bytes")
        
        url = "https://mineru.net/api/v4/file-urls/batch"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_token}"
        }
        data_id = uuid4().hex
        data = {
            "enable_formula": True,
            "enable_table": True,
            "language": "ch",
            "model_version": "vlm",
            "files": [
                {
                    "name": file_name,
                    "is_ocr": True,
                    "data_id": data_id
                }
            ]
        }
        
        _debug("正在获取 MinerU 上传链接: /api/v4/file-urls/batch")
        response = _request("POST", url, headers=headers, json=data, timeout=30)
        if response.status_code != 200:
            _debug(f"获取上传链接失败 HTTP {response.status_code}: {response.text[:500]}")
            response.raise_for_status()
        result = response.json()
        _debug(f"获取上传链接响应 code={result.get('code')} keys={list((result.get('data') or {}).keys())}")
        if result.get("code") != 0:
            raise Exception(f"获取上传链接失败: {result.get('msg') or result}")
        
        result_data = result.get("data") or {}
        batch_id = result_data.get("batch_id")
        upload_urls = result_data.get("file_urls") or result_data.get("file_url") or []
        if isinstance(upload_urls, str):
            upload_urls = [upload_urls]
        if not batch_id:
            raise Exception(f"MinerU 未返回 batch_id: {result}")
        if not upload_urls:
            raise Exception(f"MinerU 未返回上传链接: {result}")
        
        upload_url = _pick_upload_url(upload_urls[0])
        _debug("正在上传文件到 MinerU 预签名地址...")
        with open(image_path, 'rb') as f:
            upload_response = _request("PUT", upload_url, data=f, timeout=120)
        if upload_response.status_code not in (200, 201, 204):
            _debug(f"预签名地址上传失败 HTTP {upload_response.status_code}: {upload_response.text[:500]}")
            raise Exception(
                f"上传到预签名地址失败: HTTP {upload_response.status_code} - "
                f"{upload_response.text[:200]}"
            )
        
        _debug(f"文件上传成功，batch_id: {batch_id}")
        time.sleep(2)
        return batch_id
        
    except Exception as e:
        raise Exception(f"文件上传失败: {str(e)}")


def _pick_upload_url(upload_item):
    if isinstance(upload_item, str):
        return upload_item
    if isinstance(upload_item, dict):
        for key in ("upload_url", "url", "file_url"):
            if upload_item.get(key):
                return upload_item[key]
    raise Exception(f"上传链接格式异常: {upload_item}")


def _poll_batch_result(batch_id: str, api_token: str, max_wait_time: int = 300) -> str:
    """
    轮询查询批量上传任务结果。
    
    返回:
        full_zip_url: 解析结果压缩包 URL
    """
    try:
        headers = {
            "Authorization": f"Bearer {api_token}"
        }
        urls = [
            f"https://mineru.net/api/v4/extract-results/batch/{batch_id}",
            f"https://mineru.net/api/v4/extract-results/{batch_id}",
        ]
        
        start_time = time.time()
        poll_interval = 5  # 每 5 秒轮询一次
        
        while time.time() - start_time < max_wait_time:
            response = None
            last_error = None
            for url in urls:
                _debug(f"查询 MinerU 结果: {url}")
                response = _request("GET", url, headers=headers, timeout=30)
                if response.status_code == 404:
                    last_error = f"HTTP 404: {response.text[:200]}"
                    continue
                if response.status_code != 200:
                    _debug(f"查询结果失败 HTTP {response.status_code}: {response.text[:500]}")
                    response.raise_for_status()
                break
            else:
                raise Exception(f"查询结果接口不存在或 batch_id 无效: {last_error}")
            
            result = response.json()
            _debug(f"查询结果响应 code={result.get('code')} data_type={type(result.get('data')).__name__}")
            if result.get("code") != 0:
                raise Exception(f"查询任务失败: {result.get('msg')}")
            
            item = _extract_first_result_item(result)
            state = (item.get("state") or item.get("status") or "").strip().lower()
            _debug(f"任务状态: {state}")
            
            if state == "done":
                full_zip_url = (
                    item.get("full_zip_url")
                    or item.get("zip_url")
                    or item.get("result_url")
                    or item.get("url")
                )
                if not full_zip_url:
                    raise Exception(f"未获取到结果 URL: {result}")
                return full_zip_url
            elif state == "failed":
                err_msg = item.get("err_msg") or item.get("message") or "未知错误"
                raise Exception(f"任务失败: {err_msg}")
            elif state in ["waiting-file", "waiting_file", "pending", "running", "converting", "uploaded", "processing"]:
                time.sleep(poll_interval)
            else:
                _debug(f"遇到 MinerU 临时状态，继续等待: {state or 'empty'}")
                time.sleep(poll_interval)
        
        raise Exception(f"任务超时（超过 {max_wait_time} 秒）")
        
    except Exception as e:
        raise Exception(f"查询任务结果失败: {str(e)}")


def _extract_first_result_item(result: dict) -> dict:
    data = result.get("data") or {}
    for key in ("extract_result", "extract_results", "results", "files"):
        items = data.get(key)
        if isinstance(items, list) and items:
            return items[0]
    if isinstance(data, list) and data:
        return data[0]
    if isinstance(data, dict):
        return data
    raise Exception(f"查询结果格式异常: {result}")


def _download_and_extract_markdown(zip_url: str) -> str:
    """
    下载并提取 Markdown 内容
    
    参数:
        zip_url: 压缩包 URL
    
    返回:
        markdown_content: Markdown 文本内容
    """
    try:
        # 下载压缩包
        response = _request("GET", zip_url, timeout=60)
        response.raise_for_status()
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            tmp_file.write(response.content)
            tmp_zip_path = tmp_file.name
        
        # 解压
        extract_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(tmp_zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # 查找 full.md 文件
        md_file = None
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.endswith('.md') and 'full' in file.lower():
                    md_file = os.path.join(root, file)
                    break
            if md_file:
                break
        
        if not md_file:
            # 如果没找到 full.md，尝试找任何 .md 文件
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file.endswith('.md'):
                        md_file = os.path.join(root, file)
                        break
                if md_file:
                    break
        
        if not md_file:
            raise Exception("未找到 Markdown 文件")
        
        # 读取 Markdown 内容
        with open(md_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # 清理临时文件
        os.unlink(tmp_zip_path)
        import shutil
        shutil.rmtree(extract_dir)
        
        _debug(f"Markdown 内容提取成功，长度: {len(markdown_content)} 字符")
        
        return markdown_content
        
    except Exception as e:
        raise Exception(f"下载或提取 Markdown 失败: {str(e)}")


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
