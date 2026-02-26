import requests

from io import BytesIO
from typing import Any, Dict, List, Literal, Union, Self
from fastfeishu.models import SheetProperties, CellStyle
from yarl import URL
from pathlib import Path
from PIL import Image

from fastfeishu.core import FeiShuRequest
from fastfeishu.exceptions.exception import FeiShuException, FeiShuRequestException
from fastfeishu.helpers import match_row_num_by_range, base64_image, num_to_excel_col, excel_col_to_num


def _response_json(response: requests.Response) -> Dict[str, Any]:
    response_json: Dict[str, Any] = response.json()
    # TODO 增加通过栈获取是哪个请求调用的，方便记录
    if response_json["code"] != 0:
        raise FeiShuRequestException(f"\n>>>\tcode: {response_json['code']}"
                                     f"\n>>>\tmsg: {response_json['msg']}"
                                     f"\n>>>\t飞书通用异常情况查看：https://open.feishu.cn/document/server-docs/api-call-guide/generic-error-code")
    return response_json

class FeiShuSheetOperations:
    """对 FeiShuRequest 类方法做读写入口的前后处理，并返回适合处理的返回值"""

    def __init__(self, link: str, readonly: bool = False):
        self._alter_header = True
        self._header = None
        self._readonly = readonly
        self._request = FeiShuRequest(link)

    @property
    def header(self) -> List[str]:
        return self.get_header()

    @property
    def link(self) -> str:
        return self._request.link

    @link.setter
    def link(self, value: str) -> None:
        self._request.link = value

    @property
    def sheet_token(self) -> str:
        return self._request.sheet_token

    @sheet_token.setter
    def sheet_token(self, value: str) -> None:
        self._request.sheet_token = value

    @property
    def sheet_id(self) -> str:
        return self._request.sheet_id

    @sheet_id.setter
    def sheet_id(self, value: str) -> None:
        self._request.sheet_id = value

    @property
    def raw_request(self) -> FeiShuRequest:
        return self._request

    def _deny_if_readonly(self) -> None:
        """统一写操作拦截点"""
        if self._readonly:
            raise FeiShuException("当前实例为只读模式，禁止写入操作")

    def get_header(self) -> List[str]:
        """获取表头"""
        if not self._alter_header:
            return self._header
        sheet_info = self.get_sheet_info()
        if sheet_info is None:
            return []
        self._header = self.read(f"A1:{num_to_excel_col(sheet_info['columnCount'])}1")[0]
        self._alter_header = False
        return self._header

    def _detect_header_modification(self, sheet_range: str) -> bool:
        if self._alter_header:
            return True
        start_row, _ = match_row_num_by_range(sheet_range)
        if start_row == "1":
            self._alter_header = True
            return True
        return False

    def is_readonly(self):
        """当前飞书对象是否是只读模式"""
        return self._readonly

    # -------------------------------------- 其他操作 --------------------------------------------
    def get_sheet_metadata(self) -> Dict[str, Any]:
        response = self._request.get_sheet_metadata()
        return response

    def get_sheet_info(self) -> Dict[str, Any] | None:
        response_json = self._request.get_sheet_info().json()
        for sheet_info in response_json["data"]["sheets"]:
            if sheet_info["sheetId"] == self.sheet_id:
                return sheet_info
        return None

    # -------------------------------------- 写操作 --------------------------------------------
    def write(self, sheet_range: str, data_list: List[List[Any]]):
        self._deny_if_readonly()
        response = self._request.write(sheet_range, data_list)
        _response_json(response)
        self._detect_header_modification(sheet_range)

    def write_batch(self, value_ranges: List[Dict[str, Any]]):
        """
        向多个范围批量写入数据。

        Args:
            value_ranges: 写入数据的列表，每个元素包含 range 和 values 字段
                示例: [
                    {"range": "A2:B5", "values": [[1,2], [3,4], [5,6], [7,8]]},
                    {"range": "D2:E3", "values": [[9,10], [11,12]]}
                ]
        """
        self._deny_if_readonly()
        response = self._request.write_batch(value_ranges)
        _response_json(response)

        # 检测是否有任何范围修改了表头
        for value_range in value_ranges:
            self._detect_header_modification(value_range["range"])

    def append(self, sheet_range, data_list, insert_data_option="OVERWRITE"):
        self._deny_if_readonly()
        response = self._request.append(sheet_range, data_list, insert_data_option)
        _response_json(response)
        self._detect_header_modification(sheet_range)

    def insert(self, sheet_range, data_list):
        """在电子表格工作表的指定范围的起始位置上方增加若干行，并在该范围中填充数据。"""
        self._deny_if_readonly()
        response = self._request.insert(sheet_range, data_list)
        _response_json(response)
        self._detect_header_modification(sheet_range)

    def delete_series(self, start_index: int, end_index: int, major_dimension: Literal["ROWS", "COLUMNS"] = "ROWS") -> int:
        """返回删除行或者列的数量"""
        self._deny_if_readonly()
        response = self._request.delete_series(start_index, end_index, major_dimension)
        del_count = _response_json(response)['data']['delCount']
        if major_dimension == "COLUMNS":
            self._alter_header = True
        return del_count

    def append_series(self, add_count: int, major_dimension: Literal["ROWS", "COLUMNS"] = "ROWS") -> Union[int, str]:
        """
        该接口仅支持在工作表的行末尾或列末尾新增行列。如果是列返回该列的字母索引，如果是行返回总行数。

        Args:
            add_count: 要增加的行列数
            major_dimension: ROWS 或 COLUMNS ，默认 ROWS

        Returns:
            Union[int, str]: 返回列字母索引或者插入后的总行数（最后一行/列）
        """
        self._deny_if_readonly()
        response = self._request.append_series(add_count, major_dimension)
        _response_json(response)
        if major_dimension.upper() == "ROWS":
            return self.get_sheet_info()["rowCount"]
        else:
            self._alter_header = True
            col_index = len(self.get_header())
            return num_to_excel_col(col_index)

    def insert_series(
        self,
        start_index: int,
        end_index: int,
        major_dimension: Literal["ROWS", "COLUMNS"] = "ROWS",
        inherit_style: Literal["BEFORE", "AFTER", ""] = ''
    ):
        """插入行列的入口方法，控制一些权限操作，所有插入行列高级抽象方法都引用此函数"""
        self._deny_if_readonly()
        response = self._request.insert_series(start_index, end_index, major_dimension, inherit_style)
        _response_json(response)
        if major_dimension.upper() == "COLUMNS":
            self._alter_header = True

    def write_image(self, cell, image, image_name="cell.png"):
        """
        [写入图片](https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/write-images)

        :param cell: 示例: 'a2', 'B33', 'df56'
        :param image: 可传入一个本地图片的路径或者已经加载好的二进制数据
        :param image_name: 图片名称
        """
        self._deny_if_readonly()
        response = self._request.write_image(cell, image, image_name)
        _response_json(response)
        self._detect_header_modification(f'{cell}:{cell}')

    def create_sheet(self, title: str, index: int = 0) -> Self:
        """返回新创建的 FeiShuSheet 对象"""
        self._deny_if_readonly()
        response = self._request.create_sheet(title, index)
        new_sheet_id = _response_json(response)["data"]["replies"][0]["addSheet"]["properties"]["sheetId"]
        new_link = str(URL(self.link).update_query(sheet=new_sheet_id))
        return type(self)(new_link)

    def copy(self, title: str) -> Self:
        """复制当前 sheet ，返回新 sheet 对象"""
        response = self._request.copy_sheet(title)
        new_sheet_id = _response_json(response)["data"]["replies"][0]["copySheet"]["properties"]["sheetId"]
        new_link = str(URL(self.link).update_query(sheet=new_sheet_id))
        return type(self)(new_link)

    def update_sheet_properties(self, properties: SheetProperties):
        self._deny_if_readonly()
        response = self._request.update_sheet_properties(properties)
        _response_json(response)

    # -------------------------------------- 设置样式 --------------------------------------------
    def set_style(self, sheet_range: str, style: Union[CellStyle, Dict[str, Any]]):
        """
        设置单元格样式，支持字体、对齐、边框、颜色等多种样式配置

        [飞书 API 文档](https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/set-cell-style)

        Args:
            sheet_range: 单元格范围，如 'A3:C4'
            style: CellStyle 对象或样式字典，支持以下属性：
                - font (dict): 字体相关样式
                    - bold (bool): 是否加粗，默认 false
                    - italic (bool): 是否斜体，默认 false
                    - fontSize (str): 字体大小，如 "10pt/1.5"。10pt 表示字号（取值范围 [9,36]pt），1.5 为行距（固定 1.5px）
                    - clean (bool): 是否清除字体格式，默认 false
                - textDecoration (int): 文本装饰样式
                    - 0: 默认样式，不加下划线和删除线
                    - 1: 下划线
                    - 2: 删除线
                    - 3: 下划线和删除线
                - formatter (str): 数字格式，支持的格式类型：
                    - "@": 纯文本 (text)
                    - "0": 数字 (1024)
                    - "#,##0": 数字(千分位) (1,024)
                    - "#,##0.00": 数字(千分位 小数点) (1,024.56)
                    - "0%": 百分比 (10%)
                    - "0.00%": 百分比(小数点) (10.24%)
                    - "0.00E+00": 科学计数 (1.02E+03)
                    - "¥#,##0": 人民币 (¥1,024)
                    - "¥#,##0.00": 人民币(小数点) (¥1,024.56)
                    - "$#,##0": 美元 ($1,024)
                    - "$#,##0.00": 美元(小数点) ($1,024.56)
                    - "yyyy/MM/dd": 日期 (2017/08/10)
                    - "yyyy-MM-dd": 日期 (2017-08-10)
                    - "HH:mm:ss": 时间 (23:24:25)
                    - "yyyy/MM/dd HH:mm:ss": 日期时间 (2017/08/10 23:24:25)
                - hAlign (int): 水平对齐方式
                    - 0: 左对齐
                    - 1: 中对齐
                    - 2: 右对齐
                - vAlign (int): 垂直对齐方式
                    - 0: 上对齐
                    - 1: 中对齐
                    - 2: 下对齐
                - foreColor (str): 字体颜色，十六进制颜色代码，如 "#000000"
                - backColor (str): 背景颜色，十六进制颜色代码，如 "#ffffff"
                - borderType (str): 边框类型
                    - FULL_BORDER: 全边框，即四周都有边框
                    - OUTER_BORDER: 外边框，只有外侧有边框
                    - INNER_BORDER: 内边框，只有内部有边框
                    - NO_BORDER: 无边框
                    - LEFT_BORDER: 左边框
                    - RIGHT_BORDER: 右边框
                    - TOP_BORDER: 上边框
                    - BOTTOM_BORDER: 下边框
                - borderColor (str): 边框颜色，十六进制颜色代码，如 "#ff0000"
                - clean (bool): 是否清除所有格式，默认 false

        Examples:
            >>> # 使用 Builder 模式创建样式
            >>> style = CellStyle.builder() \\
            ...     .font(Font.builder().bold().font_size("12pt/1.5").build()) \\
            ...     .fore_color("#000000") \\
            ...     .back_color("#ffff00") \\
            ...     .h_align(1) \\
            ...     .border_type("FULL_BORDER") \\
            ...     .build()
            >>> sheet.set_style("A1:C3", style)

            >>> # 使用字典直接设置
            >>> sheet.set_style("A1:C3", {
            ...     "font": {"bold": True, "fontSize": "14pt/1.5"},
            ...     "hAlign": 1,
            ...     "foreColor": "#000000"
            ... })
        """
        self._deny_if_readonly()
        # 如果是 CellStyle 对象，转为字典
        if isinstance(style, CellStyle):
            style = style.to_dict()
        response = self._request.set_style(sheet_range, style)
        _response_json(response)

    # -------------------------------------- 读操作 --------------------------------------------

    def read(
        self,
        sheet_range: str,
        value_render_option: str="ToString",
        date_time_render_option: str="FormattedString"
    ) -> List[List[Any]]:
        """
        [读取单个范围](https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/reading-a-single-range)

        Args:
            sheet_range: 读取表格的范围: 'A2:BC10'
            value_render_option: 指定单元格数据的格式。可选值如下所示。当参数缺省时，默认不进行公式计算，返回公式本身，且单元格为数值格式。

                - ToString: 回纯文本的值（数值类型除外）
                - Formula: 单元格中含有公式时，返回公式本身
                - FormattedValue: 计算并格式化单元格
                - UnformattedValue: 计算但不对单元格进行格式化
            date_time_render_option: 指定数据类型为日期、时间、或时间日期的单元格数据的格式。

                - 若不传值，默认返回浮点数值，整数部分为自 1899 年 12 月 30 日以来的天数；小数部分为该时间占 24 小时的份额。
                  例如：若时间为 1900 年 1 月 1 日中午 12 点，则默认返回 2.5。
                  其中，2 表示 1900 年 1 月 1 日为 1899 年12 月 30 日之后的 2 天；
                  0.5 表示 12 点占 24 小时的二分之一，即 12/24=0.5。
                - 可选值为 FormattedString，此时接口将计算并对日期、时间、或时间日期类型的数据格式化并返回格式化后的字符串，但不会对数字进行格式化。
        """
        response = self._request.read(sheet_range, value_render_option, date_time_render_option)
        return _response_json(response)["data"]["valueRange"]["values"]

    def read_batch(
        self,
        ranges: List[str],
        value_render_option: str = "ToString",
        date_time_render_option: str = "FormattedString"
    ) -> Dict[str, Any]:
        """
        [读取多个范围](https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/reading-multiple-ranges)

        批量读取电子表格中多个指定范围的数据。该接口返回数据的最大限制为 10 MB。

        Args:
            ranges: 要读取的范围列表，例如 ["A1:B2", "D5:E10"]
            value_render_option: 指定单元格数据的格式。可选值如下所示。当参数缺省时，默认不进行公式计算，返回公式本身，且单元格为数值格式。
                - ToString: 返回纯文本的值（数值类型除外）
                - Formula: 单元格中含有公式时，返回公式本身
                - FormattedValue: 计算并格式化单元格
                - UnformattedValue: 计算但不对单元格进行格式化
            date_time_render_option: 指定数据类型为日期、时间、或时间日期的单元格数据的格式。
                - 若不传值，默认返回浮点数值
                - 可选值为 FormattedString，此时接口将计算并对日期、时间、或时间日期类型的数据格式化并返回格式化后的字符串

        Returns:
            包含多个范围数据的字典，格式为:
            {
                "valueRanges": [
                    {"range": "sheet1!A1:B2", "values": [[...], [...]]},
                    {"range": "sheet1!D5:E10", "values": [[...], [...]]}
                ]
            }
        """
        response = self._request.read_batch(ranges, value_render_option, date_time_render_option)
        return _response_json(response)["data"]

    def read_images(self, sheet_range) -> List[List[Any]]:
        response = self._request.read_images(sheet_range)
        return _response_json(response)["data"]["valueRange"]["values"]

    # TODO 下载图片应该提取到飞书工具中
    def download_image_to_path(
        self,
        file_token: str,
        save_path: Union[str, Path],
        *,
        extra: str | None = None,
    ) -> Path:
        """
        下载图片并保存到本地路径
        """
        save_path = Path(save_path)
        data = self._request.download_media_raw(file_token, extra=extra)

        if save_path.is_dir():
            content_type = self._request.get_media_content_type(file_token)
            ext = {
                "image/png": ".png",
                "image/jpeg": ".jpg",
                "image/webp": ".webp",
                "image/gif": ".gif",
            }.get(content_type, ".jpg")
            save_path = save_path / f"{file_token}{ext}"

        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_bytes(data)
        return save_path.resolve()

    def download_image_bytes(
        self,
        file_token: str,
        *,
        extra: str | None = None,
    ) -> bytes:
        """
        下载图片到内存，返回原始字节（推荐用于 OCR、上传、处理）
        """
        return self._request.download_media_raw(file_token, extra=extra)

    def download_image_stream(
        self,
        file_token: str,
        *,
        extra: str | None = None,
    ) -> BytesIO:
        """
        下载图片为内存流（推荐用于 FastAPI 响应、流式上传）
        """
        data = self._request.download_media_raw(file_token, extra=extra)
        stream = BytesIO(data)
        stream.name = file_token
        return stream

    def download_image_base64(
        self,
        file_token: str,
        *,
        extra: str | None = None,
        compress: int | None = None,
    ) -> str:
        """
        下载图片并返回 base64 编码字符串。

        :param file_token: 文件 token
        :param extra: 额外 query 参数（同原有方法）
        :param compress: 可选，压缩阈值（单位 MB）。
                        如果图片原始大小 > compress MB，则自动压缩至低于该阈值。
                        为 None 时不压缩，直接返回原图 base64。
        :return: base64 编码的图片字符串（不带 data:image/...;base64, 前缀）
        """
        # 1. 下载原始字节
        data = self._request.download_media_raw(file_token, extra=extra)

        # 如果不需要压缩，直接转 base64 返回
        if compress is None:
            return base64_image(data)

        # 2. 计算阈值（MB → bytes）
        threshold_bytes = compress * 1024 * 1024
        if len(data) <= threshold_bytes:
            # 小于阈值，无需压缩
            return base64_image(data)

        # 3. 需要压缩 → 使用 Pillow
        img = Image.open(BytesIO(data))
        # 保持原始格式（如果不支持保存的格式会自动转成合理格式）
        img_format = img.format or "JPEG"

        quality = 95  # 初始质量
        compressed_data = data

        while len(compressed_data) > threshold_bytes and quality > 10:
            buffer = BytesIO()
            save_kwargs = {"optimize": True, "quality": quality}
            # WebP 支持 quality，PNG 支持 compression（0-9）
            if img_format == "PNG":
                save_kwargs.pop("quality", None)
                save_kwargs["compress_level"] = 9

            img.save(buffer, format=img_format, **save_kwargs)
            compressed_data = buffer.getvalue()

            quality -= 10  # 逐步降低质量

        # 最终转 base64
        return base64_image(data)
