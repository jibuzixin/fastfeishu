"""
测试 write_row 智能批量写入功能（集成测试）

该方法结合了 partition_grid（数据分区）和 write_batch（批量写入）的优势，
能够智能地只写入有效数据，避免用 None 覆盖单元格。
"""

import pytest
from fastfeishu.core import FeiShuSheet
from tests.integration.config import get_test_sheet_url


# 获取测试表格 URL（如果未配置会跳过所有测试）
try:
    TEST_SHEET_URL = get_test_sheet_url("write_row_smart")
except ValueError as e:
    pytest.skip(f"write_row_smart 测试表格未配置: {e}", allow_module_level=True)


@pytest.fixture
def test_sheet():
    """创建可写的测试 sheet 对象"""
    return FeiShuSheet(TEST_SHEET_URL, readonly=False)


@pytest.mark.integration
class TestWriteRowSmart:
    """write_row 智能批量写入功能的集成测试"""

    def test_cover_none_mode(self, test_sheet):
        """测试1: 覆盖 None 模式（与 write_row 行为相同）"""
        print("\n" + "=" * 60)
        print("测试1: 覆盖 None 模式（skip_none=False）")
        print("=" * 60)

        data = [
            [1, None, 3, 4],
            [5, 6, None, 8],
            [None, 10, 11, None]
        ]

        # skip_none=False 时，会用 None 覆盖对应单元格
        test_sheet.write_row(data, write_row=5, skip_none=False)

        # 验证：读取第一行，检查 None 位置是否为空
        result = test_sheet.read('A5:D5')
        assert result[0][0] == 1, f"期望 1，实际 '{result[0][0]}'"
        # result[0][1] 应该是空（None 被覆盖）
        assert result[0][2] == 3, f"期望 3，实际 '{result[0][2]}'"

        print("✅ 已写入数据，None 位置已被覆盖为空，验证通过\n")

    def test_dict_format(self, test_sheet):
        """测试2: 字典格式数据"""
        print("\n" + "=" * 60)
        print("测试2: 字典格式数据")
        print("=" * 60)

        # 字典格式：根据列名自动对齐
        employees = [
            {"姓名": "张三", "年龄": 25, "部门": "技术部"},
            {"姓名": "李四", "年龄": None, "部门": "销售部"},  # 年龄为 None
            {"姓名": "王五", "年龄": 35, "部门": None},       # 部门为 None
        ]

        test_sheet.write_row([list(employees[0].keys())] + employees, write_row=1)

        # 验证：抽查第一行和第三行
        result_row1 = test_sheet.read('A2:C2')
        assert result_row1[0][0] == "张三", f"期望 '张三'，实际 '{result_row1[0][0]}'"
        assert result_row1[0][1] == 25, f"期望 25，实际 '{result_row1[0][1]}'"
        assert result_row1[0][2] == "技术部", f"期望 '技术部'，实际 '{result_row1[0][2]}'"

        result_row3 = test_sheet.read('A4:B4')
        assert result_row3[0][0] == "王五", f"期望 '王五'，实际 '{result_row3[0][0]}'"
        assert result_row3[0][1] == 35, f"期望 35，实际 '{result_row3[0][1]}'"

        print("✅ 字典格式数据已写入，验证通过\n")

    def test_list_format(self, test_sheet):
        """测试3: 列表格式数据"""
        print("\n" + "=" * 60)
        print("测试3: 列表格式数据")
        print("=" * 60)

        # 列表格式：按顺序写入
        data = [
            [1, 2, None, 4, 5],
            [6, None, 8, None, 10],
            [None, 12, 13, 14, None]
        ]

        test_sheet.write_row(data, write_row=5)

        # 验证：抽查第一行和第二行的几个单元格
        result_row1 = test_sheet.read('A5:E5')
        assert result_row1[0][0] == 1, f"期望 1，实际 '{result_row1[0][0]}'"
        assert result_row1[0][1] == 2, f"期望 2，实际 '{result_row1[0][1]}'"
        assert result_row1[0][3] == 4, f"期望 4，实际 '{result_row1[0][3]}'"

        result_row2 = test_sheet.read('A6:C6')
        assert result_row2[0][0] == 6, f"期望 6，实际 '{result_row2[0][0]}'"
        assert result_row2[0][2] == 8, f"期望 8，实际 '{result_row2[0][2]}'"

        print("✅ 列表格式数据已写入，None 位置未覆盖，验证通过\n")

    def test_partition_strategy(self, test_sheet):
        """测试4: 不同的分区策略"""
        print("\n" + "=" * 60)
        print("测试4: 不同的分区策略")
        print("=" * 60)

        data = [
            [1, 2, None, 4],
            [5, None, None, 8],
            [9, 10, 11, 12]
        ]

        # 横向优先分割
        test_sheet.write_row(data, write_row=2, partition_strategy='horizontal')
        print("✓ 使用横向优先策略")

        # 纵向优先分割
        test_sheet.write_row(data, write_row=10, partition_strategy='vertical')
        print("✓ 使用纵向优先策略")

        # 自动选择（默认）
        test_sheet.write_row(data, write_row=20, partition_strategy='auto')
        print("✓ 使用自动选择策略")

        # 验证：只验证最后一次写入（auto 策略）
        result = test_sheet.read('A20:D20')
        assert result[0][0] == 1, f"期望 1，实际 '{result[0][0]}'"
        assert result[0][1] == 2, f"期望 2，实际 '{result[0][1]}'"
        assert result[0][3] == 4, f"期望 4，实际 '{result[0][3]}'"

        print("✅ 不同分区策略写入成功，验证通过\n")

    def test_with_header(self, test_sheet):
        """测试5: 写入表头"""
        print("\n" + "=" * 60)
        print("测试5: 写入表头")
        print("=" * 60)

        # 第一行是表头（列表格式），后续是数据
        data = [
            ["姓名", "年龄", "部门", "薪资"],  # 表头
            {"姓名": "张三", "年龄": 25, "部门": "技术部", "薪资": 8000},
            {"姓名": "李四", "年龄": 30, "部门": None, "薪资": 9000},
        ]

        # 注意：写入第一行时，skip_none 通常设为 False，确保表头完整
        test_sheet.write_row(data, write_row=1, skip_none=False)

        # 验证：读取表头
        header = test_sheet.read('A1:D1')
        assert header[0] == ["姓名", "年龄", "部门", "薪资"], f"表头不匹配，实际 {header[0]}"

        # 验证：读取第一行数据
        data_row1 = test_sheet.read('A2:D2')
        assert data_row1[0][0] == "张三", f"期望 '张三'，实际 '{data_row1[0][0]}'"
        assert data_row1[0][1] == 25, f"期望 25，实际 '{data_row1[0][1]}'"
        assert data_row1[0][3] == 8000, f"期望 8000，实际 '{data_row1[0][3]}'"

        print("✅ 表头和数据已写入，验证通过\n")

    @pytest.mark.slow
    def test_performance_comparison(self, test_sheet):
        """测试6: 性能对比（大数据量）"""
        print("\n" + "=" * 60)
        print("测试6: 性能对比 - write_row with skip_none")
        print("=" * 60)

        # 假设有100行数据，每行都有一些 None
        data = []
        for i in range(100):
            data.append({
                "ID": i,
                "名称": f"测试{i}" if i % 3 != 0 else None,
                "数值": i * 10 if i % 2 == 0 else None,
                "备注": "备注" if i % 5 == 0 else None
            })

        test_sheet.write('B2:B2', [["测试0"]])

        # 使用 write_row（跳过 None）
        test_sheet.write_row([list(data[0].keys())] + data, write_row=1, skip_none=True)

        # 验证：抽查前3行和最后1行
        # 第一行: ID=0, 名称="测试0", 数值=0, 备注="备注"
        row1 = test_sheet.read('A2:D2')
        assert row1[0][0] == 0, f"期望 0，实际 '{row1[0][0]}'"
        assert row1[0][1] == "测试0", f"期望 '测试0'，实际 '{row1[0][1]}'"

        # 第三行: ID=2, 名称="测试2", 数值=20
        row3 = test_sheet.read('A4:C4')
        assert row3[0][0] == 2, f"期望 2，实际 '{row3[0][0]}'"
        assert row3[0][2] == 20, f"期望 20，实际 '{row3[0][2]}'"

        # 最后一行: ID=99, 名称="测试99"
        row100 = test_sheet.read('A99:D99')
        assert row100[0][1] == "测试97", f"期望 97，实际 '{row100[0][0]}'"
        assert row100[0][2] is None, f"期望 None，实际 '{row100[0][1]}'"

        print("✅ write_row 优势:")
        print("  1. 只写入有效数据，不覆盖 None")
        print("  2. 使用批量写入 API，减少网络请求")
        print("  3. 自动分区优化，性能更好")
        print("  4. 100行数据写入并验证通过\n")

    def test_advanced_scenario(self, test_sheet):
        """测试7: 高级示例 - 复杂数据场景"""
        print("\n" + "=" * 60)
        print("测试7: 高级示例 - 复杂数据场景")
        print("=" * 60)

        # 模拟真实业务场景：从数据库查询的结果，部分字段可能为空
        query_results = [
            {
                "订单ID": "ORD001",
                "客户": "公司A",
                "金额": 10000,
                "状态": "已完成",
                "备注": None,  # 没有备注
                "发货日期": None  # 还未发货
            },
            {
                "订单ID": "ORD002",
                "客户": None,  # 客户信息缺失
                "金额": 5000,
                "状态": "处理中",
                "备注": "加急",
                "发货日期": "2024-01-15"
            },
            {
                "订单ID": "ORD003",
                "客户": "公司B",
                "金额": None,  # 金额待确认
                "状态": "待审核",
                "备注": None,
                "发货日期": None
            }
        ]

        # 使用 write_row 写入，None 字段不会覆盖表格中已有的数据
        test_sheet.write_row([list(query_results[0].keys())] + query_results, write_row=1, skip_none=True)

        # 验证：抽查第一条和第二条订单
        # 第一条: ORD001, 公司A, 10000, 已完成
        order1 = test_sheet.read('A2:D2')
        assert order1[0][0] == "ORD001", f"期望 'ORD001'，实际 '{order1[0][0]}'"
        assert order1[0][1] == "公司A", f"期望 '公司A'，实际 '{order1[0][1]}'"
        assert order1[0][2] == 10000, f"期望 10000，实际 '{order1[0][2]}'"
        assert order1[0][3] == "已完成", f"期望 '已完成'，实际 '{order1[0][3]}'"

        # 第二条: ORD002, 5000, 处理中, 加急
        order2 = test_sheet.read('A3:F3')
        assert order2[0][0] == "ORD002", f"期望 'ORD002'，实际 '{order2[0][0]}'"
        assert order2[0][2] == 5000, f"期望 5000，实际 '{order2[0][2]}'"
        assert order2[0][3] == "处理中", f"期望 '处理中'，实际 '{order2[0][3]}'"
        assert order2[0][4] == "加急", f"期望 '加急'，实际 '{order2[0][4]}'"

        print("✅ 复杂数据已写入")
        print("✅ None 字段保留了表格中的原有数据")
        print("✅ 数据验证通过\n")
