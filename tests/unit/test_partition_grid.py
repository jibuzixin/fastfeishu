"""
Grid分区算法的单元测试

测试 fastfeishu/utils/partition_grid.py 中的智能分区算法。
"""

import pytest
from fastfeishu.utils.partition_grid import partition_grid


@pytest.mark.unit
class TestPartitionGrid:
    """Grid分区算法测试"""

    def test_partition_empty_grid(self):
        """测试空网格"""
        result = partition_grid([])
        assert result == []

        result = partition_grid([[]])
        assert result == []

    def test_partition_all_none(self):
        """测试全是None的网格"""
        grid = [
            [None, None, None],
            [None, None, None]
        ]
        result = partition_grid(grid)
        assert result == []

    def test_partition_single_cell(self):
        """测试单个单元格"""
        grid = [[1]]
        result = partition_grid(grid, strategy='horizontal')

        assert len(result) == 1
        assert result[0]['values'] == [1]
        assert result[0]['top_left'] == (0, 0)
        assert result[0]['bottom_right'] == (0, 0)

    def test_partition_horizontal_row(self):
        """测试横向连续行"""
        grid = [
            [1, 2, 3, None],
            [None, None, None, None],
        ]
        result = partition_grid(grid, strategy='horizontal')

        assert len(result) == 1
        assert result[0]['type'] == 'horizontal'
        assert result[0]['values'] == [1, 2, 3]
        assert result[0]['top_left'] == (0, 0)
        assert result[0]['bottom_right'] == (0, 2)

    def test_partition_vertical_column(self):
        """测试纵向连续列"""
        grid = [
            [1, None],
            [2, None],
            [3, None],
        ]
        result = partition_grid(grid, strategy='vertical')

        assert len(result) >= 1
        # 找到纵向矩形
        vertical_rect = [r for r in result if r.get('type') == 'vertical']
        assert len(vertical_rect) >= 1
        # vertical 类型的 values 是二维列表 [[1], [2], [3]]
        assert vertical_rect[0]['values'] == [[1], [2], [3]]

    def test_partition_sparse_grid(self, sample_grid_with_none):
        """测试稀疏网格"""
        result = partition_grid(sample_grid_with_none, strategy='auto')

        # 应该能够分区，且没有重叠
        assert len(result) > 0

        # 验证所有非None值都被包含
        all_values = []
        for rect in result:
            values = rect['values']
            # 扁平化 values（可能是一维或二维列表）
            if isinstance(values[0], list):
                # vertical 类型：二维列表 [[1], [2]]
                for row in values:
                    all_values.extend(row)
            else:
                # horizontal 类型：一维列表 [1, 2]
                all_values.extend(values)

        expected_values = [1, 3, 5, 7, 8, 11]
        assert sorted(all_values) == sorted(expected_values)

    def test_partition_auto_strategy_chooses_best(self):
        """测试auto策略选择最优方案"""
        # 创建一个横向优势明显的网格
        grid = [
            [1, 2, 3, 4, 5],
            [None, None, None, None, None],
            [6, 7, 8, 9, 10],
        ]

        result_auto = partition_grid(grid, strategy='auto')
        result_horizontal = partition_grid(grid, strategy='horizontal')
        result_vertical = partition_grid(grid, strategy='vertical')

        # auto应该选择矩形数量较少的策略
        assert len(result_auto) <= min(len(result_horizontal), len(result_vertical))

    def test_partition_mixed_pattern(self):
        """测试混合模式网格"""
        grid = [
            [1, 2, None, 4],
            [None, None, None, 5],
            [6, None, None, 6],
        ]

        result = partition_grid(grid, strategy='horizontal')

        # 验证没有遗漏值
        all_values = []
        for rect in result:
            values = rect['values']
            # 扁平化 values（可能是一维或二维列表）
            if isinstance(values[0], list):
                # vertical 类型：二维列表
                for row in values:
                    all_values.extend(row)
            else:
                # horizontal 类型：一维列表
                all_values.extend(values)

        expected = [1, 2, 4, 5, 6, 6]
        assert sorted(all_values) == sorted(expected)

    def test_partition_full_grid(self):
        """测试完整网格（无None）"""
        grid = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
        ]

        result_h = partition_grid(grid, strategy='horizontal')
        result_v = partition_grid(grid, strategy='vertical')

        # 横向策略应该产生3个横向矩形
        assert len(result_h) == 3
        assert all(r['type'] == 'horizontal' for r in result_h)

        # 纵向策略应该产生3个纵向矩形
        assert len(result_v) == 3
        assert all(r['type'] == 'vertical' for r in result_v)

    def test_partition_coordinates_correct(self):
        """测试分区坐标正确性"""
        grid = [
            [1, 2, None],
            [3, 4, None],
        ]

        result = partition_grid(grid, strategy='vertical')

        # 找到第一列的矩形
        for rect in result:
            if rect['top_left'][1] == 0:  # 第一列
                assert rect['top_left'] == (0, 0)
                if len(rect['values']) == 2:
                    assert rect['bottom_right'] == (1, 0)
                    # vertical 类型的 values 是二维列表 [[1], [3]]
                    assert rect['values'] == [[1], [3]]
