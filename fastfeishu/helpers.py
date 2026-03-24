"""
纯工具函数模块 - 无任何项目内部依赖

这个模块包含最底层的工具函数，不依赖任何其他项目模块。
可以被 models、core、utils 等任何层级安全导入。
"""

import re
import base64
import pandas as pd
from typing import Tuple, Union, Any
import requests
from urllib.parse import unquote


def extract_filename_from_response(response: requests.Response) -> str | None:
    """从响应头中提取文件名"""
    content_disposition = response.headers.get('Content-Disposition')
    if not content_disposition:
        return None

    # 方法1：使用正则表达式提取（更健壮）
    filename_match = re.search(r'filename\*?=["\']?(?:UTF-\d[\'"]*)?([^"\';\s]+)', content_disposition)
    if filename_match:
        filename = filename_match.group(1)
        # 处理可能的URL编码
        filename = unquote(filename)
        return filename
    return None

def cell_is_blank(cell_data: Any) -> bool:
    """判断单元格是否为空、None、nan"""
    if pd.isna(cell_data) or cell_data == '' or cell_data is None:
        return True
    else:
        return False


def match_row_num_by_range(s: str) -> Tuple[str, str]:
    """例如 Ac12:B3 匹配到数字: '12', '3'"""
    pattern = r'(?<=[a-zA-Z])(\d+)'
    matches = re.findall(pattern, s)
    return matches[0], matches[1]


def match_col_letter_by_range(s: str) -> Tuple[str, str]:
    """例如 Ac12:B3 匹配到列索引: 'AC', 'B'"""
    pattern = r'([a-zA-Z]+)\d+:([a-zA-Z]+)\d'
    matches = re.findall(pattern, s)
    for match in matches:
        return str(match[0]).upper(), str(match[1]).upper()


def num_to_excel_col(n: int) -> str:
    """
    将 1-based 列号转成 Excel 列字母
    例如 1 -> 'A', 26 -> 'Z', 27 -> 'AA', 702 -> 'ZZ', 703 -> 'AAA'
    """
    if n <= 0:
        raise ValueError("列号必须 ≥ 1")
    chars = []
    while n > 0:
        n -= 1                 # 关键：先减 1，让 0->A, 25->Z
        chars.append(chr(ord('A') + n % 26))
        n //= 26
    return ''.join(reversed(chars))


def excel_col_to_num(col: str) -> int:
    """
    将 Excel 列字母转成 1-based 列号
    例如 'A' -> 1, 'Z' -> 26, 'AA' -> 27, 'ZZ' -> 702, 'AAA' -> 703
    """
    if not col.isalpha():
        raise ValueError("列名必须是英文字母")
    num = 0
    for char in col.upper():  # 将输入统一转换为大写
        num = num * 26 + (ord(char) - ord('A') + 1)
    return num


def base64_image(path_or_bytes: Union[str, bytes]) -> str:
    """统一转 base64 字符串"""
    if isinstance(path_or_bytes, str):
        with open(path_or_bytes, 'rb') as f:
            data = f.read()
    else:
        data = path_or_bytes
    return base64.b64encode(data).decode('ascii')


def extract_json_content(input_string: str, start_flag: str = '<json>', end_flag: str = '</json>') -> str | None:
    """
    Parses a string wrapped in <json></json> tags and extracts the content inside.

    Args:
        input_string: The input string containing the tags.
        start_flag: Starting tag, default '<json>'
        end_flag: Ending tag, default '</json>'

    Returns:
        The extracted content if tags are found, otherwise None.
    """
    match = re.search(f'{start_flag}(.*?){end_flag}', input_string, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None
