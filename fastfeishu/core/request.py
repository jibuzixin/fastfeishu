from typing import Union, Dict, Any, List, Tuple
import os, re, json, requests
from typing import Union
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

from requests import Response

from fastfeishu.configs.settings import get_feishu_property
from fastfeishu.models.type import Formula
from fastfeishu.utils.little_utils import base64_image
from fastfeishu.exceptions.exception import FeiShuException
from fastfeishu.models.feishu_var import FeishuVariable
from datetime import datetime
from decimal import Decimal
import math

load_dotenv()
feishu_property = get_feishu_property().feishu  # 读取配置文件

class FeiShuRequest:
    link = FeishuVariable(str, readonly_after_first_set=True)  # 保证初始化
    sheet_token = FeishuVariable(str, readonly_after_first_set=True)  # 保证初始化
    sheet_id = FeishuVariable(str, readonly_after_first_set=True)  # 保证初始化
    base_url = feishu_property.links.baseUrl
    link_auth = feishu_property.links.auth
    link_media = feishu_property.links.media
    link_sheets = feishu_property.links.sheets
    link_workBook = feishu_property.links.workBook

    def __init__(self, link: str):
        self.tat = self.get_tenant_token()
        self.set_link(link)

    def get_tenant_token(self):
        """获取tenant_access_token"""
        tat = ""
        url = os.path.join(
            self.base_url, self.link_auth.tenantToken.format().human_repr()
        )
        post_data = {
            "app_id": os.getenv("FS_APP_ID"),
            "app_secret": os.getenv("FS_APP_SECRET"),
        }
        try:
            r = requests.post(url, data=post_data)
            tat = r.json()["tenant_access_token"]
        except Exception as e:
            raise FeiShuException("Error happened when get tat token: %s" % e)
        return tat

    def set_link(self, link: str):
        self.link = link
        token, sheet_id = FeiShuRequest.parse_feishu_url(link)
        if not token:
            raise FeiShuException(
                f"请检查飞书链接是否正确，解析失败！无法提取 sheet_token"
            )
        self.sheet_token = token
        if sheet_id is None:
            sheet_id: str = self.get_sheet_metadata()["data"]["sheets"][0]["sheetId"]
        self.sheet_id = sheet_id
        
    def _get_request_headers(self) -> dict:
        """返回请求头"""
        return {
            "content-type": "application/json; charset=utf-8",
            "Authorization": "Bearer " + str(self.tat),
        }
    
    def _build_url(self, link_cfg: str):
        u = '/'.join([self.base_url, link_cfg,]).replace('//', '/')
        return u.replace(':/', '://')

    def get_sheet_metadata(self) -> Dict[str, Any]:
        url = self._build_url(
            self.link_sheets.metainfo
            .format(SHEET_TOKEN=self.sheet_token)
            .human_repr()
        )
        response = requests.get(url, headers=self._get_request_headers())
        response.raise_for_status()
        return response.json()

    def get_sheet_info(self) -> Response:
        url = self._build_url(
            self.link_sheets.metainfo
            .format(SHEET_TOKEN=self.sheet_token)
            .human_repr()
        )
        response = requests.get(url, headers=self._get_request_headers())
        response.raise_for_status()
        return response

    def read(
            self,
            sheet_range: str,
            value_render_option: str="ToString",
            date_time_render_option: str="FormattedString"
    ) -> requests.Response:
        """
        [读取单个范围](https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/reading-a-single-range)

        Args:
            sheet_range: 读取表格的范围: 'A2:BC10'
            value_render_option: 指定单元格数据的格式。可选值如下所示。当参数缺省时，默认不进行公式计算，返回公式本身，且单元格为数值格式。

                - ToString：返回纯文本的值（数值类型除外）
                - Formula：单元格中含有公式时，返回公式本身
                - FormattedValue：计算并格式化单元格
                - UnformattedValue：计算但不对单元格进行格式化
            date_time_render_option: 指定数据类型为日期、时间、或时间日期的单元格数据的格式。

                - 若不传值，默认返回浮点数值，整数部分为自 1899 年 12 月 30 日以来的天数；小数部分为该时间占 24 小时的份额。
                  例如：若时间为 1900 年 1 月 1 日中午 12 点，则默认返回 2.5。
                  其中，2 表示 1900 年 1 月 1 日为 1899 年12 月 30 日之后的 2 天；
                  0.5 表示 12 点占 24 小时的二分之一，即 12/24=0.5。
                - 可选值为 FormattedString，此时接口将计算并对日期、时间、或时间日期类型的数据格式化并返回格式化后的字符串，但不会对数字进行格式化。
        """

        url = self._build_url(
            self.link_sheets.read.format(
                self.sheet_id + "!" + sheet_range.upper(), SHEET_TOKEN=self.sheet_token
            )
            .with_query(
                valueRenderOption=value_render_option, dateTimeRenderOption=date_time_render_option
            )
            .human_repr(),
        )
        response = requests.get(url, headers=self._get_request_headers())
        response.raise_for_status()
        return response

    def read_images(self, sheet_range: str) -> requests.Response:
        """
        [读取单个范围](https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/reading-a-single-range) \n
        读取图片的文本格式：
        ```
        {
            'fileToken': 'IHrBbu5poo3Kfxx9Kr0cHIUdnsh',
            'height': 232,
            'link': 'https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/v2/cover/IHrBbu5poo3Kfxx9Kr0cHIUdnsh/?height=1280&mount_node_token=MifosrRX4h6dJotK3gEc1OJun0f&mount_point=sheet_image&policy=equal&width=1280',
            'text': '',
            'type': 'embed-image',
            'width': 217
        }
        ```
        可以使用 download_image_* 方法传入 fileToken 下载图片。

        :param sheet_range: 读取表格的范围: 'A2:BC10'
        """

        url = self._build_url(
            self.link_sheets.read.format(
                self.sheet_id + "!" + sheet_range.upper(), SHEET_TOKEN=self.sheet_token
            ).human_repr(),
        )
        response = requests.get(url, headers=self._get_request_headers())
        response.raise_for_status()
        return response

    def insert(self, sheet_range: str, data_list: List[List]) -> requests.Response:
        """
        [插入数据](https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/prepend-data)

        在电子表格工作表的指定范围的起始位置上方增加若干行，并在该范围中填充数据。
        """
        
        url = self._build_url(
            self.link_sheets.insert.format(SHEET_TOKEN=self.sheet_token).human_repr(),
        )
        body = {
            "valueRange": {
                "range": self.sheet_id + "!" + sheet_range.upper(),
                "values": data_list,
            }
        }
        response = requests.post(url, headers=self._get_request_headers(), data=json.dumps(body))
        response.raise_for_status()
        return response

    def write(self, sheet_range: str, data_list: List[List[Any]]) -> requests.Response:
        """
        [向单个范围写入数据](https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/write-data-to-a-single-range)

        单次写入数据不得超过 5000 行、100列。
        每个单元格不超过 50,000 字符，由于服务端会增加控制字符，因此推荐每个单元格不超过 40,000 字符。

        :param sheet_range: 示例: 'A2:B5', 'ad10:ad100', 'd3:d12'
        :param data_list: 二维数组，数组元素表示行数据。如： [[1,2,3], [4,5,6]] 表示写入的第一行数据为 1,2,3 ... ... 没有数据填 None
        """
        def _default(o):
            if isinstance(o, float) and math.isnan(o):
                return None
            if isinstance(o, (datetime, Decimal, bool)):
                return str(o)
            raise TypeError(f"对象类型：[ {type(o).__name__} ] 不是一个可 JSON 序列化的，写入失败")

        for r, row in enumerate(data_list):
            for c, item in enumerate(row):
                if isinstance(item, float) and math.isnan(item):
                    data_list[r][c] = None
                elif item is None or isinstance(item, (int, float, bool)):
                    continue
                elif isinstance(item, str):  # 公式
                    if item.startswith("="):
                        data_list[r][c] = Formula(item).to_json()
                    else:
                        continue
                else:
                    data_list[r][c] = json.dumps(item, default=_default, ensure_ascii=False)
        
        url = self._build_url(
            self.link_sheets.write.format(SHEET_TOKEN=self.sheet_token).human_repr(),
        )
        body = {
            "valueRange": {
                "range": self.sheet_id + "!" + sheet_range.upper(),
                "values": data_list,
            }
        }
        response = requests.put(url, headers=self._get_request_headers(), data=json.dumps(body))
        response.raise_for_status()
        return response

    def append(
        self, sheet_range: str, data_list: List[List[Any]], insert_data_option="OVERWRITE",
    ) -> requests.Response:
        """
        [追加数据](https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/append-data)
        在电子表格工作表的指定范围中，在空白位置中追加数据。例如，若指定范围参数 range 为 6e5ed3!A1:B2，
        该接口将会依次寻找 A1、A2、A3...单元格，在找到的第一个空白位置中写入数据。

        :param sheet_range: 示例: 'A2:B5', 'ad10:ad100', 'd3:d12'
        :param data_list: 要写入的二维数组，外层数组元素代表行，内层数组元素代表列。[[1,2,3]] 将会写入一行数据，按顺序写入 1、2、3
        :param insert_data_option:
            指定追加数据的方式，默认值为 OVERWRITE ，即若空行数量小于追加数据的行数，则会覆盖已有数据。可选值：

            - OVERWRITE ：若空行的数量小于追加数据的行数，则会覆盖已有数据

            - INSERT_ROWS ：插入足够数量的行后再进行数据追加
        """
        
        url = self._build_url(
            self.link_sheets.append.format(SHEET_TOKEN=self.sheet_token)
            .with_query(insertDataOption=insert_data_option)
            .human_repr(),
        )
        body = {
            "valueRange": {
                "range": self.sheet_id + "!" + sheet_range.upper(),
                "values": data_list,
            }
        }
        response = requests.post(url, headers=self._get_request_headers(), data=json.dumps(body))
        response.raise_for_status()
        return response

    # def create_work(self, title: str, folder_token: str) -> requests.Response:
    #     """
    #     [创建电子表格](https://open.feishu.cn/document/server-docs/docs/sheets-v3/spreadsheet/create)

    #     :param title: 说明
    #     :param folder_token: 说明
    #     """
        
    #     url = "https://open.feishu.cn/open-apis/sheets/v3/spreadsheets"
    #     body = {"title": title, "folder_token": folder_token}
    #     response = requests.post(url, headers=self._get_request_headers(), data=json.dumps(body))
    #     return self._response_or_json(response)

    def create_sheet(self, title: str, index: int=0) -> requests.Response:
        """
        [操作工作表-创建sheet](https://open.feishu.cn/document/server-docs/docs/sheets-v3/spreadsheet-sheet/operate-sheets) \n
        在当前 Excel 在线文档中创建一个新的 sheet 。 \n

        :param title: 新 sheet 的名称
        :param index: 新 sheet 在表中的索引位置，默认为 0 第一个
        """
        
        url = self._build_url(
            self.link_sheets.sheetsBatchUpdate.format(SHEET_TOKEN=self.sheet_token).human_repr(),
        )
        body = {
            "requests": {"addSheet": {"properties": {"title": title, "index": index}}}
        }
        response = requests.post(url, headers=self._get_request_headers(), data=json.dumps(body))
        response.raise_for_status()
        return response

    def copy_sheet(self, title: str) -> requests.Response:
        """
        [操作工作表-复制sheet](https://open.feishu.cn/document/server-docs/docs/sheets-v3/spreadsheet-sheet/operate-sheets) \n

        :param title: 新 sheet 的名称
        :param index: 新 sheet 在表中的索引位置，默认为 0 第一个
        """

        url = self._build_url(
            self.link_sheets.sheetsBatchUpdate.format(SHEET_TOKEN=self.sheet_token).human_repr(),
        )
        body = {
            "requests": [
                {
                    "copySheet": {
                        "source": {"sheetId": self.sheet_id},
                        "destination": {"title": title}
                    }
                }
            ]
        }
        response = requests.post(url, headers=self._get_request_headers(), data=json.dumps(body))
        response.raise_for_status()
        return response

    def delete_series(
        self, start_index, end_index, major_dimension="ROWS"
    ) -> Dict | requests.Response:
        """
        [删除行或者列](https://open.feishu.cn/document/server-docs/docs/sheets-v3/sheet-rowcol/-delete-rows-or-columns)

        :param start_index:

            要删除的行或列的起始位置，从 1 开始计数。若 startIndex 为 3 ，则从第 3 行或列开始删除。包含第 3 行或列。
        :param end_index:

            要删除的行或列结束的位置。从 1 开始计数。若 endIndex 为 7 ，则删除至第 7 行或列结束。包含第 7 行或列。

            示例：当 majorDimension 为 ROWS、 startIndex 为 3、endIndex 为 7 时，则删除第 3、4、5、6、7 行的数据，共删除 5 行.
        :param major_dimension: 说明
        """
        
        url = self._build_url(
            self.link_sheets.deleteSeries.format(SHEET_TOKEN=self.sheet_token).human_repr(),
        )
        body = {
            "dimension": {
                "sheetId": self.sheet_id,
                "majorDimension": major_dimension.upper(),
                "startIndex": start_index,
                "endIndex": end_index,
            }
        }
        response = requests.delete(url, headers=self._get_request_headers(), data=json.dumps(body))
        response.raise_for_status()
        return response

    def append_series(
        self, add_count: int, major_dimension="ROWS"
    ):
        """
        [增加行列](https://open.feishu.cn/document/server-docs/docs/sheets-v3/sheet-rowcol/add-rows-or-columns)
        :param add_count: 要增加的行列数
        :param major_dimension: ROWS 或 COLUMNS ，默认 ROWS
        """
        url = self._build_url(
            self.link_sheets.appendSeries.format(SHEET_TOKEN=self.sheet_token).human_repr(),
        )
        body = {
            "dimension": {
                "sheetId": self.sheet_id,
                "majorDimension": major_dimension.upper(),
                "length": add_count,
            }
        }
        response = requests.post(url, headers=self._get_request_headers(), data=json.dumps(body))
        response.raise_for_status()
        return response

    def write_image(
        self, cell: str, image: Union[str, bytes], image_name: str = "cell.png"
    ) -> requests.Response:
        """
        [写入图片](https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/write-images)
        
        :param cell: 示例: 'a2', 'B33', 'df56'
        :param image: 可传入一个本地图片的路径或者已经加载好的二进制数据
        :param image_name: 图片名称
        """

        url = self._build_url(
            self.link_sheets.writeImage
            .format(SHEET_TOKEN=self.sheet_token)
            .human_repr(),
        )
        body = {
            "range": f"{self.sheet_id}!{cell.upper()}:{cell.upper()}",  # 开始结束必须一致
            "image": base64_image(image),
            "name": image_name,
        }
        response = requests.post(url, data=json.dumps(body), headers=self._get_request_headers())
        response.raise_for_status()
        return response

    def download_media_raw(
        self,
        file_token: str,
        *,
        extra: str | None = None,
        chunk_size: int = 8192,
        timeout: int = 30,
    ) -> bytes:
        """所有下载方法的底层实现.[文档](https://open.feishu.cn/document/server-docs/docs/drive-v1/media/download)"""
        image_down_url = self.link_media.imageDownload.format(FILE_TOKEN=file_token)
        if extra:
            image_down_url = image_down_url.with_query(extra=extra)

        url = self._build_url(image_down_url.human_repr())
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {self.tat}"},
            stream=True,
            timeout=timeout,
        )
        response.raise_for_status()

        chunks = [
            chunk for chunk in response.iter_content(chunk_size=chunk_size) if chunk
        ]
        return b"".join(chunks)

    def get_media_content_type(
        self,
        file_token: str,
    ):
        """发送一个头请求，获取资源类型"""
        return requests.head(
            str(self.link_media.download.get_url(FILE_TOKEN=file_token)),
            headers={"Authorization": f"Bearer {self.tat}"},
        ).headers.get("content-type", "")

    @staticmethod
    def parse_feishu_url(url: str) -> Tuple[str, str] | Tuple[None, None]:
        if not url or not isinstance(url, str):
            return None, None

        match = re.search(r"/(sheets|wiki)/([a-zA-Z0-9]+)", url)
        sheet_token = match.group(2) if match else None

        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        sheet_id = query_params.get("sheet", [None])[0]

        return sheet_token, sheet_id

    # -------------------------------------- 设置样式 ----------------------------------------------
    def set_style(self, sheet_range: str, style: dict[str, Any]) -> requests.Response:
        """[设置单元格样式](https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/set-cell-style)"""
        url = self._build_url(
            self.link_sheets.style.format(SHEET_TOKEN=self.sheet_token).human_repr(),
        )
        body = {
            "appendStyle": {
                "range": self.sheet_id + '!' + sheet_range.upper(),
                "style": style,
            }
        }
        response = requests.put(url, headers=self._get_request_headers(), data=json.dumps(body))
        response.raise_for_status()
        return response