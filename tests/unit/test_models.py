"""
SheetProperties 和相关模型的单元测试

测试 Builder 模式和属性配置。
"""

import pytest
from fastfeishu.models.sheet_properties import SheetProperties, Protect


@pytest.mark.unit
class TestSheetProperties:
    """SheetProperties 模型测试"""

    def test_protect_builder(self):
        """测试 Protect Builder 模式"""
        protect = Protect.builder() \
            .lock(True) \
            .lock_info("测试锁定") \
            .build()

        assert protect.lock == "LOCK"
        assert protect.lock_info == "测试锁定"

    def test_sheet_properties_builder_basic(self):
        """测试 SheetProperties Builder 基本功能"""
        props = SheetProperties.builder() \
            .title("测试Sheet") \
            .index(0) \
            .hidden(False) \
            .build()

        assert props.title == "测试Sheet"
        assert props.index == 0
        assert props.hidden is False

    def test_sheet_properties_builder_frozen(self):
        """测试冻结行列配置"""
        props = SheetProperties.builder() \
            .frozen_row_count(2) \
            .frozen_col_count(3) \
            .build()

        assert props.frozen_row_count == 2
        assert props.frozen_col_count == 3

    def test_sheet_properties_builder_with_protect(self):
        """测试带保护的Sheet配置"""
        protect = Protect.builder() \
            .lock(True) \
            .lock_info("只读保护") \
            .build()

        props = SheetProperties.builder() \
            .title("受保护的Sheet") \
            .protect(protect) \
            .build()

        assert props.title == "受保护的Sheet"
        assert props.protect is not None
        assert props.protect.lock == "LOCK"
        assert props.protect.lock_info == "只读保护"

    def test_sheet_properties_builder_full_config(self):
        """测试完整配置"""
        protect = Protect.builder() \
            .lock(True) \
            .lock_info("完整保护") \
            .build()

        props = SheetProperties.builder() \
            .title("完整配置Sheet") \
            .index(5) \
            .hidden(True) \
            .frozen_row_count(1) \
            .frozen_col_count(2) \
            .protect(protect) \
            .build()

        assert props.title == "完整配置Sheet"
        assert props.index == 5
        assert props.hidden is True
        assert props.frozen_row_count == 1
        assert props.frozen_col_count == 2
        assert props.protect.lock == "LOCK"

    def test_builder_method_chaining(self):
        """测试Builder方法链式调用"""
        # 确保所有方法都返回builder实例
        builder = SheetProperties.builder()

        result = builder \
            .title("测试") \
            .index(0) \
            .hidden(False) \
            .frozen_row_count(1) \
            .frozen_col_count(1)

        # result 应该仍然是 builder 实例
        assert result is not None

        # 能够最终 build
        props = result.build()
        assert props.title == "测试"
