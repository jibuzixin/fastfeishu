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

class FeiShuStyleException(FeiShuException):
    """飞书样式格式错误异常"""
    def __init__(self, message="飞书样式格式错误"):
        super().__init__(message)

class FeiShuExportException(FeiShuException):
    """飞书导出异常"""
    def __init__(self, message="飞书导出异常"):
        super().__init__(message)

class FeiShuExportTaskFailedException(FeiShuExportException):
    """飞书导出任务失败异常"""
    def __init__(self, job_status: int, error_msg: str):
        message = f"导出任务失败 (状态码: {job_status}): {error_msg}"
        super().__init__(message)
        self.job_status = job_status
        self.error_msg = error_msg

class FeiShuExportTimeoutException(FeiShuExportException):
    """飞书导出任务超时异常"""
    def __init__(self, message="导出任务查询超时"):
        super().__init__(message)
