from yarl import URL
from pydantic_settings import BaseSettings

# 注意：每个节点都是 BaseSettings 子类，才能继续被 settings 链加载
class LinkAttribute(BaseSettings):
    url: str

    def format(self, *append_path, **format_kwargs) -> URL:
        """
        获取配置文件对应的 URL \n
        ```python
        get_url("append_1", "append_2", SHEET_TOKEN='*****')
        原 url: 'sheets/v2/spreadsheets/{SHEET_TOKEN}/values'
        打印: 'sheets/v2/spreadsheets/*****/values/append_1/append_2'
        ```

        :param append_path: 可以向路径后追加额外字符串，用 “/” 分割
        :param format_kwargs: 格式化路径中带有 {} 的占位符
        :return: 返回一个 URL 对象，可使用 .with_query 方式添加路径参数
        :rtype: URL
        """
        if append_path:
            url = (self.url.format(**format_kwargs) +'/'+ '/'.join(append_path)).replace('//', '/')
        else:
            url = self.url.format(**format_kwargs)
        return URL(url)

# ----------------------- 链接详细配置 --------------------------
class AuthSettings(BaseSettings):
    """tenant_access_token"""
    target: str
    tenantToken: LinkAttribute

class MediaSettings(BaseSettings):
    """下载图片等媒体素材"""
    target: str
    imageDownload: LinkAttribute

class SheetsSettings(BaseSettings):
    """操作 Sheet 相关"""
    target: str
    metainfo: LinkAttribute
    read: LinkAttribute
    readBatch: LinkAttribute
    insert: LinkAttribute
    write: LinkAttribute
    writeBatch: LinkAttribute
    append: LinkAttribute
    sheetsBatchUpdate: LinkAttribute
    # delete: LinkAttribute
    appendSeries: LinkAttribute
    deleteSeries: LinkAttribute
    insertSeries: LinkAttribute
    writeImage: LinkAttribute
    style: LinkAttribute
    styleBatchUpdate: LinkAttribute

class WorkBookSettings(BaseSettings):
    """控制工作簿"""
    target: str
    create: LinkAttribute

class ExportSettings(BaseSettings):
    """导出云文档"""
    target: str
    createTask: LinkAttribute
    getTaskResult: LinkAttribute
    downloadFile: LinkAttribute

# ------------------------- 链接配置 ----------------------------
class LinksSettings(BaseSettings):
    """所有飞书链接配置"""
    baseUrl: str
    auth: AuthSettings
    media: MediaSettings
    sheets: SheetsSettings
    workBook: WorkBookSettings
    export: ExportSettings

# --------------------------- 根 --------------------------------
class FeishuSettings(BaseSettings):
    links: LinksSettings

    # ===== 自定义业务方法 =====
    def get_url_by_(self, token: str | None = None) -> str:
        # 也可以把 token 当字段传进来，这里演示手动替换
        url = self.links.sheets.read.url
        if token:
            url = url.replace("${SHEET_TOKEN}", token)
        return self.links.baseUrl + url
