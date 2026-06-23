from ..core.interface import FeiShuInterface, IterableSheetProtocol
from fastfeishu.helpers import num_to_excel_col, match_col_letter_by_range, match_row_num_by_range, excel_col_to_num
from typing import Optional, Callable, List, Dict, Any, Union
import pandas as pd

class FeiShuUtil:

    @classmethod
    def process_rows_to_new_sheet(
        cls,
        source_sheet: IterableSheetProtocol,  # 源   sheet
        target_sheet: FeiShuInterface,  # 目标 sheet
        start_row: int = 2,  # 数据起始行（含），默认跳过表头
        end_row: Optional[int] = None,  # 数据结束行（含），None=全部
        row_handler: Callable[[Union[pd.Series, Dict[str, Any]]], List[Dict[str, Any]]] = lambda row: [row],
        batch_write: int = 2000,  # 每批写多少行
    ) -> FeiShuInterface:
        """
            分批读取源 sheet 的数据，通过 row_handler 处理每一行数据，然后分批写入目标 sheet。

            Args:
                source_sheet (IterableSheetProtocol): 源 sheet，支持逐行迭代。
                target_sheet (FeiShuInterface): 目标 sheet，支持写入操作。
                start_row (int, optional): 数据起始行（含），默认为 2，跳过表头。
                end_row (Optional[int], optional): 数据结束行（含），默认为 None，表示处理全部行。
                row_handler (Callable[[Union[pd.Series, Dict[str, Any]]], List[Dict[str, Any]]]): 每行数据的处理函数，
                    接收一行数据作为输入，返回一个包含字典的列表，每个字典代表一行数据。
                    默认为将每行数据转换为字典。
                batch_read (int, optional): 每批读取的行数，默认为 1000。
                batch_write (int, optional): 每批写入的行数，默认为 2000。

            Returns:
                FeiShuInterface: 目标 sheet 实例，已完成数据写入。

            Note:
                - 确保 source_sheet 和 target_sheet 的接口符合 IterableSheetProtocol 和 FeiShuInterface。
                - row_handler 函数的返回值必须是列表，即使只处理一行数据。
                - 如果数据量较大，建议调整 batch_read 和 batch_write 的值以优化性能。
                - 没有表头的数据将会缺失，并不能完完整整复制全部数据，如果需要请确保所有表头都存在

            See Also:
                IterableSheetProtocol: 源 sheet 的协议定义。
                FeiShuInterface: 目标 sheet 的接口定义。
            """

        header_written = False
        buffer: List[Dict[str, Any]] = []  # 待写入的缓冲

        for index, row in source_sheet.iterrows(
            start_row=start_row,
            end_row=end_row,
        ):
            outs = row_handler(row,)
            buffer.extend(outs)

            if len(buffer) >= batch_write:
                FeiShuUtil._flush_to_sheet(target_sheet, buffer, header_written)
                header_written = True
                buffer.clear()

        # 最后残余
        if buffer:
            FeiShuUtil._flush_to_sheet(target_sheet, buffer, header_written)
        return target_sheet

    @classmethod
    def _flush_to_sheet(
        cls, sheet: FeiShuInterface, rows: List[Dict[str, Any]], header_exist: bool
    ):
        """配合 process_rows_to_new_sheet 方法把缓冲写 sheet"""
        if not rows:
            return
        data = [list(r.values()) for r in rows]
        col_count = len(data[0])

        if not header_exist:
            header = [list(rows[0].keys())]
            sheet.write(f"A1:{num_to_excel_col(col_count)}1", header)
            sheet.write(f"A2:{num_to_excel_col(col_count)}{len(data)+1}", data)
        else:
            placeholder = f"A1:{num_to_excel_col(col_count)}{len(data)}"
            sheet.append(placeholder, data)

    @classmethod
    def replace_placeholder(cls, sheet: FeiShuInterface, sheet_range: str, **kwargs):
        """
        将 sheet_range 范围内中出现的占位符替换为传入的键值对。

        使用批量写入 API，只更新包含占位符的单元格，性能更好。

        Args:
            sheet: FeiShuInterface 实例，用于读写操作
            sheet_range: 要处理的单元格范围，如 "A1:C10"
            **kwargs: 占位符的键值对，用于替换占位符

        Example:
            >>> # 假设单元格中有 "Hello {name}, you are {age} years old"
            >>> FeiShuUtil.replace_placeholder(sheet, "A1:B2", name="Alice", age=30)
            >>> # 结果: "Hello Alice, you are 30 years old"
        """
        # 1. 读取原始数据
        read_range = sheet.read_raw(sheet_range)

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
            sheet.write_batch(ranges_data)
