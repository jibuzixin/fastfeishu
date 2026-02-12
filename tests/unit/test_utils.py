"""
工具函数的单元测试

测试 fastfeishu/utils/ 中的工具函数。
"""

import pytest
from fastfeishu.utils.common import (
    num_to_excel_col,
    excel_col_to_num,
    match_row_num_by_range,
    match_col_letter_by_range
)


@pytest.mark.unit
class TestCommonUtils:
    """通用工具函数测试"""

    def test_num_to_excel_col(self):
        """测试数字转Excel列字母"""
        assert num_to_excel_col(1) == "A"
        assert num_to_excel_col(26) == "Z"
        assert num_to_excel_col(27) == "AA"
        assert num_to_excel_col(52) == "AZ"
        assert num_to_excel_col(53) == "BA"
        assert num_to_excel_col(702) == "ZZ"
        assert num_to_excel_col(703) == "AAA"

    def test_excel_col_to_num(self):
        """测试Excel列字母转数字"""
        assert excel_col_to_num("A") == 1
        assert excel_col_to_num("Z") == 26
        assert excel_col_to_num("AA") == 27
        assert excel_col_to_num("AZ") == 52
        assert excel_col_to_num("BA") == 53
        assert excel_col_to_num("ZZ") == 702
        assert excel_col_to_num("AAA") == 703

    def test_excel_col_conversion_roundtrip(self):
        """测试数字和字母转换的往返一致性"""
        for num in [1, 10, 26, 27, 100, 702, 703]:
            col = num_to_excel_col(num)
            assert excel_col_to_num(col) == num

    def test_match_row_num_by_range(self):
        """测试从范围提取行号"""
        # 简单范围
        start, end = match_row_num_by_range("A1:B2")
        assert start == "1"
        assert end == "2"

        # 单个单元格
        start, end = match_row_num_by_range("C5:C5")
        assert start == "5"
        assert end == "5"

        # 大行号
        start, end = match_row_num_by_range("A100:Z200")
        assert start == "100"
        assert end == "200"

    def test_match_col_letter_by_range(self):
        """测试从范围提取列字母"""
        # 简单范围
        start, end = match_col_letter_by_range("A1:C3")
        assert start == "A"
        assert end == "C"

        # 多字母列
        start, end = match_col_letter_by_range("AA10:AZ20")
        assert start == "AA"
        assert end == "AZ"

        # 单列
        start, end = match_col_letter_by_range("B1:B100")
        assert start == "B"
        assert end == "B"

    def test_case_insensitive_col_letter(self):
        """测试列字母大小写不敏感"""
        assert excel_col_to_num("a") == 1
        assert excel_col_to_num("z") == 26
        assert excel_col_to_num("aa") == 27
        assert excel_col_to_num("aZ") == 52
