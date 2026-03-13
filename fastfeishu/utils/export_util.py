"""
飞书云文档导出工具类

提供便捷的文档导出功能，支持一步到位的导出操作。
"""
import time
import os
import requests
import json
from typing import Optional, Literal, Union
from pathlib import Path

from fastfeishu.core.request import FeiShuRequest
from fastfeishu.configs.settings import get_feishu_property
from fastfeishu.models.export_task import (
    ExportTaskRequest,
    ExportTaskResult,
    ExportDocType,
    ExportFileExtension,
    ExportJobStatus
)
from fastfeishu.exceptions.exception import (
    FeiShuException,
    FeiShuExportException,
    FeiShuExportTaskFailedException,
    FeiShuExportTimeoutException
)

# 读取配置文件
feishu_property = get_feishu_property().feishu


class _LightweightAuth:
    """
    轻量级认证类

    只负责获取和管理 tenant_access_token，不依赖完整的 FeiShuRequest。
    专门为导出功能设计，避免不必要的依赖。
    """

    def __init__(self):
        """初始化并获取 tenant_access_token"""
        self.base_url = feishu_property.links.baseUrl
        self.link_auth = feishu_property.links.auth
        self.link_export = feishu_property.links.export
        self.tat = self._get_tenant_token()

    def _get_tenant_token(self) -> str:
        """
        获取 tenant_access_token

        Returns:
            str: tenant_access_token

        Raises:
            ValueError: 环境变量未设置
            FeiShuException: 获取 token 失败
        """
        if os.getenv("FS_APP_ID") is None or os.getenv("FS_APP_SECRET") is None:
            raise ValueError(
                "请设置飞书必要的环境变量：FS_APP_ID 和 FS_APP_SECRET"
            )

        url = os.path.join(
            self.base_url,
            self.link_auth.tenantToken.format().human_repr()
        )

        post_data = {
            "app_id": os.getenv("FS_APP_ID"),
            "app_secret": os.getenv("FS_APP_SECRET"),
        }

        try:
            r = requests.post(url, data=post_data)
            return r.json()["tenant_access_token"]
        except Exception as e:
            raise FeiShuException(f"获取 tenant_access_token 失败: {e}")

    def get_request_headers(self) -> dict:
        """
        返回带认证的请求头

        Returns:
            dict: 包含 Authorization 的请求头
        """
        return {
            "content-type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {self.tat}",
        }

    def _build_url(self, link_cfg: str) -> str:
        """构建完整的 API URL"""
        u = '/'.join([self.base_url, link_cfg]).replace('//', '/')
        return u.replace(':/', '://')


class FeiShuExportUtil:
    """飞书云文档导出工具类"""

    def __init__(self, auth: Optional[Union[FeiShuRequest, _LightweightAuth]] = None):
        """
        初始化导出工具

        Args:
            auth: 认证对象，可以是 FeiShuRequest 或 _LightweightAuth 实例
                 如果不传，则在调用方法时会自动创建轻量级认证
        """
        self.auth = auth
        self._headers = None
        self._base_url = None
        self._link_export = None

    def _ensure_auth(self):
        """确保已经初始化认证"""
        if self.auth is None:
            self.auth = _LightweightAuth()

        # 设置请求头和 URL
        if isinstance(self.auth, FeiShuRequest):
            self._headers = self.auth._get_request_headers()
            self._base_url = self.auth.base_url
            self._link_export = self.auth.link_export
        elif isinstance(self.auth, _LightweightAuth):
            self._headers = self.auth.get_request_headers()
            self._base_url = self.auth.base_url
            self._link_export = self.auth.link_export
        else:
            raise FeiShuExportException(
                "auth 必须是 FeiShuRequest 或 _LightweightAuth 实例"
            )

    def _build_url(self, link_cfg: str) -> str:
        """构建完整的 API URL"""
        u = '/'.join([self._base_url, link_cfg]).replace('//', '/')
        return u.replace(':/', '://')

    @staticmethod
    def create_export_util_with_auth() -> "FeiShuExportUtil":
        """
        创建一个带有认证的导出工具实例

        该方法会自动获取 tenant_access_token 用于后续的导出操作。
        需要设置环境变量：FS_APP_ID 和 FS_APP_SECRET

        Returns:
            FeiShuExportUtil: 已认证的导出工具实例

        Example:
            >>> util = FeiShuExportUtil.create_export_util_with_auth()
            >>> # 现在可以使用 util 进行导出操作
        """
        auth = _LightweightAuth()
        return FeiShuExportUtil(auth)

    def export_document(
        self,
        token: str,
        doc_type: Union[ExportDocType, str],
        file_extension: Union[ExportFileExtension, str],
        save_path: Optional[str] = None,
        sub_id: Optional[str] = None,
        max_retry: int = 60,
        retry_interval: float = 2.0
    ) -> Union[bytes, str]:
        """
        一步到位导出云文档

        该方法会自动完成创建导出任务、轮询任务状态、下载文件的完整流程。

        Args:
            token: 要导出的云文档的 token
            doc_type: 云文档类型（doc/sheet/bitable/docx）
            file_extension: 导出文件扩展名（docx/pdf/xlsx/csv）
            save_path: 保存文件的路径，如果为 None 则返回字节流
            sub_id: 导出电子表格或多维表格为 CSV 时需要传入的子表 ID
            max_retry: 最大轮询次数，默认 60 次
            retry_interval: 轮询间隔时间（秒），默认 2 秒

        Returns:
            Union[bytes, str]:
                - 如果指定了 save_path，返回保存的文件路径
                - 如果未指定 save_path，返回文件的字节流

        Raises:
            FeiShuExportTaskFailedException: 导出任务失败
            FeiShuExportTimeoutException: 导出任务超时
            FeiShuExportException: 其他导出异常

        Example:
            >>> util = FeiShuExportUtil.create_export_util_with_auth()
            >>>
            >>> # 保存到本地文件
            >>> file_path = util.export_document(
            ...     token="doxcnxxxxxx",
            ...     doc_type="docx",
            ...     file_extension="pdf",
            ...     save_path="./output.pdf"
            ... )
            >>>
            >>> # 返回字节流
            >>> content = util.export_document(
            ...     token="doxcnxxxxxx",
            ...     doc_type="docx",
            ...     file_extension="pdf"
            ... )
            >>> # 自行处理字节流
            >>> with open("my_file.pdf", "wb") as f:
            ...     f.write(content)
        """
        # 步骤 1: 创建导出任务
        ticket = self.create_export_task_simple(
            token=token,
            doc_type=doc_type,
            file_extension=file_extension,
            sub_id=sub_id
        )

        # 步骤 2: 轮询任务结果
        result = self.poll_export_task_result(
            ticket=ticket,
            token=token,
            max_retry=max_retry,
            retry_interval=retry_interval
        )

        # 步骤 3: 下载文件
        file_content = self.download_export_file_simple(result.file_token)

        # 步骤 4: 保存或返回
        if save_path:
            # 保存到本地文件
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(file_content)
            return str(save_path.absolute())
        else:
            # 返回字节流
            return file_content

    def create_export_task_simple(
        self,
        token: str,
        doc_type: Union[ExportDocType, str],
        file_extension: Union[ExportFileExtension, str],
        sub_id: Optional[str] = None
    ) -> str:
        """
        创建导出任务（简化版）

        Args:
            token: 要导出的云文档的 token
            doc_type: 云文档类型
            file_extension: 导出文件扩展名
            sub_id: 子表 ID（CSV 导出时需要）

        Returns:
            str: 导出任务 ID (ticket)

        Example:
            >>> util = FeiShuExportUtil.create_export_util_with_auth()
            >>> ticket = util.create_export_task_simple(
            ...     token="doxcnxxxxxx",
            ...     doc_type="docx",
            ...     file_extension="pdf"
            ... )
        """
        self._ensure_auth()

        # 转换为字符串类型
        doc_type_str = doc_type if isinstance(doc_type, str) else doc_type.value
        file_ext_str = file_extension if isinstance(file_extension, str) else file_extension.value

        # 构建 URL
        url = self._build_url(
            self._link_export.createTask.format().human_repr()
        )

        # 构建请求体
        body = {
            "file_extension": file_ext_str,
            "token": token,
            "type": doc_type_str
        }
        if sub_id:
            body["sub_id"] = sub_id

        # 发送请求
        response = requests.post(
            url,
            headers=self._headers,
            data=json.dumps(body)
        )
        response.raise_for_status()

        # 解析响应
        result = response.json()
        if result.get("code") != 0:
            raise FeiShuExportException(f"创建导出任务失败: {result.get('msg')}")

        return result["data"]["ticket"]

    def get_export_task_result_simple(
        self,
        ticket: str,
        token: str
    ) -> ExportTaskResult:
        """
        查询导出任务结果（简化版）

        Args:
            ticket: 导出任务 ID
            token: 云文档 token

        Returns:
            ExportTaskResult: 导出任务结果对象

        Example:
            >>> util = FeiShuExportUtil.create_export_util_with_auth()
            >>> result = util.get_export_task_result_simple(
            ...     ticket="6933093124755423251",
            ...     token="doxcnxxxxxx"
            ... )
            >>> if result.is_success:
            ...     print(f"导出成功: {result.file_name}")
        """
        self._ensure_auth()

        # 构建 URL
        url = self._build_url(
            self._link_export.getTaskResult
            .format(TICKET=ticket)
            .with_query(token=token)
            .human_repr()
        )

        # 发送请求
        response = requests.get(url, headers=self._headers)
        response.raise_for_status()

        # 解析响应
        result = response.json()
        if result.get("code") != 0:
            raise FeiShuExportException(f"查询导出任务失败: {result.get('msg')}")

        return ExportTaskResult(result["data"]["result"])

    def poll_export_task_result(
        self,
        ticket: str,
        token: str,
        max_retry: int = 60,
        retry_interval: float = 2.0
    ) -> ExportTaskResult:
        """
        轮询导出任务结果直到完成

        Args:
            ticket: 导出任务 ID
            token: 云文档 token
            max_retry: 最大轮询次数
            retry_interval: 轮询间隔（秒）

        Returns:
            ExportTaskResult: 导出任务结果对象

        Raises:
            FeiShuExportTaskFailedException: 导出任务失败
            FeiShuExportTimeoutException: 轮询超时

        Example:
            >>> util = FeiShuExportUtil.create_export_util_with_auth()
            >>> result = util.poll_export_task_result(
            ...     ticket="6933093124755423251",
            ...     token="doxcnxxxxxx",
            ...     max_retry=30
            ... )
        """
        for i in range(max_retry):
            result = self.get_export_task_result_simple(ticket, token)

            if result.is_success:
                return result
            elif result.is_failed:
                raise FeiShuExportTaskFailedException(
                    job_status=result.job_status,
                    error_msg=result.job_error_msg
                )

            # 继续轮询
            time.sleep(retry_interval)

        # 超时
        raise FeiShuExportTimeoutException(
            f"导出任务查询超时（已重试 {max_retry} 次）"
        )

    def download_export_file_simple(
        self,
        file_token: str
    ) -> bytes:
        """
        下载导出文件（简化版）

        Args:
            file_token: 导出文件的 token

        Returns:
            bytes: 文件的字节流

        Example:
            >>> util = FeiShuExportUtil.create_export_util_with_auth()
            >>> content = util.download_export_file_simple(
            ...     file_token="boxcnxe5OdjlAkNgSNdsJvabcef"
            ... )
            >>> with open("output.pdf", "wb") as f:
            ...     f.write(content)
        """
        self._ensure_auth()

        # 构建 URL
        url = self._build_url(
            self._link_export.downloadFile
            .format(FILE_TOKEN=file_token)
            .human_repr()
        )

        # 发送请求
        response = requests.get(url, headers=self._headers)
        response.raise_for_status()

        return response.content


# 便捷函数：直接导出文档
def export_document(
    token: str,
    doc_type: Union[ExportDocType, str],
    file_extension: Union[ExportFileExtension, str],
    save_path: Optional[str] = None,
    sub_id: Optional[str] = None,
    max_retry: int = 60,
    retry_interval: float = 2.0
) -> Union[bytes, str]:
    """
    便捷函数：一步到位导出云文档

    该函数是 FeiShuExportUtil.export_document 的便捷封装，自动处理认证。

    Args:
        token: 要导出的云文档的 token
        doc_type: 云文档类型（doc/sheet/bitable/docx）
        file_extension: 导出文件扩展名（docx/pdf/xlsx/csv）
        save_path: 保存文件的路径，如果为 None 则返回字节流
        sub_id: 导出电子表格或多维表格为 CSV 时需要传入的子表 ID
        max_retry: 最大轮询次数，默认 60 次
        retry_interval: 轮询间隔时间（秒），默认 2 秒

    Returns:
        Union[bytes, str]:
            - 如果指定了 save_path，返回保存的文件路径
            - 如果未指定 save_path，返回文件的字节流

    Example:
        >>> from fastfeishu.utils.export_util import export_document
        >>>
        >>> # 保存到本地文件
        >>> file_path = export_document(
        ...     token="doxcnxxxxxx",
        ...     doc_type="docx",
        ...     file_extension="pdf",
        ...     save_path="./output.pdf"
        ... )
        >>>
        >>> # 返回字节流
        >>> content = export_document(
        ...     token="doxcnxxxxxx",
        ...     doc_type="docx",
        ...     file_extension="pdf"
        ... )
    """
    util = FeiShuExportUtil.create_export_util_with_auth()
    return util.export_document(
        token=token,
        doc_type=doc_type,
        file_extension=file_extension,
        save_path=save_path,
        sub_id=sub_id,
        max_retry=max_retry,
        retry_interval=retry_interval
    )
