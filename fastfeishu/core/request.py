from typing import Union, Dict, Any, List, Tuple, Literal
import os, re, json, requests
from typing import Union
from urllib.parse import urlparse, parse_qs

from fastfeishu.models import SheetProperties
from requests import Response

from fastfeishu.configs.settings import get_feishu_property
from fastfeishu.models.type import Formula, FeiShuCellType
from fastfeishu.helpers import base64_image, extract_filename_from_response
from fastfeishu.exceptions.exception import FeiShuException
from fastfeishu.models.feishu_var import FeishuVariable
from datetime import datetime
from decimal import Decimal
import math

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
    link_export = feishu_property.links.export

    def __init__(self, link: str):
        self.tat = self.get_tenant_token()
        self.set_link(link)

    def get_tenant_token(self):
        """获取tenant_access_token"""
        if os.getenv("FS_APP_ID") is None or os.getenv("FS_APP_SECRET") is None:
            raise ValueError(f"请设置飞书必要的环境变量：FS_APP_ID 和 FS_APP_SECRET ，如果已设置请检查是否有值")
        url = os.path.join(
            self.base_url, self.link_auth.tenantToken.format().human_repr()
        )
        post_data = {
            "app_id": os.getenv("FS_APP_ID"),
            "app_secret": os.getenv("FS_APP_SECRET"),
        }
        try:
            r = requests.post(url, data=post_data)
            return r.json()["tenant_access_token"]
        except Exception as e:
            raise FeiShuException("Error happened when get tat token: %s" % e)

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

    def read_batch(
            self,
            ranges: List[str],
            value_render_option: str = "ToString",
            date_time_render_option: str = "FormattedString"
    ) -> requests.Response:
        """
        [读取多个范围](https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/reading-multiple-ranges)

        批量读取电子表格中多个指定范围的数据。该接口返回数据的最大限制为 10 MB。

        Args:
            ranges: 多个查询范围的列表，每个元素为形如 'A2:B6' 的范围字符串
                    例如: ['A2:B6', 'D1:E10']
            value_render_option: 指定单元格数据的格式。可选值:
                - ToString：返回纯文本的值（数值类型除外）
                - Formula：单元格中含有公式时，返回公式本身
                - FormattedValue：计算并格式化单元格
                - UnformattedValue：计算但不对单元格进行格式化
            date_time_render_option: 指定日期、时间类型的格式
                - FormattedString：格式化为字符串
                - 默认：返回浮点数（自1899年12月30日以来的天数）

        Returns:
            Response 对象，其 json() 返回的数据结构:
            {
                "code": 0,
                "data": {
                    "revision": 87,
                    "spreadsheetToken": "shtcn...",
                    "totalCells": 6,
                    "valueRanges": [
                        {
                            "majorDimension": "ROWS",
                            "range": "sheetId!A2:B3",
                            "revision": 87,
                            "values": [[1, 2], [3, 4]]
                        },
                        ...
                    ]
                }
            }

        Example:
            >>> response = request.read_batch(['A2:B3', 'D5:E6'])
            >>> data = response.json()
            >>> for value_range in data['data']['valueRanges']:
            >>>     print(value_range['range'], value_range['values'])
        """
        # 构造范围字符串：每个范围前加上 sheet_id
        range_params = ','.join([f"{self.sheet_id}!{r.upper()}" for r in ranges])

        url = self._build_url(
            self.link_sheets.readBatch
            .format(SHEET_TOKEN=self.sheet_token)
            .with_query(
                ranges=range_params,
                valueRenderOption=value_render_option,
                dateTimeRenderOption=date_time_render_option
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

        return self.read(sheet_range, value_render_option="Formula", date_time_render_option="FormattedString")

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

    def _preprocess_data_grid(self, data_list: List[List[Any]]) -> List[List[Any]]:
        """
        预处理数据网格，将各种数据类型转换为飞书 API 接受的格式。

        处理逻辑:
        - FeiShuCellType: 调用 to_json() 方法
        - NaN: 转换为 None
        - 公式（以 = 开头的字符串）: 封装为 Formula 对象
        - datetime/Decimal/bool: 转换为字符串
        - 其他复杂对象: JSON 序列化

        :param data_list: 二维数组
        :return: 处理后的二维数组
        """
        def _default(o):
            if isinstance(o, float) and math.isnan(o):
                return None
            if isinstance(o, (datetime, Decimal, bool)):
                return str(o)
            raise TypeError(f"对象类型：[ {type(o).__name__} ] 不是一个可 JSON 序列化的，写入失败")

        for r, row in enumerate(data_list):
            for c, item in enumerate(row):
                if isinstance(item, FeiShuCellType):
                    data_list[r][c] = item.to_json()
                elif isinstance(item, bool):
                    data_list[r][c] = "True" if item else "False"
                elif isinstance(item, float) and math.isnan(item):
                    data_list[r][c] = None
                elif item is None or isinstance(item, (int, float)):
                    continue
                elif isinstance(item, str):  # 公式
                    if item.startswith("="):
                        data_list[r][c] = Formula(item).to_json()
                    else:
                        continue
                else:
                    data_list[r][c] = json.dumps(item, default=_default, ensure_ascii=False, indent=4)

        return data_list

    def write(self, sheet_range: str, data_list: List[List[Any]]) -> requests.Response:
        """
        [向单个范围写入数据](https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/write-data-to-a-single-range)

        单次写入数据不得超过 5000 行、100列。
        每个单元格不超过 50,000 字符，由于服务端会增加控制字符，因此推荐每个单元格不超过 40,000 字符。

        :param sheet_range: 示例: 'A2:B5', 'ad10:ad100', 'd3:d12'
        :param data_list: 二维数组，数组元素表示行数据。如： [[1,2,3], [4,5,6]] 表示写入的第一行数据为 1,2,3 ... ... 没有数据填 None
        """
        data_list = self._preprocess_data_grid(data_list)

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

    def write_batch(self, value_ranges: List[Dict[str, Any]]) -> requests.Response:
        """
        [向多个范围写入数据](https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/write-data-to-multiple-ranges)

        该接口用于根据电子表格的 spreadsheetToken 和 range 向多个范围写入数据。
        单次写入不超过 5000 行，100 列，每个格子不超过 5 万字符。

        :param value_ranges: 写入数据的列表，每个元素包含 range 和 values 字段
            示例: [
                {"range": "A2:B5", "values": [[1,2], [3,4], [5,6], [7,8]]},
                {"range": "D2:E3", "values": [[9,10], [11,12]]}
            ]
        """
        # 处理每个范围的数据
        processed_ranges = []
        for value_range in value_ranges:
            sheet_range = value_range["range"]
            data_list = value_range["values"]

            # 数据预处理（复用公共方法）
            data_list = self._preprocess_data_grid(data_list)

            processed_ranges.append({
                "range": self.sheet_id + "!" + sheet_range.upper(),
                "values": data_list
            })

        url = self._build_url(
            self.link_sheets.writeBatch.format(SHEET_TOKEN=self.sheet_token).human_repr(),
        )
        body = {"valueRanges": processed_ranges}
        response = requests.post(url, headers=self._get_request_headers(), data=json.dumps(body))
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

    def update_sheet_properties(self, properties: SheetProperties) -> requests.Response:
        """
        [操作工作表-复制sheet](https://open.feishu.cn/document/server-docs/docs/sheets-v3/spreadsheet-sheet/operate-sheets) \n

        :param title: 新 sheet 的名称
        :param index: 新 sheet 在表中的索引位置，默认为 0 第一个
        """
        properties_dict = properties.to_dict()
        properties_dict.update({"sheetId": self.sheet_id})

        url = self._build_url(
            self.link_sheets.sheetsBatchUpdate.format(SHEET_TOKEN=self.sheet_token).human_repr(),
        )
        body = {
            "requests": [
                {
                    "updateSheet": {
                        "properties": properties_dict,
                    }
                }
            ]
        }
        response = requests.post(url, headers=self._get_request_headers(), data=json.dumps(body))
        response.raise_for_status()
        return response

    def delete_series(
        self, start_index: int, end_index: int, major_dimension="ROWS"
    ) -> Dict | requests.Response:
        """
        [删除行或者列](https://open.feishu.cn/document/server-docs/docs/sheets-v3/sheet-rowcol/-delete-rows-or-columns)

        :param start_index:
            要删除的行或列的起始位置，从 1 开始计数。若 startIndex 为 3 ，则从第 3 行或列开始删除。包含第 3 行或列。
        :param end_index:
            要删除的行或列结束的位置。从 1 开始计数。若 endIndex 为 7 ，则删除至第 7 行或列结束。包含第 7 行或列。
            示例：当 majorDimension 为 ROWS、 startIndex 为 3、endIndex 为 7 时，则删除第 3、4、5、6、7 行的数据，共删除 5 行.
        :param major_dimension: 删除的维度。可选值：
            - ROWS：行
            - COLUMNS：列
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

    def insert_series(
        self, start_index: int, end_index: int, major_dimension="ROWS", inherit_style: str='',
    ):
        """
        [插入行列](https://open.feishu.cn/document/server-docs/docs/sheets-v3/sheet-rowcol/insert-rows-or-columns)

        :param start_index: 插入的行或列的起始位置。从 0 开始计数。若 ``startIndex`` 为 3，则从第 4 行或列开始插入空行或列。包含第 4 行或列。

        :param end_index: 插入的行或列结束的位置。从 0 开始计数。若 ``endIndex`` 为 7，则从第 8 行结束插入行。第 8 行不再插入空行。
            示例：当 ``majorDimension`` 为 ROWS、 ``startIndex`` 为 3、``endIndex`` 为 7 时，则在第 4、5、6、7 行插入空白行，共插入 4 行。

        :param major_dimension: ROWS 或 COLUMNS ，默认 ROWS

        :param inherit_style: 插入的空白行或列是否继承表中的单元格样式。不填或设置为空即不继承任何样式，为默认空白样式。可选值：
        - BEFORE：继承起始位置的单元格的样式
        - AFTER：继承结束位置的单元格的样式
        """
        url = self._build_url(
            self.link_sheets.insertSeries.format(SHEET_TOKEN=self.sheet_token).human_repr(),
        )
        body = {
            "dimension": {
                "sheetId": self.sheet_id,
                "majorDimension": major_dimension.upper(),
                "startIndex": start_index,
                "endIndex": end_index,
            },
            "inheritStyle": inherit_style,
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
    ) -> Tuple[str | None, bytes]:
        """
        所有下载方法的底层实现.[文档](https://open.feishu.cn/document/server-docs/docs/drive-v1/media/download)

        Return:
            返回一个元组(文件名.扩展名--可能为 None, 二进制数据)
        """
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

        filename = extract_filename_from_response(response)

        chunks = [
            chunk for chunk in response.iter_content(chunk_size=chunk_size) if chunk
        ]
        return filename, b"".join(chunks)

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

    def set_styles_batch_update(self, data: List[Dict[str, Any]]) -> requests.Response:
        """
        [批量设置单元格样式](https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/batch-set-cell-style)

        该接口用于根据 spreadsheetToken 操作表格，批量设置单元格样式。

        Args:
            data: 样式设置数据列表，每个元素包含 ranges 和 style 字段
                示例: [
                    {
                        "ranges": ["A1:B2", "C3:D4"],
                        "style": {
                            "font": {"bold": True, "fontSize": "12pt/1.5"},
                            "foreColor": "#000000"
                        }
                    }
                ]

        Returns:
            requests.Response: API 响应对象
        """
        # 处理每个样式设置项
        processed_data = []
        for item in data:
            ranges = item["ranges"]
            style = item["style"]

            # 自动添加 sheet_id 前缀
            processed_ranges = [self.sheet_id + '!' + r.upper() for r in ranges]

            processed_data.append({
                "ranges": processed_ranges,
                "style": style
            })

        url = self._build_url(
            self.link_sheets.styleBatchUpdate.format(SHEET_TOKEN=self.sheet_token).human_repr(),
        )
        body = {"data": processed_data}
        response = requests.put(url, headers=self._get_request_headers(), data=json.dumps(body))
        response.raise_for_status()
        return response

    # ========== 导出任务相关方法 ==========

    def create_export_task(
        self,
        token: str,
        doc_type: str,
        file_extension: str,
        sub_id: str = None
    ) -> requests.Response:
        """
        创建导出任务

        将飞书云文档导出为本地文件，支持导出为 Word、Excel、PDF、CSV 格式。
        这是一个异步接口，需要继续调用 get_export_task_result 获取导出结果。

        参考文档: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/drive-v1/export_task/create

        Args:
            token: 要导出的云文档的 token
            doc_type: 云文档类型，可选值：
                - doc: 旧版飞书文档（已不推荐）
                - sheet: 飞书电子表格
                - bitable: 飞书多维表格
                - docx: 新版飞书文档
            file_extension: 导出文件扩展名，可选值：
                - docx: Microsoft Word 格式
                - pdf: PDF 格式
                - xlsx: Microsoft Excel 格式
                - csv: CSV 格式
            sub_id: 导出电子表格或多维表格为 CSV 时，需要传入工作表或数据表的 ID

        Returns:
            requests.Response: API 响应对象，包含导出任务 ID (ticket)

        Example:
            >>> request = FeiShuRequest(link)
            >>> response = request.create_export_task(
            ...     token="your_doc_token",
            ...     doc_type="docx",
            ...     file_extension="pdf"
            ... )
            >>> ticket = response.json()["data"]["ticket"]
        """
        url = self._build_url(
            self.link_export.createTask.human_repr()
        )

        body = {
            "file_extension": file_extension,
            "token": token,
            "type": doc_type
        }

        if sub_id:
            body["sub_id"] = sub_id

        response = requests.post(
            url,
            headers=self._get_request_headers(),
            data=json.dumps(body)
        )
        response.raise_for_status()
        return response

    def get_export_task_result(
        self,
        ticket: str,
        token: str
    ) -> requests.Response:
        """
        查询导出任务结果

        根据导出任务 ID 查询导出任务的状态和结果，返回导出文件的 token。

        参考文档: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/drive-v1/export_task/get

        Args:
            ticket: 导出任务 ID，由 create_export_task 返回
            token: 要导出的云文档的 token（与创建任务时的 token 保持一致）

        Returns:
            requests.Response: API 响应对象，包含导出任务状态和文件信息

        Example:
            >>> request = FeiShuRequest(link)
            >>> response = request.get_export_task_result(
            ...     ticket="6933093124755423251",
            ...     token="your_doc_token"
            ... )
            >>> result = response.json()["data"]["result"]
            >>> if result["job_status"] == 0:  # 成功
            ...     file_token = result["file_token"]
        """
        url = self._build_url(
            self.link_export.getTaskResult
            .format(TICKET=ticket)
            .with_query(token=token)
            .human_repr()
        )

        response = requests.get(url, headers=self._get_request_headers())
        response.raise_for_status()
        return response

    def download_export_file(
        self,
        file_token: str
    ) -> requests.Response:
        """
        下载导出文件

        根据导出文件的 token 下载导出的产物到本地。
        注意：导出文件在导出任务结束 10 分钟后会被删除，请及时下载。

        参考文档: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/drive-v1/export_task/download

        Args:
            file_token: 导出文件的 token，由 get_export_task_result 返回

        Returns:
            requests.Response: API 响应对象，响应体为文件二进制流

        Example:
            >>> request = FeiShuRequest(link)
            >>> response = request.download_export_file(
            ...     file_token="boxcnxe5OdjlAkNgSNdsJvabcef"
            ... )
            >>> with open("export.pdf", "wb") as f:
            ...     f.write(response.content)
        """
        url = self._build_url(
            self.link_export.downloadFile
            .format(FILE_TOKEN=file_token)
            .human_repr()
        )

        response = requests.get(url, headers=self._get_request_headers())
        response.raise_for_status()
        return response
