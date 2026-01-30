from typing import List


class FeiShuException(Exception):
    """飞书异常"""
    def __init__(self, message="飞书异常"):
        super().__init__(message)

class FeiShuRequestException(FeiShuException):
    """飞书 API 发送请求异常"""
    def __init__(self, message):
        super().__init__(message)

class FeiShuColumnNotExist(FeiShuException):
    """飞书列不存在"""
    def __init__(self, column_name: str | List[str], message="飞书列不存在"):
        super().__init__(f"[{column_name}] {message}")