"""
测试 iterrows 方法的 columns 参数功能（集成测试）

此测试验证列选择功能在真实飞书表格上的表现。
"""

import pytest
from fastfeishu.core import FeiShuSheet
from tests.integration.config import get_test_sheet_url


# 获取测试表格 URL（如果未配置会跳过所有测试）
try:
    TEST_SHEET_URL = get_test_sheet_url("main")
except ValueError as e:
    pytest.skip(f"集成测试表格未配置: {e}", allow_module_level=True)


@pytest.fixture
def test_sheet():
    """创建只读的测试 sheet 对象"""
    return FeiShuSheet(TEST_SHEET_URL, readonly=True)


@pytest.mark.integration
class TestIterrowsColumns:
    """iterrows 列选择功能的集成测试"""

    def test_read_all_columns_default(self, test_sheet):
        """测试1: 读取所有列（默认行为）"""
        count = 0
        for index, row in test_sheet.iterrows(start_row=2, end_row=5):
            print(f"行 {index}: {list(row.keys())}")
            assert isinstance(row, dict), "应该返回字典"
            count += 1

        assert count > 0, "应该读取到数据"
        print(f"✅ 测试1通过：共读取 {count} 行\n")

    def test_read_specific_columns_by_name(self, test_sheet):
        """测试2: 只读取指定列（列名）"""
        # 假设表格有 'CaseID' 和 'query' 列
        # 如果没有，可以修改为实际存在的列名
        header = test_sheet.get_header()
        print(f"表头: {header}")

        if len(header) < 2:
            pytest.skip("表格列数不足，跳过此测试")

        # 选择前两列
        col1, col2 = header[0], header[1]

        count = 0
        for index, row in test_sheet.iterrows(start_row=2, end_row=5, columns=[col1, col2]):
            print(f"行 {index}: {row}")
            assert len(row) == 2, f"应该只有2列，实际: {len(row)}"
            assert col1 in row, f"应该包含 {col1}"
            assert col2 in row, f"应该包含 {col2}"
            count += 1

        print(f"✅ 测试2通过：共读取 {count} 行，只包含 {col1} 和 {col2}\n")

    def test_read_columns_by_letter(self, test_sheet):
        """测试3: 使用列字母索引"""
        count = 0
        for index, row in test_sheet.iterrows(start_row=2, end_row=5, columns=['A', 'B']):
            print(f"行 {index}: {row}")
            assert isinstance(row, dict), "应该返回字典"
            # 键可能是列名或列字母，取决于表头
            assert len(row) == 2, f"应该只有2列，实际: {len(row)}"
            count += 1

        print(f"✅ 测试3通过：共读取 {count} 行\n")

    def test_mixed_column_names_and_letters(self, test_sheet):
        """测试4: 混合使用列名和列字母"""
        header = test_sheet.get_header()
        if len(header) < 2:
            pytest.skip("表格列数不足，跳过此测试")

        # 使用第一列的列名和第三列的列字母
        col1_name = header[0]
        columns = [col1_name, 'B', 'D']

        count = 0
        for index, row in test_sheet.iterrows(start_row=2, end_row=5, columns=columns):
            print(f"行 {index}: {row}")
            assert len(row) == 3, f"应该只有3列，实际: {len(row)}"
            count += 1

        print(f"✅ 测试4通过：共读取 {count} 行\n")

    def test_discrete_columns_batch_optimization(self, test_sheet):
        """测试5: 离散列（测试批量读取优化）"""
        # 测试不连续的列，验证批量读取优化
        count = 0
        for index, row in test_sheet.iterrows(start_row=2, end_row=5, columns=['A', 'C', 'E']):
            print(f"行 {index}: {list(row.keys())}")
            assert len(row) == 3, f"应该只有3列，实际: {len(row)}"
            count += 1

        print(f"✅ 测试5通过：共读取 {count} 行（离散列）\n")

    def test_return_list_format(self, test_sheet):
        """测试6: 返回列表格式"""
        header = test_sheet.get_header()
        if len(header) < 2:
            pytest.skip("表格列数不足，跳过此测试")

        col1, col2 = header[0], header[1]

        count = 0
        for index, row in test_sheet.iterrows(
            start_row=2,
            end_row=5,
            columns=[col1, col2],
            return_type=list
        ):
            print(f"行 {index}: {row}")
            assert isinstance(row, list), "应该返回列表"
            assert len(row) == 2, f"应该有2个元素，实际: {len(row)}"
            count += 1

        print(f"✅ 测试6通过：共读取 {count} 行（列表格式）\n")

    @pytest.mark.slow
    def test_large_batch_with_columns(self, test_sheet):
        """测试7: 大批次读取（性能测试）"""
        header = test_sheet.get_header()
        if len(header) < 2:
            pytest.skip("表格列数不足，跳过此测试")

        col1, col2 = header[0], header[1]

        count = 0
        for index, row in test_sheet.iterrows(
            start_row=2,
            end_row=100,
            batch_size=1000,
            columns=[col1, col2]
        ):
            count += 1
            if count <= 3:  # 只打印前3行
                print(f"行 {index}: {row}")

        print(f"✅ 测试7通过：共读取 {count} 行（大批次）\n")

    def test_continuous_vs_discrete_columns(self, test_sheet):
        """测试8: 对比连续列和离散列的读取"""
        # 连续列
        continuous_count = 0
        for index, row in test_sheet.iterrows(start_row=2, end_row=5, columns=['A', 'B', 'C']):
            continuous_count += 1

        # 离散列
        discrete_count = 0
        for index, row in test_sheet.iterrows(start_row=2, end_row=5, columns=['A', 'C', 'E']):
            discrete_count += 1

        # 两种方式应该读取相同数量的行
        assert continuous_count == discrete_count, "连续列和离散列应读取相同行数"
        print(f"✅ 测试8通过：连续列和离散列都读取了 {continuous_count} 行\n")


@pytest.mark.integration
def test_iterrows_with_read_raw(test_sheet):
    """测试使用 read_raw 方法读取原始数据"""
    count = 0
    for index, row in test_sheet.iterrows(
        start_row=2,
        end_row=5,
        read_method=test_sheet.read_raw
    ):
        print(f"行 {index} (raw): {row}")
        count += 1

    assert count > 0, "应该读取到数据"
    print(f"✅ read_raw 测试通过：共读取 {count} 行\n")
