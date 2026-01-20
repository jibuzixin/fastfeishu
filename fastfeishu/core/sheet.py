import pandas as pd

from fastfeishu.core.operations import FeiShuSheetOperations
from typing import Union, Any, Optional, List, Generator, Dict, Literal
from fastfeishu.utils import num_to_excel_col
from fastfeishu.exceptions.exception import FeiShuColumnNotExist, FeiShuException
from fastfeishu.core.interface import FeiShuInterface
from fastfeishu.utils.common import match_row_num_by_range, match_col_letter_by_range, excel_col_to_num


class FeiShuSheet(FeiShuSheetOperations, FeiShuInterface):
    """更直观的操作接口，并做了一些优化"""

    def __init__(self, link: str, readonly: bool = False):
        super().__init__(link, readonly)

    def get_index_by_col_name(self, col_name: str) -> int:
        """
        根据列名获取对应列的数字索引，起始序号为 1。
        例如：get_index_by_col_name("端到端回复") -> 6, 将会返回“端到端回复”列在第六列。

        Note:
            - 列名不存在的话抛出 ``FeiShuColumnNotExist`` 异常

        Args:
            col_name: 列名（列的第一行为列名）
        """
        if col_name not in self.get_header():
            raise FeiShuColumnNotExist(col_name)
        return self.get_header().index(col_name) + 1

    def get_letter_by_col_name(self, col_name: str) -> str:
        """
        根据列名获取对应列的字母索引，起始序号为 A。
        例如：get_index_by_col_name("端到端回复") -> AC, 将会返回“端到端回复”列在 AC 列。

        :param col_name: 列名（列的第一行为列名）
        """
        return num_to_excel_col(self.get_index_by_col_name(col_name))
    
    # -------------------------------------- 写操作 --------------------------------------------
    def delete_series_by_index(
        self,
        start_index: Union[str, int],
        end_index: Union[str, int]=None,
    ) -> int:
        """
        删除行或者列，如果 ``start_index`` 和 ``end_index`` 都是字符串，表明删除对应字母区间的列，如果都是整数删除对应区间的行。

        如果只填写 ``start_index`` 只删除单独这一列/行。

        Note:
            - 当表头有相同的重复名字的话，从左到右默认取第一个，避免使用相同表头名（列名）
            - 从 1 开始计数，左右都是闭区间

        Args:
            start_index: 可以是：<列字母：A/B/AA/BC>、行数8/9/23
            end_index: 可以是：<列名字母：A/B/AA/BC>、行数8/9/23

        Returns:
            int: 返回被删除 行/列 数
        """
        major_dimension: Literal["ROWS", "COLUMNS"] = "ROWS"
        if end_index is None:
            end_index = start_index

        if not isinstance(start_index, type(end_index)):
            raise ValueError(f"{start_index} 和 {end_index} 不是一个相同的类型")
        if isinstance(start_index, str):
            start_index = excel_col_to_num(start_index)
            end_index = excel_col_to_num(end_index)
            major_dimension = "COLUMNS"

        del_count = self.delete_series(start_index, end_index, major_dimension)
        return del_count

    def delete_column_by_name(
        self,
        start_col_name: str,
        end_col_name: str=None,
    ) -> int:
        """
        删除行或者列，如果 ``start_index`` 和 ``end_index`` 都是字符串，表明删除对应字母区间的列。

        如果只填写 ``start_index`` 只删除单独这一列。

        Note:
            - 当表头有相同的重复名字的话，从左到右默认取第一个，避免使用相同表头名（列名）
            - 列名不存在的话抛出 ``FeiShuColumnNotExist`` 异常
            - 从 1 开始计数，左右都是闭区间

        Args:
            start_index: 可以是：列字母：A/B/AA/BC
            end_index: 可以是：列名字母：A/B/AA/BC

        Returns:
            int: 返回被删除列数
        """
        if end_index is None:
            end_index = start_index

        start_col_name = self.get_index_by_col_name(start_col_name)
        end_col_name = self.get_index_by_col_name(end_col_name)

        return self.delete_series(start_index, end_index, "COLUMNS")

    def write_column(
        self, column_name: str,
        data_list: List[Any],
        start_row: int=2,
    ):
        """
        根据列名写入一列数据，如果列存在则覆盖写入，不存在则在行或列的末尾追加一列然后写入。
        """
        # 1. 预处理数据为二维数组
        data_list = [[d] for d in data_list]
        # 2. 如果列不存在则在末位新增一列并写入标题
        if column_name not in self.get_header():
            col_letter = self.append_series(1, "COLUMNS")  # 在末尾新增一列
            self.write(f'{col_letter}1:{col_letter}1', [[column_name]])  # 写入列名
        else:
            col_letter = self.get_letter_by_col_name(column_name)  # 列存在，获取列的字母索引
        # 3. 找到对应的列，将处理好的数据写入
        self.write(f'{col_letter}{start_row}:{col_letter}{len(data_list)+start_row-1}', data_list)

    def write_row(
        self,
        data: List[Union[List[Any], Dict[str, Any]]],
        write_row: int = 2,
    ):
        """
        写入一行或者多行数据，如果是多行需要用数组包装。

        Note:
            - 如果是字典则会根据列名（默认列的第一个单元格）写入，列不存在什么都不写
            - 二维数组的第一个索引值代表行，第二个索引值代表行中单元格的值。需要保证数组元素可序列化

        Args:
            data: 需要写入的值可以是二维数组、数组[字典]
            write_row: 要写入的起始行
        """
        write_list = []
        header = self.header
        heads_len = len(header)

        if write_row == 1:
            if not isinstance(data[0], list):
                raise ValueError("此方法依赖表头，无法覆盖写入第一行，如有需要，请将写入数组的第一个元素设置为数组类型表示为表头。"
                                 "或者使用 write() 方法。")
            if isinstance(data[0], list):
                header = data[0]
                heads_len = len(header)

        for row in data:
            if isinstance(row, dict):
                write_list.append([row[col_name] if col_name in row.keys() else None
                                   for col_name in header])
            elif isinstance(row, list):
                row = (row + [None] * heads_len)[:heads_len]  # 对齐数组长度，否则写入的时候会报错
                write_list.append(row)
            else:
                raise ValueError(f"需要写入的值可以是二维数组、数组[字典]。当前数组元素类型是: {type(row)}")

        cell_range = f'A{write_row}:{num_to_excel_col(heads_len)}{len(write_list)+write_row-1}'
        self.write(cell_range, write_list)

    def write_row_by_hang_header(
        self,
        hang_header_range: str,
        data: List[Union[List[Any], Dict[str, Any]]],
        write_row: int = 2,
    ):
        """
        根据指定的“悬挂表头”写入行数据。即：可以指定任意一行范围内的数据为临时表头，并按照此表头写入数据。

        Note:
            - 如果表头之间有不想写入的数据，应该分为若干个“悬挂头”分别写入，此方法不能自动跳过不想写入的数据

        Args:
            hang_header_range: 悬挂头的范围（ 如：C22:JK22, DF345:DL345 ），一个行范围，多行报错
            data: 需要写入的值可以是二维数组、数组[字典]
            write_row: 相对于悬挂头来说的开始行数，悬挂头为第 1 行，默认开始从第 2 行写入
        """
        if write_row <= 1:
            raise ValueError(f"write_row")
        # 1. 判断行的范围是否正确
        a, b = match_row_num_by_range(hang_header_range)
        if a != b:
            raise ValueError(f"hang_header 参数单元格范围表示应该为一行数据的范围，如：A2:F2。当前为：{hang_header_range}")
        write_row = int(a) + write_row - 1  # 写入数据相对于表头的偏移量

        # 2. 校验输入 range 正确
        start_col, end_col = match_col_letter_by_range(hang_header_range)
        start_col_num = excel_col_to_num(start_col)
        end_col_num = excel_col_to_num(end_col)
        if end_col_num < start_col_num:
            raise ValueError(f"输入 hang_header 数据范围有误，当前 {end_col} 比 {start_col} 要小，输入数据: {hang_header_range}")

        # 3. 获取行的内容作为临时表头
        header = self.read_human(hang_header_range)[0]

        # 4. 将数据按照表头对齐
        write_list = []
        for row in data:
            if isinstance(row, dict):
                write_list.append([row[col_name] if col_name in row.keys() else None
                                   for col_name in header])
            elif isinstance(row, list):
                row = (row + [None] * len(header))[:len(header)]
                write_list.append(row)
            else:
                raise ValueError(f"需要写入的值可以是二维数组、数组[字典]。当前数组元素类型是: {type(row)}")
        # 5. 写入数据
        cell_range = f'{start_col}{write_row}:{end_col}{len(write_list) + write_row - 1}'
        self.write(cell_range, write_list)

    def replace_placeholder(self, sheet_range: str, **kwargs):
        """将 sheet_range 范围内中出现的占位符替换为传入的键值对"""
        read_range = self.read_raw(sheet_range)
        for r, row in enumerate(read_range):
            for c, cell in enumerate(row):
                if cell is not None and isinstance(cell, str):
                    read_range[r][c] = cell.format(**kwargs)
        # TODO 改成写多范围可以提升意料之外情况的影响
        self.write(sheet_range, read_range)

    def insert_column_to_right(
        self,
        column_letter: str,
        insert_number: int = 1,
        inherit_style: bool = True,
    ):
        """向指定列左边插入指定数量的空列，inherit_style 为 True 表示插入列是否复制起始列的单元格样式。"""
        col_num = excel_col_to_num(column_letter)
        if inherit_style:
            self.insert_series(col_num, col_num + insert_number, "COLUMNS", "BEFORE")
        else:
            self.insert_series(col_num, col_num + insert_number, "COLUMNS")

    def insert_column_to_left(
        self,
        column_letter: str,
        insert_number: int = 1,
        inherit_style: bool = True,
    ):
        """向指定列右边插入指定数量的空列，inherit_style 为 True 表示插入列是否复制起始列的单元格样式。"""
        col_num = excel_col_to_num(column_letter) - 1
        if inherit_style:
            self.insert_series(col_num, col_num + insert_number, "COLUMNS", "AFTER")
        else:
            self.insert_series(col_num, col_num + insert_number, "COLUMNS")

    # ------------------------------------- 读操作 ---------------------------------------------

    def _cell_value_type_judge(self, cell: Union[Dict, List, str, bool]) -> str:
        new_value = []
        if isinstance(cell, dict):
            if cell['type'] == 'url':
                return cell["link"]
            else:
                return cell['text']
        elif isinstance(cell, list):
            for item in cell:
                new_value.append(self._cell_value_type_judge(item))
        else:
            return cell
        return ''.join(new_value)

    def read_human(self, sheet_range: str) -> List[List[Any]]:
        """人类所见即所得的方式读。如果是链接就是链接，如果是公式的值就是公式的值，如果是日期格式化的就是格式化后的日期字符串。不能读图！"""
        data = self.read(sheet_range, value_render_option="FormattedValue")
        for r, row in enumerate(data):
            for c, cell in enumerate(row):
                data[r][c] = self._cell_value_type_judge(cell)
        return data

    def read_raw(self, sheet_range: str) -> List[List[Any]]:
        data = self.read(sheet_range, value_render_option="Formula", date_time_render_option='')
        return data

    def get_title(self) -> str:
        info = self.get_sheet_info()
        if "title" in info:
            return info["title"]
        else:
            return ''

    def iterrows(
            self,
            start_row: int = 2,
            end_row: Optional[int] = None,
            batch_size: int = 500,
            include_header: bool = False,
            use_pandas: bool = True,
    ) -> Generator[Union[tuple[int, dict[str, Any]], tuple[int, pd.Series]], None, None]:
        """
        流式迭代读取飞书表格每一行，像本地列表一样使用，内存安全。

        自动控制每次请求数据量 < 10MB（飞书实际限制更严格，保守估计）
        推荐 batch_size=500（根据实际情况适当调节，可加快遍历速度）

        Example:
            >>> # noinspection PyUnresolvedReferences
            >>> for index, row in sheet.iterrows(start_row=2):
            >>>     print(index, row["姓名"], row["年龄"])  # dict 模式（推荐）
            >>>     # 或
            >>>     print(index, row[0], row[1])          # pd.Series 模式

        Args:
            start_row: 数据起始行（含），默认 2（跳过表头）
            end_row: 结束行（含），None 表示读到最后
            batch_size: 每次读取行数，默认 200，建议 800~2000
            include_header: 是否在第一批返回表头行
            use_pandas: True 返回 pd.Series 字典行（更强大），需要 import pandas

        Returns:
            生成器，每行是 (索引, 数据) 元组，数据为 dict 或 pd.Series
        """

        info = self.get_sheet_info()
        total_rows = info["rowCount"]
        max_row = end_row or total_rows
        if start_row > max_row:
            return

        header = None
        if include_header or use_pandas:
            header = self.get_header()

        current_row = start_row
        while current_row <= max_row:
            batch_end = min(current_row + batch_size - 1, max_row)
            range_str = (
                f"A{current_row}:{num_to_excel_col(info['columnCount'])}{batch_end}"
            )

            try:
                batch_data = self.read_human(range_str)
            except Exception as e:
                raise FeiShuException(f"读取行 {current_row}~{batch_end} 失败: {e}")

            if not batch_data:
                break

            # 首次读取时提取表头（如果还没取）
            if header is None and batch_data:
                header = batch_data[0] if start_row == 1 else self.get_header()
                if start_row > 1:
                    batch_data = batch_data  # 数据从第 start_row 行开始
                else:
                    batch_data = batch_data[1:]  # 跳过表头行

            # 构造每一行
            for row_values in batch_data:
                if not row_values:  # 跳过空行，正常来说不会走这个逻辑
                    current_row += 1
                    continue

                if use_pandas:
                    # 自动对齐列数（飞书有时返回短行）
                    padded = (row_values + [""] * len(header))[: len(header)]
                    yield current_row, pd.Series(padded, index=header)
                else:
                    # dict 模式最推荐：字段名访问，补空对齐
                    padded = (row_values + [""] * len(header))[: len(header)]
                    yield current_row, dict(zip(header, padded))

                current_row += 1

            if batch_end >= max_row:
                break
