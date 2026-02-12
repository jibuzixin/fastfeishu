import asyncio
import aiohttp
import time
import os
from typing import List, Optional, Tuple, Literal, Dict, Any, Union
import logging
import random
import json

# 导入纯工具函数（避免循环依赖）
from fastfeishu.helpers import (
    match_row_num_by_range,
    match_col_letter_by_range,
    num_to_excel_col,
    excel_col_to_num,
    base64_image,
    extract_json_content
)

# 配置日志（可选，也可以外部传入 logger）
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def sample_from_array(labels_array, label_config=None, max_samples=None):
    """
    根据提供的标签数组、标签配置和最大采样数进行随机抽取。

    :param labels_array: 一维列表，包含字符串标签，如 ['[安全]', '[涉政]', '[安全]']
    :param label_config: 可以是 None（随机抽取总个数，不按标签分组）、字典 {标签: 数量}（为指定标签抽取最多指定数量的索引）、
                         或空字典 {}（针对所有独特标签，每种抽取最多 max_samples 个，默认1如果 max_samples 为 None）。
    :param max_samples: 可以是 None 或整数，用于 label_config 为 None 时（总随机抽取个数，默认1）、
                        或 label_config 为 {} 时（每标签最大抽取个数，默认1）。
    :return: 字典，键为标签，值为对应的索引列表（即使只有一个，也用列表形式以保持一致）。

    示例使用:
    >>> labels = ['[安全]', '[涉政]', '[安全]', '[涉政]', '[其他]']
    
    # 随机抽取1个（两者均为 None）
    >>> sample_from_array(labels)
    {'[安全]': [0]}  # 输出示例，实际随机
    
    # 随机抽取3个总个数，不按标签分组
    >>> sample_from_array(labels, label_config=None, max_samples=3)
    {'[安全]': [2], '[涉政]': [1, 3]}  # 输出示例，实际随机
    
    # 按指定字典抽取
    >>> sample_from_array(labels, label_config={'[安全]': 2, '[涉政]': 1})
    {'[安全]': [0, 2], '[涉政]': [3]}  # 输出示例，实际随机
    
    # 针对所有独特标签，每种抽取最多2个
    >>> sample_from_array(labels, label_config={}, max_samples=2)
    {'[安全]': [0, 2], '[涉政]': [1, 3], '[其他]': [4]}  # 输出示例，实际随机
    """
    result = {}
    
    if label_config is None:
        result = []
        # 随机抽取总个数，不按标签分组
        count = max_samples if max_samples is not None else 1
        if count <= 0 or not labels_array:
            return {}
        k = min(count, len(labels_array))
        indices = random.sample(range(len(labels_array)), k)
        for idx in indices:
            label = labels_array[idx]
            result.append(label)
        return result
    elif isinstance(label_config, dict):
        if len(label_config) == 0:
            # 针对所有独特标签，每种抽取最多 max_samples 个
            unique_labels = set(labels_array)
            count = max_samples if max_samples is not None else 1
            label_config = {label: count for label in unique_labels}
        # 按字典指定标签和数量抽取
        for label, count in label_config.items():
            indices = [i for i, x in enumerate(labels_array) if x == label]
            if indices:
                k = min(len(indices), count)
                sampled_indices = random.sample(indices, k)
                result[label] = sampled_indices
    else:
        raise ValueError("label_config must be None or dict")
    
    # 对每个标签的索引列表排序，以保持一致性
    for label in result:
        result[label].sort()
    
    return result


def get_real_extension_from_bytes(data: bytes) -> str:
    """
    通过魔数前几个字节判断真实图片格式（零依赖方案）
    """
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data.startswith(b"\x47\x49\x46\x38"):
        return ".gif"
    if data.startswith(b"\x52\x49\x46\x46") and b"WEBP" in data[8:12]:
        return ".webp"
    if len(data) >= 12 and data[4:12] in (b"ftypheic", b"ftypheix", b"ftypmif1", b"ftypmsf1"):
        return ".heic"
    if len(data) >= 12 and data[4:12] == b"ftypavif":
        return ".avif"
    if data.startswith(b"BM"):
        return ".bmp"
    if data.startswith((b"\x49\x49\x2A\x00", b"\x4D\x4D\x00\x2A")):
        return ".tiff"
    return ".jpg"  # 默认

async def _download_image(session: aiohttp.ClientSession,
                          url: str,
                          semaphore: asyncio.Semaphore) -> Tuple[bool, str, Optional[bytes], str]:
    """
    单个图片下载协程
    返回: (success, msg, content, real_ext)
    """
    async with semaphore:  # 控制并发 QPS
        try:
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    content = await response.read()
                    real_ext = get_real_extension_from_bytes(content)
                    return True, url, content, real_ext
                else:
                    return False, f"{url} HTTP {response.status}", None, ""
        except Exception as e:
            return False, f"{url} Exception: {str(e)}", None, ""
        finally:
            # 简单 QPS 控制（更精确可使用 token bucket）
            await asyncio.sleep(0.01)  # 可配合 semaphore 精细控制

async def batch_download_images(
    urls: List[str],
    qps: int = 10,
    save_dir: Optional[str] = None,
    return_type: Literal["success", "binary", "both"] = "both",
    failed_log_path: str = "download_failed.json",
    filename_template: str = "{index}_{timestamp}_{name}",
    headers: Optional[Dict[str, str]] = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    批量下载图片函数-异步
    
    Args:
        urls: 图片URL列表
        qps: 每秒请求数限制（最大并发数）
        save_dir: 保存目录，为None时不保存到本地
        return_type: 
            "success"  -> 只返回成功/失败状态
            "binary"   -> 只返回二进制内容（适合直接上传云端）
            "both"     -> 返回状态 + 二进制（推荐）
        failed_log_path: 失败日志保存路径（json格式）
        filename_template: 文件命名模板，支持 {index}, {timestamp}, {name}
        headers: 自定义请求头（如需要referer、user-agent等）
    
    Returns:
        success_list: 成功下载的列表
        failed_list: 失败的列表（会自动写入 failed_log_path）
    """
    if return_type in ["success", "both"] and save_dir and not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    semaphore = asyncio.Semaphore(qps)
    timeout = aiohttp.ClientTimeout(total=60)
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    if headers:
        default_headers.update(headers)
    
    connector = aiohttp.TCPConnector(limit=qps * 2, limit_per_host=10)
    async with aiohttp.ClientSession(headers=default_headers, timeout=timeout, connector=connector) as session:
        tasks = []
        for idx, url in enumerate(urls):
            task = _download_image(session, url, semaphore)
            tasks.append((idx, url, task))
        
        success_list = []
        failed_list = []
        
        # 并发执行所有任务
        for idx, url, task in tasks:
            success, msg, content, real_ext = await task
            
            # 生成文件名
            original_filename = os.path.basename(url.split('?')[0].split('#')[0])
            name_without_ext = os.path.splitext(original_filename)[0] or f"image_{idx}"
            safe_name = "".join(c for c in name_without_ext if c.isalnum() or c in "._-")
            timestamp = int(time.time() * 1000)
            filename = filename_template.format(
                index=idx,
                timestamp=timestamp,
                name=safe_name
            ) + real_ext if real_ext else filename_template.format(
                index=idx,
                timestamp=timestamp,
                name=safe_name
            ) + ".jpg"
            
            save_path = os.path.join(save_dir, filename) if save_dir else None
            
            result = {
                "index": idx,
                "url": url,
                "filename": filename,
                "save_path": save_path,
                "timestamp": int(time.time()),
            }
            
            if success:
                if return_type in ['success', 'both'] and save_dir and content:
                    with open(save_path, 'wb') as f:
                        f.write(content)
                if return_type in ["binary", "both"]:
                    result["data"] = content  # 二进制数据（内存中）
                success_list.append(result)
                logger.info(f"√ 下载成功: {url} (格式: {real_ext})")
            else:
                result["error"] = msg
                failed_list.append(result)
                logger.error(f"× 下载失败: {msg}")
        
        # 保存失败日志（可用于重试）
        if failed_list:
            os.makedirs(os.path.dirname(os.path.abspath(failed_log_path)), exist_ok=True)
            with open(failed_log_path, 'w', encoding='utf-8') as f:
                json.dump(failed_list, f, ensure_ascii=False, indent=2)
            logger.info(f"失败记录已保存至: {failed_log_path}（共 {len(failed_list)} 条）")
        
        return success_list, failed_list


# ==================== 使用示例 ====================

# 同步调用入口
def sync_batch_download_images(*args, **kwargs):
    """
    批量下载图片函数-同步

    Args:
        urls: 图片URL列表
        qps: 每秒请求数限制（最大并发数）
        save_dir: 保存目录，为None时不保存到本地
        return_type:
            "success"  -> 只返回成功/失败状态
            "binary"   -> 只返回二进制内容（适合直接上传云端）
            "both"     -> 返回状态 + 二进制（推荐）
        failed_log_path: 失败日志保存路径（json格式）
        filename_template: 文件命名模板，支持 {index}, {timestamp}, {name}
        headers: 自定义请求头（如需要referer、user-agent等）

    Returns:
        success_list: 成功下载的列表
        failed_list: 失败的列表（会自动写入 failed_log_path）
    """
    return asyncio.run(batch_download_images(*args, **kwargs))


def example_json():
    example = "```json\n{\"key\": \"value\"}\n```"
    result = extract_json_content(example)
    print(result)  # Output: {"key": "value"}

async def example_batch_download():
    urls = [
        r"https://ssai-online-data-1.bj.bcebos.com/ssai-tech/ssai-biz03/livis/tars-image-history/20251214/3397113544816640001/5cde147b-daba-430b-ae57-be735c66e307-3?authorization=bce-auth-v1%2FALTAKgz7347Tk617o7HQeoqifH%2F2025-12-14T02%3A57%3A17Z%2F315360000%2Fhost%2Fd59e820974475cc3af1ff99badaaf979b1b82a7a8fd4d96c28f8b9d57c5f26f2",
        r"https://ssai-online-data-1.bj.bcebos.com/ssai-tech/ssai-biz03/livis/tars-image-history/20251212/3913326932869292034/502f06d4-91fe-47e0-b43d-da2682cc9002-0?authorization=bce-auth-v1%2FALTAKgz7347Tk617o7HQeoqifH%2F2025-12-12T11%3A35%3A30Z%2F315360000%2Fhost%2F876a3dbcd2c5e8175600e3249c5c81aa97b5bf1759b7b8b897c936ed5b2ea17c"
    ]
    
    success, failed = await batch_download_images(
        urls=urls,
        qps=5,                              # 每秒最多5个请求
        save_dir="./downloaded_images",      # 保存到本地
        return_type="binary",                  # 返回状态 + 二进制
        failed_log_path="logs/failed_2025.json",
        headers={"Referer": "https://google.com"}  # 防盗链
    )
    
    print(f"成功: {len(success)} 张")
    print(f"失败: {len(failed)} 张")
    
    # 示例：直接上传成功图片到云端（这里仅演示）
    for item in success:
        binary_data = item.get("data")
        if binary_data:
            # upload_to_cloud(binary_data, item["filename"])
            pass

if __name__ == "__main__":
    # asyncio.run(example_batch_download())
    # example_json()
    a, b = match_col_letter_by_range('C22:ab22')
    print(excel_col_to_num(a))
    print(excel_col_to_num(b))