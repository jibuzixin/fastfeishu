"""
fastfeishu.utils.feishu_util 模块的单元测试

测试 FeiShuUtil 工具类的功能。
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from fastfeishu.utils.feishu_util import FeiShuUtil


@pytest.mark.unit
class TestFeiShuUtil:
    """FeiShuUtil 工具类的测试"""

    def test_flush_to_sheet_first_time(self):
        """测试首次写入（需要写表头）"""
        mock_sheet = Mock()
        mock_sheet.write = Mock()
        mock_sheet.append = Mock()

        rows = [
            {"姓名": "张三", "年龄": 25},
            {"姓名": "李四", "年龄": 30}
        ]

        FeiShuUtil._flush_to_sheet(mock_sheet, rows, header_exist=False)

        # 应该调用 write 两次：一次写表头，一次写数据
        assert mock_sheet.write.call_count == 2

        # 第一次调用：写表头
        first_call = mock_sheet.write.call_args_list[0]
        assert first_call[0][0] == "A1:B1"  # 范围
        assert first_call[0][1] == [["姓名", "年龄"]]  # 表头

        # 第二次调用：写数据
        second_call = mock_sheet.write.call_args_list[1]
        assert second_call[0][0] == "A2:B3"  # 范围
        assert second_call[0][1] == [["张三", 25], ["李四", 30]]  # 数据

    def test_flush_to_sheet_append_mode(self):
        """测试追加模式（表头已存在）"""
        mock_sheet = Mock()
        mock_sheet.write = Mock()
        mock_sheet.append = Mock()

        rows = [
            {"姓名": "王五", "年龄": 35}
        ]

        FeiShuUtil._flush_to_sheet(mock_sheet, rows, header_exist=True)

        # 应该调用 append
        mock_sheet.append.assert_called_once()
        call_args = mock_sheet.append.call_args
        assert call_args[0][0] == "A1:B1"  # placeholder 范围
        assert call_args[0][1] == [["王五", 35]]  # 数据

        # 不应该调用 write
        mock_sheet.write.assert_not_called()

    def test_flush_to_sheet_empty_rows(self):
        """测试空行（不执行任何操作）"""
        mock_sheet = Mock()
        mock_sheet.write = Mock()
        mock_sheet.append = Mock()

        FeiShuUtil._flush_to_sheet(mock_sheet, [], header_exist=False)

        # 不应该调用任何方法
        mock_sheet.write.assert_not_called()
        mock_sheet.append.assert_not_called()

    def test_flush_to_sheet_multiple_columns(self):
        """测试多列数据"""
        mock_sheet = Mock()
        mock_sheet.write = Mock()

        rows = [
            {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}
        ]

        FeiShuUtil._flush_to_sheet(mock_sheet, rows, header_exist=False)

        # 验证列数正确
        first_call = mock_sheet.write.call_args_list[0]
        assert first_call[0][0] == "A1:E1"  # 5列

    def test_process_rows_to_new_sheet_basic(self):
        """测试基本的行处理功能"""
        # 模拟源 sheet
        mock_source = Mock()
        mock_source.iterrows = Mock(return_value=[
            (2, {"姓名": "张三", "年龄": 25}),
            (3, {"姓名": "李四", "年龄": 30})
        ])

        # 模拟目标 sheet
        mock_target = Mock()
        mock_target.write = Mock()
        mock_target.append = Mock()

        # 修正：使用正确的处理函数（接收元组）
        def handler(row):
            index, data = row
            return [data]

        result = FeiShuUtil.process_rows_to_new_sheet(
            source_sheet=mock_source,
            target_sheet=mock_target,
            row_handler=handler,
            start_row=2
        )

        # 应该返回目标 sheet
        assert result == mock_target

        # 验证 iterrows 被调用
        mock_source.iterrows.assert_called_once_with(
            start_row=2,
            end_row=None
        )

    def test_process_rows_to_new_sheet_with_handler(self):
        """测试使用自定义行处理函数"""
        # 模拟源 sheet
        mock_source = Mock()
        mock_source.iterrows = Mock(return_value=[
            (2, {"姓名": "张三", "年龄": 25}),
            (3, {"姓名": "李四", "年龄": 30})
        ])

        # 模拟目标 sheet
        mock_target = Mock()
        mock_target.write = Mock()
        mock_target.append = Mock()

        # 自定义处理函数：将年龄加10
        def custom_handler(row):
            index, data = row
            data = data.copy()
            data["年龄"] = data["年龄"] + 10
            return [data]

        with patch.object(FeiShuUtil, '_flush_to_sheet') as mock_flush:
            FeiShuUtil.process_rows_to_new_sheet(
                source_sheet=mock_source,
                target_sheet=mock_target,
                row_handler=custom_handler,
                start_row=2,
                batch_write=1000
            )

            # 验证 flush 被调用
            assert mock_flush.called

    def test_process_rows_to_new_sheet_batch_write(self):
        """测试分批写入功能"""
        # 模拟源 sheet - 返回5行数据
        rows_data = [(i, {"col": i}) for i in range(2, 7)]
        mock_source = Mock()
        mock_source.iterrows = Mock(return_value=rows_data)

        # 模拟目标 sheet
        mock_target = Mock()

        # 修正：使用正确的处理函数
        def handler(row):
            index, data = row
            return [data]

        with patch.object(FeiShuUtil, '_flush_to_sheet') as mock_flush:
            # 设置 batch_write=2，应该触发多次 flush
            FeiShuUtil.process_rows_to_new_sheet(
                source_sheet=mock_source,
                target_sheet=mock_target,
                row_handler=handler,
                start_row=2,
                batch_write=2
            )

            # 5行数据，batch_write=2，应该调用 3 次 flush（2+2+1）
            assert mock_flush.call_count == 3

    def test_process_rows_to_new_sheet_empty_source(self):
        """测试空源数据"""
        mock_source = Mock()
        mock_source.iterrows = Mock(return_value=[])

        mock_target = Mock()

        with patch.object(FeiShuUtil, '_flush_to_sheet') as mock_flush:
            result = FeiShuUtil.process_rows_to_new_sheet(
                source_sheet=mock_source,
                target_sheet=mock_target
            )

            # 空数据不应该调用 flush
            mock_flush.assert_not_called()
            assert result == mock_target

    def test_process_rows_to_new_sheet_handler_returns_multiple(self):
        """测试处理函数返回多行数据（一行扩展为多行）"""
        mock_source = Mock()
        mock_source.iterrows = Mock(return_value=[
            (2, {"姓名": "张三", "年龄": 25})
        ])

        mock_target = Mock()

        # 处理函数：将一行扩展为两行
        def expand_handler(row):
            index, data = row
            return [
                {"姓名": data["姓名"], "类型": "原始"},
                {"姓名": data["姓名"], "类型": "复制"}
            ]

        with patch.object(FeiShuUtil, '_flush_to_sheet') as mock_flush:
            FeiShuUtil.process_rows_to_new_sheet(
                source_sheet=mock_source,
                target_sheet=mock_target,
                row_handler=expand_handler,
                batch_write=1000
            )

            # 验证 flush 被调用，且缓冲区有2行
            assert mock_flush.called
            call_args = mock_flush.call_args[0]
            buffer = call_args[1]
            assert len(buffer) == 2
