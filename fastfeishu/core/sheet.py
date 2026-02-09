import pandas as pd

from fastfeishu.core.operations import FeiShuSheetOperations
from typing import Union, Any, Optional, List, Generator, Dict, Literal, Type, Tuple, Callable
from fastfeishu.utils import num_to_excel_col
from fastfeishu.exceptions.exception import FeiShuColumnNotExist, FeiShuException
from fastfeishu.core.interface import FeiShuInterface
from fastfeishu.utils.common import match_row_num_by_range, match_col_letter_by_range, excel_col_to_num
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
        例如：get_index_by_col_name("端到端回复") -> AC, 将会返回“端到端回复”列在 AC 列。

        :param col_name: 列名（列的第一行为列名）
        """
        return num_to_excel_col(self.get_index_by_col_name(col_name))
    
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

    def replace_placeholder(self, sheet_range: str, **kwargs):
        """
        将 sheet_range 范围内中出现的占位符替换为传入的键值对。

        使用批量写入 API，只更新包含占位符的单元格，性能更好。

        Args:
            sheet_range: 要处理的单元格范围，如 "A1:C10"
            **kwargs: 占位符的键值对，用于替换占位符

        Example:
            >>> # 假设单元格中有 "Hello {name}, you are {age} years old"
            >>> sheet.replace_placeholder("A1:B2", name="Alice", age=30)
            >>> # 结果: "Hello Alice, you are 30 years old"
        """
        # 1. 读取原始数据
        read_range = self.read_raw(sheet_range)

        # 2. 收集需要更新的单元格
        ranges_data = []

        # 解析起始位置
        start_col, _ = match_col_letter_by_range(sheet_range)
        start_row, _ = match_row_num_by_range(sheet_range)
        start_col_num = excel_col_to_num(start_col)
        start_row_num = int(start_row)

        # 3. 遍历数据，只对包含占位符的单元格进行替换
        for r, row in enumerate(read_range):
            for c, cell in enumerate(row):
                if cell is not None and isinstance(cell, str):
                    # 检查是否为纯占位符（如 {name}）
                    stripped = cell.strip()
                    if stripped.startswith('{') and stripped.endswith('}') and stripped.count('{') == 1:
                        # 纯占位符：直接替换为原始值（保持类型）
                        key = stripped[1:-1]
                        if key in kwargs:
                            actual_row = start_row_num + r
                            actual_col = num_to_excel_col(start_col_num + c)
                            range_str = f"{actual_col}{actual_row}:{actual_col}{actual_row}"
                            ranges_data.append({
                                "range": range_str,
                                "values": [[kwargs[key]]]  # 保持原始类型
                            })
                    else:
                        # 混合文本：使用 format（结果为字符串）
                        try:
                            formatted_value = cell.format(**kwargs)
                            if formatted_value != cell:
                                actual_row = start_row_num + r
                                actual_col = num_to_excel_col(start_col_num + c)
                                range_str = f"{actual_col}{actual_row}:{actual_col}{actual_row}"
                                ranges_data.append({
                                    "range": range_str,
                                    "values": [[formatted_value]]
                                })
                        except (KeyError, ValueError):
                            # 格式化失败，跳过
                            pass

        # 4. 使用批量写入 API 更新所有需要替换的单元格
        if ranges_data:
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

    def read_column(self, column_name: str) -> List[Any]:
        """
        根据列名读取对应列的所有数据，返回一维数组。
        """
        col_index = self.get_index_by_col_name(column_name)
        col_letter = num_to_excel_col(col_index)
        data = self.read_human(f'{col_letter}2:{col_letter}{self.get_sheet_info()["rowCount"]}')
        return [row[0] for row in data]
    
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
        header: Optional[List[str]] = None,  # 自定义表头
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
            - 用户可以通过 header 参数自定义表头。
            - read_method 方法引用是为了满足不同的读单元表格内容

        Example:
            >>> for index, row in sheet.iterrows(start_row=2):
            >>>     print(index, row["姓名"], row["年龄"])  # dict 模式
            >>> for index, row in sheet.iterrows(start_row=1, return_type=list):
            >>>     print(index, row[0], row[1])          # list 模式
            >>> for index, row in sheet.iterrows(start_row=1, return_type=dict):
            >>>     print(index, row["A"], row["B"])      # dict 模式，使用 Excel 列字母索引
            >>> for index, row in sheet.iterrows(start_row=1, return_type=dict, header=["姓名", "年龄"]):
            >>>     print(index, row["姓名"], row["年龄"])  # dict 模式，自定义表头

        Args:
            start_row: 数据起始行（含），默认 2（跳过表头）
            end_row: 结束行（含），None 表示读到最后
            batch_size: 每次读取行数，默认 500
            return_type: 返回类型，可以是 list 或 dict，默认 dict
            header: 自定义表头，可选
            read_method: 读取 sheet 单元格的方法引用，可以是此类方法的 read, read_huamn（默认）, read_raw（可以返回公式）

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

        if header is None and return_type == dict:
            if start_row >= 2:
                header = self.get_header()
            else:
                header = [num_to_excel_col(i + 1) for i in range(info["columnCount"])]  # 使用 Excel 列字母索引作为表头

        current_row = start_row

        while current_row <= max_row:
            batch_end = min(current_row + batch_size - 1, max_row)
            range_str = f"A{current_row}:{num_to_excel_col(info['columnCount'])}{batch_end}"

            try:
                batch_data = read_method(range_str)
            except Exception as e:
                raise FeiShuException(f"读取行 {current_row}~{batch_end} 失败，范围: {range_str}, 错误: {e}")

            if not batch_data:
                break

            # 构造每一行
            for row_values in batch_data:
                if not row_values:  # 跳过空行
                    current_row += 1
                    continue

                if return_type == dict:
                    # dict 模式：字段名访问，补空对齐
                    padded = (row_values + [""] * len(header))[: len(header)]
                    yield current_row, dict(zip(header, padded))
                else:
                    # list 模式：直接返回行数据
                    yield current_row, row_values

                current_row += 1
            if batch_end >= max_row:
                break
