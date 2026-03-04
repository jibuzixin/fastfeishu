from typing import (
    Protocol,
    Generator,
    Union,
    Optional,
    List, Any, Dict,
    Literal,)
import pandas as pd
import abc


class FeiShuInterface(abc.ABC):
    @abc.abstractmethod
    def get_header(self) -> List[str]: ...

    @abc.abstractmethod
    def read(
        self,
        sheet_range: str,
        value_render_option: str = "ToString",
        date_time_render_option: str = "FormattedString"
    ) -> List[List[Any]]:
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
        pass

    @abc.abstractmethod
    def read_images(self, sheet_range: str) -> List[List[Any]]: ...

    @abc.abstractmethod
    def create_sheet(self, title: str, index: int) -> str: ...

    @abc.abstractmethod
    def insert(self, sheet_range: str, data_list: List[List]): ...  # ?

    @abc.abstractmethod
    def write(self, sheet_range: str, data_list: List[List[Any]]): ...  # ?

    @abc.abstractmethod
    def write_batch(self, value_ranges: List[Dict[str, Any]]): ...  # ?

    @abc.abstractmethod
    def append(self, sheet_range: str, data_list: List[list], insert_data_option="OVERWRITE"): ...  # ?

    @abc.abstractmethod
    def delete_series_by_index(self, start_index: str | int, end_index: str | int): ...

    @abc.abstractmethod
    def write_row_by_hang_header(
            self,
            hang_header_range: str,
            data: List[Union[List[Any], Dict[str, Any]]],
            write_row: int = 2,
            skip_none: bool = True,
            partition_strategy: Literal['horizontal', 'vertical', 'auto'] = 'auto'
    ): ...

    @abc.abstractmethod
    def iterrows(
            self,
            start_row: int = 2,
            end_row: Optional[int] = None,
            batch_size: int = 500,
            include_header: bool = False,
            use_pandas: bool = True,
    ) -> Generator[Union[dict[str, Any], pd.Series], None, None]: ...

    @abc.abstractmethod
    def insert_column_to_right(
            self,
            column_letter: str,
            insert_number: int = 1,
            inherit_style: bool = True,
    ): ...

    @abc.abstractmethod
    def insert_column_to_left(
            self,
            column_letter: str,
            insert_number: int = 1,
            inherit_style: bool = True,
    ): ...

    @abc.abstractmethod
    def delete_series(self, start_index, end_index, major_dimension: Literal["ROWS", "COLUMNS"] = "ROWS") -> int: ...

    @abc.abstractmethod
    def set_style(self, sheet_range: str, style: Union['CellStyle', Dict[str, Any]]): ...

    @abc.abstractmethod
    def set_styles(self, data: List['StyleRangeData']): ...

class IterableSheetProtocol(Protocol):
    def iterrows(
        self,
        start_row: int = 2,
        end_row: Optional[int] = None,
    ) -> Generator[Union[dict[str, Any], pd.Series], None, None]: ...
