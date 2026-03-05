import pandas as pd

from fastfeishu.core.operations import FeiShuSheetOperations
from typing import Union, Any, Optional, List, Generator, Dict, Literal, Type, Tuple, Callable
from fastfeishu.helpers import num_to_excel_col, match_row_num_by_range, match_col_letter_by_range, excel_col_to_num, cell_is_blank
from fastfeishu.exceptions.exception import FeiShuColumnNotExist, FeiShuException
from fastfeishu.core.interface import FeiShuInterface
from fastfeishu.utils.partition_grid import partition_grid


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
        例如：get_index_by_col_name("端到端回复") -> AC, 将会返回"端到端回复"列在 AC 列。

        :param col_name: 列名（列的第一行为列名）
        """
        return num_to_excel_col(self.get_index_by_col_name(col_name))

    def check_columns_exist(self, col_names: List[str]) -> Dict[str, bool]:
        """
        检测指定的列名是否存在于表头中，返回每个列名的存在状态。

        该方法基于表头（第一行）进行检测，使用 self.get_header() 获取表头数据。

        Note:
            - 默认第一行为表头
            - 返回字典的键为传入的列名，值为布尔值（True 表示存在，False 表示不存在）
            - 当表头有相同的重复名字时，从左到右默认取第一个

        Args:
            col_names: 需要检测的列名数组

        Returns:
            字典，键为列名，值为布尔值，表示该列是否存在

        Example:
            >>> sheet.check_columns_exist(["姓名", "年龄", "不存在的列"])
            >>> # 返回: {"姓名": True, "年龄": True, "不存在的列": False}
        """
        header = self.get_header()
        return {col_name: col_name in header for col_name in col_names}

    def has_columns(self, col_names: List[str]) -> bool:
        """
        检测指定的所有列名是否都存在于表头中。

        该方法基于表头（第一行）进行检测，使用 self.get_header() 获取表头数据。
        只有当所有列名都存在时才返回 True，否则返回 False。

        Note:
            - 默认第一行为表头
            - 当表头有相同的重复名字时，从左到右默认取第一个
            - 如果需要知道具体哪些列存在/不存在，请使用 check_columns_exist() 方法

        Args:
            col_names: 需要检测的列名数组

        Returns:
            bool: 所有列名都存在返回 True，否则返回 False

        Example:
            >>> sheet.has_columns(["姓名", "年龄"])
            >>> # 返回: True（如果两列都存在）
            >>>
            >>> sheet.has_columns(["姓名", "不存在的列"])
            >>> # 返回: False（因为"不存在的列"不存在）
        """
        header = self.get_header()
        return all(col_name in header for col_name in col_names)

    # -------------------------------------- 写操作 --------------------------------------------

    def _convert_data_to_grid(
        self,
        data: List[Union[List[Any], Dict[str, Any]]],
        header: List[str],
        write_row: int
    ) -> Tuple[List[List[Any]], List[str], int]:
        """
        将字典/列表格式的数据统一转换为二维数组。

        Args:
            data: 输入数据，支持字典数组或二维数组
            header: 当前表头
            write_row: 起始行号

        Returns:
            (二维数组, 实际表头, 表头长度)
        """
        heads_len = len(header)

        # 处理写入第一行的情况（表头行）
        if write_row == 1:
            if not isinstance(data[0], list):
                raise ValueError(
                    "此方法依赖表头，无法覆盖写入第一行，如有需要，请将写入数组的第一个元素设置为数组类型表示为表头。"
                    "或者使用 write() 方法。"
                )
            if isinstance(data[0], list):
                header = data[0]
                heads_len = len(header)

        # 将数据转换为二维数组
        write_list = []
        for row in data:
            if isinstance(row, dict):
                write_list.append([row.get(col_name) for col_name in header])
            elif isinstance(row, list):
                row = (row + [None] * heads_len)[:heads_len]  # 对齐数组长度
                write_list.append(row)
            else:
                raise ValueError(f"需要写入的值可以是二维数组、数组[字典]。当前数组元素类型是: {type(row)}")

        return write_list, header, heads_len
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

    def delete_columns_by_name(
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
        if end_col_name is None:
            end_col_name = start_col_name

        start_col_index = self.get_index_by_col_name(start_col_name)
        end_col_index = self.get_index_by_col_name(end_col_name)

        return self.delete_series(start_col_index, end_col_index, "COLUMNS")

    def write_column(
        self,
        column_name: str,
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

    def append_to_column(
        self,
        column_name: str,
        data_list: List[Any]
    ):
        """向指定列中写入数据，如果列中已有值，则追加写入"""

        # 0. 此预处理是考虑到边界条件，如果原本此列已有值，需要追加。要将此列所有 None 改变为 ''
        col_letter = self.get_letter_by_col_name(column_name)
        total_row = self.get_sheet_info()["rowCount"]
        data = self.read(f'{col_letter}1:{col_letter}{total_row}', value_render_option='UnformattedValue')
        data.reverse()

        blank_row_num = 0
        for d in data:
            if d[0] is not None:
                break
            blank_row_num += 1
        end_row_num = total_row - blank_row_num  # 获取最后一个有效数据的行数

        # 1. 将 None 转化为 '' 字符串可以适配飞书 接口往后追加数据
        data_list = [[d] if d is not None else ['']
                     for d in data_list]

        # 2. 检查列是否存在。考虑此函数使用场景是向已有列中追加数据
        #    所以不自动创建，以免造成不明确的预期
        if column_name not in self.header:
            raise FeiShuColumnNotExist(column_name, f' 列不存在，请检查，先创建后写入')

        # 3. 写入数据
        sheet_range = f'{col_letter}{end_row_num}:{col_letter}{len(data_list)+end_row_num-1}'
        self.append(sheet_range, data_list)

    def write_row(
        self,
        data: List[Union[List[Any], Dict[str, Any]]],
        write_row: int = 2,
        skip_none: bool = True,
        partition_strategy: Literal['horizontal', 'vertical', 'auto'] = 'auto'
    ):
        """
        写入一行或多行数据，支持智能跳过 None 值。

        该方法是最强大的行写入方法，支持：
        - 字典和列表两种数据格式
        - 可选的 None 值跳过功能（避免覆盖已有数据）
        - 使用批量写入 API，性能优秀
        - 自动数据分区优化

        Note:
            - 如果是字典则会根据列名（默认列的第一个单元格）写入，列不存在填 None
            - 二维数组的第一个索引值代表行，第二个索引值代表行中单元格的值
            - 当 skip_none=True 时，只写入非 None 的数据，不会用 None 覆盖单元格
            - 当 skip_none=False（默认）时，会用 None 覆盖对应的单元格，保持向后兼容
            - 当 write_row=1 且第一个元素是列表时，该列表作为新表头

        Args:
            data: 需要写入的值，可以是二维数组或字典数组
                - 字典格式: [{"列名1": 值1, "列名2": 值2}, ...]
                - 列表格式: [[值1, 值2, ...], [值3, 值4, ...], ...]
                - 混合模式: [{"列名1": 值1, "列名2": 值2}, [值1, 值2, ...], ...]
                - 当 write_row=1 且第一个元素是列表时，该列表作为新表头
            write_row: 要写入的起始行（默认从第2行开始）
            skip_none: 是否跳过 None 值（默认 True）
                - False: 会用 None 覆盖单元格（传统行为）
                - True: 只写入非 None 数据，不覆盖单元格中的 None
            partition_strategy: 数据分区策略，仅在 skip_none=True 时生效（默认 'auto'）
                - 'horizontal': 优先横向分割
                - 'vertical': 优先纵向分割
                - 'auto': 自动选择分割数量最少的策略

        Example:
            >>> # 示例1: 传统用法（覆盖 None）
            >>> sheet.write_row([
            >>>     {"姓名": "张三", "年龄": 25, "部门": None},
            >>>     {"姓名": "李四", "年龄": None, "部门": "技术部"}
            >>> ], write_row=2)
            >>> # None 会清空对应单元格
            >>>
            >>> # 示例2: 智能模式（跳过 None）
            >>> sheet.write_row([
            >>>     {"姓名": "张三", "年龄": 25, "部门": None},
            >>>     {"姓名": "李四", "年龄": None, "部门": "技术部"}
            >>> ], write_row=2, skip_none=True)
            >>> # 只会写入 "张三", 25, "李四", "技术部"，不会覆盖 None 位置
            >>>
            >>> # 示例3: 列表格式
            >>> sheet.write_row([
            >>>     [1, None, 3],
            >>>     [4, 5, None]
            >>> ], write_row=5, skip_none=True)
        """
        # 1. 获取表头
        header = self.header

        # 2. 处理 write_row=1 的特殊情况
        if write_row == 1:
            if not isinstance(data[0], list):
                raise ValueError(
                    "此方法依赖表头，无法覆盖写入第一行，如有需要，请将写入数组的第一个元素设置为数组类型表示为表头。"
                    "或者使用 write() 方法。"
                )
            # 第一个元素作为新表头
            header = data[0]
            self.write(f'A1:{num_to_excel_col(len(header))}1', [header])
            # 如果只有表头，直接返回
            if len(data) == 1:
                return
            # 继续处理剩余数据
            data = data[1:]
            write_row = 2

        # 3. 构造表头范围并写入数据
        hang_header_range = f'A1:{num_to_excel_col(len(header))}1'
        self.write_row_by_hang_header(
            hang_header_range=hang_header_range,
            data=data,
            write_row=write_row,
            skip_none=skip_none,
            partition_strategy=partition_strategy
        )

    def write_row_by_hang_header(
        self,
        hang_header_range: str,
        data: List[Union[List[Any], Dict[str, Any]]],
        write_row: int = 2,
        skip_none: bool = True,
        partition_strategy: Literal['horizontal', 'vertical', 'auto'] = 'auto'
    ):
        """
        根据指定的"悬挂表头"写入行数据。即：可以指定任意一行范围内的数据为临时表头，并按照此表头写入数据。

        该方法支持：
        - 字典和列表两种数据格式
        - 可选的 None 值跳过功能（避免覆盖已有数据）

        Note:
            - 当 skip_none=True（默认）时，只写入非 None 的数据，不会用 None 覆盖单元格
            - 当 skip_none=False 时，会用 None 覆盖对应的单元格，保持向后兼容

        Args:
            hang_header_range: 悬挂头的范围（ 如：C22:JK22, DF345:DL345 ），一个行范围，多行报错
            data: 需要写入的值可以是二维数组、数组[字典]
                - 字典格式: [{"列名1": 值1, "列名2": 值2}, ...]
                - 列表格式: [[值1, 值2, ...], [值3, 值4, ...], ...]
                - 混合模式: [{"列名1": 值1, "列名2": 值2}, [值1, 值2, ...], ...]
            write_row: 相对于悬挂头来说的开始行数，悬挂头为第 1 行，默认开始从第 2 行写入
            skip_none: 是否跳过 None 值（默认 True，保持向后兼容）
                - False: 会用 None 覆盖单元格（传统行为）
                - True: 只写入非 None 数据，不覆盖单元格中的 None
            partition_strategy: 数据分区策略，仅在 skip_none=True 时生效（默认 'auto'）
                - 'horizontal': 优先横向分割
                - 'vertical': 优先纵向分割
                - 'auto': 自动选择分割数量最少的策略

        Example:
            >>> # 示例1: 传统用法（覆盖 None）
            >>> sheet.write_row_by_hang_header(
            >>>     "C2:E2",
            >>>     [{"姓名": "张三", "年龄": 25, "部门": None}],
            >>>     write_row=2
            >>> )
            >>>
            >>> # 示例2: 智能模式（跳过 None）
            >>> sheet.write_row_by_hang_header(
            >>>     "C2:E2",
            >>>     [{"姓名": "张三", "年龄": 25, "部门": None}],
            >>>     write_row=2,
            >>>     skip_none=True
            >>> )
        """
        if write_row <= 1:
            raise ValueError(f"write_row 参数必须大于1")

        # 1. 判断行的范围是否正确
        a, b = match_row_num_by_range(hang_header_range)
        if a != b:
            raise ValueError(f"hang_header 参数单元格范围表示应该为一行数据的范围，如：A2:F2。当前为：{hang_header_range}")
        actual_write_row = int(a) + write_row - 1  # 写入数据相对于表头的偏移量

        # 2. 校验输入 range 正确
        start_col, end_col = match_col_letter_by_range(hang_header_range)
        start_col_num = excel_col_to_num(start_col)
        end_col_num = excel_col_to_num(end_col)
        if end_col_num < start_col_num:
            raise ValueError(f"输入 hang_header 数据范围有误，当前 {end_col} 比 {start_col} 要小，输入数据: {hang_header_range}")

        # 3. 获取行的内容作为临时表头
        header = self.read_human(hang_header_range)[0]

        # 4. 将数据按照表头对齐（复用公共方法）
        write_list, _, heads_len = self._convert_data_to_grid(data, header, write_row=2)  # write_row>1 避免表头处理逻辑

        # 5. 如果 skip_none=False，使用传统方式（直接写入全部数据）
        if not skip_none:
            cell_range = f'{start_col}{actual_write_row}:{end_col}{len(write_list) + actual_write_row - 1}'
            self.write(cell_range, write_list)
            return

        # 6. skip_none=True 时，使用智能分区批量写入
        # 使用 partition_grid 将数据分成多个矩形区域
        rectangles = partition_grid(write_list, strategy=partition_strategy)

        if not rectangles:
            # 没有有效数据，直接返回
            return

        # 7. 将矩形区域转换为批量写入格式
        ranges_data = []
        for rect in rectangles:
            top_left = rect['top_left']  # (row_idx, col_idx)
            bottom_right = rect['bottom_right']
            values = rect['values']

            # 计算实际的行列位置（相对于 actual_write_row 和 start_col）
            rect_start_row = actual_write_row + top_left[0]
            rect_end_row = actual_write_row + bottom_right[0]
            rect_start_col = num_to_excel_col(start_col_num + top_left[1])
            rect_end_col = num_to_excel_col(start_col_num + bottom_right[1])

            # 构造范围字符串
            range_str = f"{rect_start_col}{rect_start_row}:{rect_end_col}{rect_end_row}"

            # 如果是横向矩形，values 是一维数组，需要转为二维
            if rect['type'] == 'horizontal':
                values = [values]

            ranges_data.append({
                "range": range_str,
                "values": values
            })

        # 8. 使用批量写入 API
        self.write_batch(ranges_data)

    def insert_column_to_right(
        self,
        column_letter: str,
        insert_number: int = 1,
        inherit_style: bool = True,
    ):
        """向指定列右边插入指定数量的空列，inherit_style 为 True 表示插入列是否复制起始列的单元格样式。"""
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

    def read_column(self, column_name: str, read_method: Callable[str, List[List[Any]]] = None) -> List[Any]:
        """
        根据列名读取对应列的所有数据，返回一维数组。
        """
        if read_method is None:
            read_method = self.read_human
        col_index = self.get_index_by_col_name(column_name)
        col_letter = num_to_excel_col(col_index)
        data = read_method(f'{col_letter}2:{col_letter}{self.get_sheet_info()["rowCount"]}')
        return [row[0] for row in data]

    def read_row(
        self,
        row_number: int,
        full_row: bool = False,
        read_method: Callable[str, List[List[Any]]] = None
    ) -> Dict[str, Any]:
        """
        读取指定单行的数据，返回字典格式。

        注意：此方法只读取单行数据，不支持行范围读取。
        如需读取多行，请使用 read() 方法读取范围，或使用 iterrows() 方法流式读取。

        根据 full_row 参数决定读取整行还是只读取和表头等长的数据：
        - full_row=False（默认）: 只读取和表头等长的列数据
        - full_row=True: 读取整行所有有数据的列

        返回字典的键规则：
        - 在表头范围内的列：
          - 如果表头有值（使用 cell_is_blank 检查），使用表头名称作为键
          - 如果表头为空（None/空字符串/NaN），使用列字母索引作为键（A, B, C, ...）
        - 超出表头范围的列：使用列字母索引作为键（A, B, C, ...）

        Note:
            - row_number 从 1 开始计数，只能指定单个行号
            - 当 row_number=1 时，返回的字典键为列字母索引（因为第一行就是表头）
            - read_method 参数用于选择不同的读取方式（默认 read_human，可选 read_raw 等）

        Args:
            row_number: 要读取的行号（从 1 开始，必须是单个行号）
            full_row: 是否读取整行，False 表示只读和表头等长的列
            read_method: 读取单元格的方法引用，默认为 read_human
                - read_human: 人类可读方式（默认）
                - read_raw: 读取原始数据（含公式）
                - read: 基础读取方法

        Returns:
            字典，键为表头名称或列字母索引，值为对应单元格的值

        Example:
            >>> # 假设表头为 ["姓名", "年龄"]，读取第2行（只读表头范围）
            >>> sheet.read_row(2)
            >>> # 返回: {"姓名": "张三", "年龄": 25}
            >>>
            >>> # 读取第2行（包含表头范围外的列）
            >>> sheet.read_row(2, full_row=True)
            >>> # 返回: {"姓名": "张三", "年龄": 25, "C": "备注", "D": "其他"}
            >>>
            >>> # 读取第1行（表头行）
            >>> sheet.read_row(1)
            >>> # 返回: {"A": "姓名", "B": "年龄"}
            >>>
            >>> # 使用 read_raw 读取公式
            >>> sheet.read_row(3, read_method=sheet.read_raw)
            >>> # 返回: {"姓名": "李四", "年龄": "=B2+1"}
        """
        if read_method is None:
            read_method = self.read_human

        # 获取表格信息
        sheet_info = self.get_sheet_info()
        total_columns = sheet_info["columnCount"]

        # 确定读取的列范围
        if full_row:
            # 读取整行
            end_col = num_to_excel_col(total_columns)
        else:
            # 只读和表头等长的列
            header_len = len(self.get_header())
            end_col = num_to_excel_col(header_len)

        # 构造读取范围并读取数据
        range_str = f"A{row_number}:{end_col}{row_number}"
        data = read_method(range_str)
        row_data = data[0] if data else []

        # 构造返回字典
        result = {}

        if row_number == 1:
            # 第一行是表头，使用列字母索引作为键
            for i, value in enumerate(row_data):
                col_letter = num_to_excel_col(i + 1)
                result[col_letter] = value
        else:
            # 非表头行，使用表头名称或列字母索引作为键
            header = self.get_header()
            for i, value in enumerate(row_data):
                if i < len(header):
                    # 在表头范围内
                    header_value = header[i]
                    if not cell_is_blank(header_value):
                        # 表头有值，使用表头名称
                        result[header_value] = value
                    else:
                        # 表头为空（None/空字符串/NaN），使用列字母索引
                        col_letter = num_to_excel_col(i + 1)
                        result[col_letter] = value
                else:
                    # 超出表头范围，使用列字母索引
                    col_letter = num_to_excel_col(i + 1)
                    result[col_letter] = value

        return result

    def read_rows(
        self,
        row_numbers: List[int],
        full_row: bool = False,
        read_method: Callable[str, List[List[Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        批量读取指定多行的数据，返回字典数组。

        该方法内部使用 read_batch API 一次性读取多个行范围，相比多次调用 read_row 方法性能更高。

        根据 full_row 参数决定读取整行还是只读取和表头等长的数据：
        - full_row=False（默认）: 只读取和表头等长的列数据
        - full_row=True: 读取整行所有有数据的列

        返回字典的键规则（与 read_row 一致）：
        - 在表头范围内的列：
          - 如果表头有值，使用表头名称作为键
          - 如果表头为空（None/空字符串/NaN），使用列字母索引作为键（A, B, C, ...）
        - 超出表头范围的列：使用列字母索引作为键（A, B, C, ...）

        Note:
            - row_numbers 中的行号从 1 开始计数
            - 当某行号为 1 时，该行返回的字典键为列字母索引（因为第一行就是表头）
            - 返回数组的顺序与 row_numbers 的顺序一致
            - read_method 参数用于选择不同的读取方式（默认 read_human，可选 read_raw 等）
            - 该接口返回数据的最大限制为 10 MB

        Args:
            row_numbers: 要读取的行号列表（从 1 开始），例如 [2, 3, 5, 10]
            full_row: 是否读取整行，False 表示只读和表头等长的列
            read_method: 读取单元格的方法引用，默认为 read_human
                - read_human: 人类可读方式（默认）
                - read_raw: 读取原始数据（含公式）
                - read: 基础读取方法

        Returns:
            字典数组，每个字典表示一行数据。
            字典的键为表头名称或列字母索引，值为对应单元格的值。

        Example:
            >>> # 假设表头为 ["姓名", "年龄"]，批量读取第2、3、5行
            >>> sheet.read_rows([2, 3, 5])
            >>> # 返回: [
            >>> #     {"姓名": "张三", "年龄": 25},
            >>> #     {"姓名": "李四", "年龄": 30},
            >>> #     {"姓名": "王五", "年龄": 28}
            >>> # ]
            >>>
            >>> # 读取包含表头范围外的列
            >>> sheet.read_rows([2, 3], full_row=True)
            >>> # 返回: [
            >>> #     {"姓名": "张三", "年龄": 25, "C": "备注1"},
            >>> #     {"姓名": "李四", "年龄": 30, "C": "备注2"}
            >>> # ]
            >>>
            >>> # 使用 read_raw 读取公式
            >>> sheet.read_rows([2, 3], read_method=sheet.read_raw)
            >>> # 返回: [
            >>> #     {"姓名": "张三", "年龄": "=B1+1"},
            >>> #     {"姓名": "李四", "年龄": "=B2+1"}
            >>> # ]
        """
        if not row_numbers:
            return []

        if read_method is None:
            read_method = self.read_human

        # 确定读取的列范围
        # get_header() 内部已有缓存机制且读取的是完整列范围
        end_col = num_to_excel_col(len(self.get_header()))

        # 构造多个范围字符串
        ranges = [f"A{row_num}:{end_col}{row_num}" for row_num in row_numbers]

        # 根据 read_method 选择底层调用方式
        # read_method 是 FeiShuSheet 的方法，内部会调用 FeiShuRequest 的方法
        # 我们需要直接使用 FeiShuRequest 的 read_batch 方法
        # 但为了兼容 read_method 参数（可能是 read_human/read_raw/read），
        # 我们需要判断 value_render_option

        # 根据 read_method 判断使用哪种渲染选项
        if read_method == self.read_raw:
            value_render_option = "Formula"
        else:
            value_render_option = "ToString"

        # 调用 Operations 层的 read_batch 方法（带权限控制）
        data = self.read_batch(ranges, value_render_option=value_render_option)

        # 解析返回数据（使用之前缓存的 header）
        result = []

        for i, value_range in enumerate(data["valueRanges"]):
            row_data = value_range["values"][0] if value_range.get("values") else []
            row_number = row_numbers[i]

            # 构造返回字典（与 read_row 逻辑一致）
            row_dict = {}

            if row_number == 1:
                # 第一行是表头，使用列字母索引作为键
                for j, value in enumerate(row_data):
                    col_letter = num_to_excel_col(j + 1)
                    row_dict[col_letter] = value
            else:
                # 非表头行，使用表头名称或列字母索引作为键
                header = self.get_header()
                for j, value in enumerate(row_data):
                    if j < len(header):
                        # 在表头范围内
                        header_value = header[j]
                        if not cell_is_blank(header_value):
                            # 表头有值，使用表头名称
                            row_dict[header_value] = value
                        else:
                            # 表头为空（None/空字符串/NaN），使用列字母索引
                            col_letter = num_to_excel_col(j + 1)
                            row_dict[col_letter] = value
                    else:
                        # 超出表头范围，使用列字母索引
                        col_letter = num_to_excel_col(j + 1)
                        row_dict[col_letter] = value

            result.append(row_dict)

        return result

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
        return_type: Type[Union[List[Any], Dict[str, Any]]] = dict,
        columns: Optional[List[str]] = None,  # 指定读取的列
        read_method: Callable[str, List[List[Any]]] = None,
    ) -> Generator[Union[tuple[int, dict[str, Any]], tuple[int, list[Any]]], None, None]:
        """
        流式迭代读取飞书表格每一行，像本地列表一样使用，内存安全。

        自动控制每次请求数据量 < 10MB（飞书实际限制更严格，保守估计）
        推荐 batch_size=500（根据实际情况适当调节，可加快遍历速度）

        Note:
            - 如果 start_row >= 2 且 return_type=dict，则返回 dict，第一行作为表头。
            - 如果 start_row == 1 且 return_type=dict，则返回 dict，表头使用 Excel 列字母索引。
            - 如果 return_type=list，则返回 list，没有表头。
            - columns 参数可以指定读取哪些列，支持列名或列字母索引，大幅减少数据传输量。
            - read_method 方法引用是为了满足不同的读单元表格内容

        Example:
            >>> # 读取所有列
            >>> for index, row in sheet.iterrows(start_row=2):
            >>>     print(index, row["姓名"], row["年龄"])  # dict 模式
            >>>
            >>> # 只读取指定列（节省带宽和内存）
            >>> for index, row in sheet.iterrows(columns=["CaseID", "query"]):
            >>>     print(index, row["CaseID"], row["query"])
            >>>
            >>> # 使用列字母索引
            >>> for index, row in sheet.iterrows(columns=["A", "B", "D"]):
            >>>     print(index, row)
            >>>
            >>> # list 模式
            >>> for index, row in sheet.iterrows(start_row=1, return_type=list):
            >>>     print(index, row[0], row[1])

        Args:
            start_row: 数据起始行（含），默认 2（跳过表头）
            end_row: 结束行（含），None 表示读到最后
            batch_size: 每次读取行数，默认 500
            return_type: 返回类型，可以是 list 或 dict，默认 dict
            columns: 指定要读取的列，支持列名（如 'CaseID'）或列字母（如 'A'），None 表示读取所有列
            read_method: 读取 sheet 单元格的方法引用，可以是此类方法的 read, read_human（默认）, read_raw（可以返回公式）

        Returns:
            生成器，每行是 (索引, 数据) 元组，数据为 dict 或 list
        """

        if read_method is None:
            read_method = self.read_human
        info = self.get_sheet_info()
        max_row = end_row or info["rowCount"]

        if start_row > max_row:
            # TODO 加日志打印
            print(f"警告: 开始处理行 start_row ({start_row}) 比现有数据行数 max_row ({max_row}) 更大. 没有行数据可处理")
            return

        # 确定要读取的列和对应的表头
        full_header = None
        if return_type == dict or columns is not None:
            if start_row >= 2:
                full_header = self.get_header()
            else:
                full_header = [num_to_excel_col(i + 1) for i in range(info["columnCount"])]

        # 处理 columns 参数：计算要读取的列索引和对应的表头
        if columns is None:
            # 读取所有列
            col_indices = list(range(1, info["columnCount"] + 1))
            selected_header = full_header if full_header else []
            col_letters = [num_to_excel_col(i) for i in col_indices]
        else:
            # 只读取指定列
            col_indices = []
            selected_header = []

            for col in columns:
                if isinstance(col, str) and col.isalpha() and col.isupper():
                    # 列字母（如 'A', 'B', 'AA'）
                    col_idx = excel_col_to_num(col)
                    col_indices.append(col_idx)
                    if full_header and col_idx <= len(full_header):
                        selected_header.append(full_header[col_idx - 1])
                    else:
                        selected_header.append(col)
                else:
                    # 列名（如 'CaseID', 'query'）
                    col_idx = self.get_index_by_col_name(col)
                    col_indices.append(col_idx)
                    selected_header.append(col)

            col_letters = [num_to_excel_col(i) for i in col_indices]

        # 优化读取策略：判断列是否连续
        is_continuous = len(col_indices) > 1 and all(
            col_indices[i] + 1 == col_indices[i + 1] for i in range(len(col_indices) - 1)
        )

        current_row = start_row

        while current_row <= max_row:
            batch_end = min(current_row + batch_size - 1, max_row)

            try:
                if columns is None:
                    # 读取所有列（原有逻辑）
                    range_str = f"A{current_row}:{num_to_excel_col(info['columnCount'])}{batch_end}"
                    batch_data = read_method(range_str)
                elif is_continuous:
                    # 连续列：使用单个范围读取
                    start_col = col_letters[0]
                    end_col = col_letters[-1]
                    range_str = f"{start_col}{current_row}:{end_col}{batch_end}"
                    batch_data = read_method(range_str)
                else:
                    # 离散列：使用 read_batch 读取多个单列范围
                    ranges = [f"{col}{current_row}:{col}{batch_end}" for col in col_letters]

                    # 根据 read_method 选择合适的 value_render_option
                    if read_method == self.read_raw:
                        value_render_option = "Formula"
                    else:
                        value_render_option = "ToString"

                    batch_result = self.read_batch(ranges, value_render_option=value_render_option)

                    # 将 read_batch 的结果转换为标准格式
                    # batch_result["valueRanges"] 是一个数组，每个元素对应一个列范围
                    batch_data = []
                    num_rows = len(batch_result["valueRanges"][0].get("values", []))

                    for row_idx in range(num_rows):
                        row = []
                        for col_range in batch_result["valueRanges"]:
                            values = col_range.get("values", [])
                            if row_idx < len(values) and len(values[row_idx]) > 0:
                                row.append(values[row_idx][0])
                            else:
                                row.append(None)
                        batch_data.append(row)

            except Exception as e:
                raise FeiShuException(f"读取行 {current_row}~{batch_end} 失败，错误: {e}")

            if not batch_data:
                break

            # 构造每一行
            for row_values in batch_data:
                if not row_values:  # 跳过空行
                    current_row += 1
                    continue

                if return_type == dict:
                    # dict 模式：字段名访问，补空对齐
                    padded = (row_values + [""] * len(selected_header))[: len(selected_header)]
                    yield current_row, dict(zip(selected_header, padded))
                else:
                    # list 模式：直接返回行数据
                    yield current_row, row_values

                current_row += 1
            if batch_end >= max_row:
                break
