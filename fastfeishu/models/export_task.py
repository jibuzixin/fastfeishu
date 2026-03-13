"""
导出任务相关的数据模型
"""
from enum import Enum
from typing import Optional, Literal


class ExportFileExtension(str, Enum):
    """导出文件扩展名"""
    DOCX = "docx"  # Microsoft Word 格式
    PDF = "pdf"    # PDF 格式
    XLSX = "xlsx"  # Microsoft Excel 格式
    CSV = "csv"    # CSV 格式


class ExportDocType(str, Enum):
    """云文档类型"""
    DOC = "doc"        # 旧版飞书文档（已不推荐）
    SHEET = "sheet"    # 飞书电子表格
    BITABLE = "bitable"  # 飞书多维表格
    DOCX = "docx"      # 新版飞书文档


class ExportJobStatus(int, Enum):
    """导出任务状态"""
    SUCCESS = 0              # 成功
    INITIALIZING = 1         # 初始化
    PROCESSING = 2           # 处理中
    INTERNAL_ERROR = 3       # 内部错误
    FILE_TOO_LARGE = 107     # 导出文档过大
    TIMEOUT = 108            # 处理超时
    NO_PERMISSION_BLOCK = 109  # 导出内容块无权限
    NO_PERMISSION = 110      # 无权限
    DOC_DELETED = 111        # 导出文档已删除
    EXPORT_DISABLED_DURING_COPY = 122  # 创建副本中禁止导出
    DOC_NOT_EXIST = 123      # 导出文档不存在
    TOO_MANY_IMAGES = 6000   # 导出文档图片过多


class ExportTaskRequest:
    """创建导出任务的请求参数"""

    def __init__(
        self,
        token: str,
        doc_type: ExportDocType | str,
        file_extension: ExportFileExtension | str,
        sub_id: Optional[str] = None
    ):
        """
        初始化导出任务请求参数

        Args:
            token: 要导出的云文档的 token
            doc_type: 云文档类型（doc/sheet/bitable/docx）
            file_extension: 导出文件扩展名（docx/pdf/xlsx/csv）
            sub_id: 导出电子表格或多维表格为 CSV 时需要传入的子表 ID
        """
        self.token = token
        self.type = doc_type if isinstance(doc_type, str) else doc_type.value
        self.file_extension = file_extension if isinstance(file_extension, str) else file_extension.value
        self.sub_id = sub_id

    def to_dict(self) -> dict:
        """转换为请求字典"""
        data = {
            "file_extension": self.file_extension,
            "token": self.token,
            "type": self.type
        }
        if self.sub_id:
            data["sub_id"] = self.sub_id
        return data


class ExportTaskResult:
    """导出任务结果"""

    def __init__(self, result_data: dict):
        """
        从 API 响应数据初始化

        Args:
            result_data: API 返回的 result 数据
        """
        self.file_extension = result_data.get("file_extension")
        self.type = result_data.get("type")
        self.file_name = result_data.get("file_name")
        self.file_token = result_data.get("file_token")
        self.file_size = result_data.get("file_size", 0)
        self.job_error_msg = result_data.get("job_error_msg", "")
        self.job_status = result_data.get("job_status", ExportJobStatus.INITIALIZING)

    @property
    def is_success(self) -> bool:
        """任务是否成功"""
        return self.job_status == ExportJobStatus.SUCCESS.value

    @property
    def is_processing(self) -> bool:
        """任务是否正在处理中"""
        return self.job_status in [
            ExportJobStatus.INITIALIZING.value,
            ExportJobStatus.PROCESSING.value
        ]

    @property
    def is_failed(self) -> bool:
        """任务是否失败"""
        return not self.is_success and not self.is_processing

    def __repr__(self):
        return (
            f"ExportTaskResult(file_name={self.file_name}, "
            f"job_status={self.job_status}, "
            f"file_size={self.file_size})"
        )
