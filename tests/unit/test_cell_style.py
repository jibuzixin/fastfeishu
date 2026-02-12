"""
CellStyle 和 Font 模型的单元测试

测试 Builder 模式和样式配置功能。
"""

import pytest
from fastfeishu.models.cell_style import CellStyle, Font


@pytest.mark.unit
class TestFont:
    """Font 模型测试"""

    def test_font_builder_bold(self):
        """测试加粗样式"""
        font = Font.builder().bold().build()

        font_dict = font.to_dict()
        assert font_dict["bold"] is True

    def test_font_builder_italic(self):
        """测试斜体样式"""
        font = Font.builder().italic().build()

        font_dict = font.to_dict()
        assert font_dict["italic"] is True

    def test_font_builder_font_size(self):
        """测试字体大小"""
        font = Font.builder().font_size("12pt/1.5").build()

        font_dict = font.to_dict()
        assert font_dict["fontSize"] == "12pt/1.5"

    def test_font_builder_combined(self):
        """测试组合样式"""
        font = Font.builder() \
            .bold() \
            .italic() \
            .font_size("14pt/1.5") \
            .build()

        font_dict = font.to_dict()
        assert font_dict["bold"] is True
        assert font_dict["italic"] is True
        assert font_dict["fontSize"] == "14pt/1.5"

    def test_font_builder_method_chaining(self):
        """测试Builder方法链式调用"""
        builder = Font.builder()

        result = builder \
            .bold() \
            .italic() \
            .font_size("10pt/1.5")

        # result 应该仍然是 builder 实例
        assert result is not None

        # 能够最终 build
        font = result.build()
        assert font is not None


@pytest.mark.unit
class TestCellStyle:
    """CellStyle 模型测试"""

    def test_cell_style_builder_basic(self):
        """测试基础样式配置"""
        style = CellStyle.builder() \
            .fore_color("#000000") \
            .back_color("#21d11f") \
            .build()

        style_dict = style.to_dict()
        assert style_dict["foreColor"] == "#000000"
        assert style_dict["backColor"] == "#21d11f"

    def test_cell_style_builder_alignment(self):
        """测试对齐方式配置"""
        style = CellStyle.builder() \
            .h_align(1) \
            .v_align(2) \
            .build()

        style_dict = style.to_dict()
        assert style_dict["hAlign"] == 1
        assert style_dict["vAlign"] == 2

    def test_cell_style_builder_with_font(self):
        """测试带字体样式的配置"""
        font = Font.builder() \
            .bold() \
            .italic() \
            .font_size("12pt/1.5") \
            .build()

        style = CellStyle.builder() \
            .font(font) \
            .fore_color("#000000") \
            .back_color("#ffff00") \
            .build()

        style_dict = style.to_dict()
        assert "font" in style_dict
        assert style_dict["font"]["bold"] is True
        assert style_dict["font"]["italic"] is True
        assert style_dict["font"]["fontSize"] == "12pt/1.5"
        assert style_dict["foreColor"] == "#000000"
        assert style_dict["backColor"] == "#ffff00"

    def test_cell_style_builder_text_decoration(self):
        """测试文本装饰配置"""
        # 测试下划线 (1)
        style_underline = CellStyle.builder() \
            .text_decoration(1) \
            .build()

        style_dict = style_underline.to_dict()
        assert style_dict["textDecoration"] == 1

        # 测试删除线 (2)
        style_strikethrough = CellStyle.builder() \
            .text_decoration(2) \
            .build()

        style_dict = style_strikethrough.to_dict()
        assert style_dict["textDecoration"] == 2

    def test_cell_style_builder_border(self):
        """测试边框配置"""
        style = CellStyle.builder() \
            .border_type("FULL_BORDER") \
            .border_color("#ff0000") \
            .build()

        style_dict = style.to_dict()
        assert style_dict["borderType"] == "FULL_BORDER"
        assert style_dict["borderColor"] == "#ff0000"

    def test_cell_style_builder_full_config(self):
        """测试完整样式配置"""
        font = Font.builder() \
            .bold() \
            .italic() \
            .font_size("12pt/1.5") \
            .build()

        style = CellStyle.builder() \
            .font(font) \
            .fore_color("#000000") \
            .back_color("#21d11f") \
            .text_decoration(1) \
            .h_align(1) \
            .v_align(1) \
            .border_type("FULL_BORDER") \
            .border_color("#ff0000") \
            .build()

        style_dict = style.to_dict()

        # 验证所有属性
        assert "font" in style_dict
        assert style_dict["font"]["bold"] is True
        assert style_dict["font"]["italic"] is True
        assert style_dict["font"]["fontSize"] == "12pt/1.5"
        assert style_dict["foreColor"] == "#000000"
        assert style_dict["backColor"] == "#21d11f"
        assert style_dict["textDecoration"] == 1
        assert style_dict["hAlign"] == 1
        assert style_dict["vAlign"] == 1
        assert style_dict["borderType"] == "FULL_BORDER"
        assert style_dict["borderColor"] == "#ff0000"

    def test_cell_style_builder_method_chaining(self):
        """测试Builder方法链式调用"""
        builder = CellStyle.builder()

        result = builder \
            .fore_color("#000000") \
            .back_color("#ffffff") \
            .h_align(1) \
            .v_align(1) \
            .text_decoration(0) \
            .border_type("FULL_BORDER") \
            .border_color("#000000")

        # result 应该仍然是 builder 实例
        assert result is not None

        # 能够最终 build
        style = result.build()
        assert style is not None

    def test_cell_style_inline_font_builder(self):
        """测试内联字体Builder"""
        style = CellStyle.builder() \
            .font(Font.builder().bold().font_size("14pt/1.5").build()) \
            .back_color("#e6f2ff") \
            .h_align(1) \
            .border_type("FULL_BORDER") \
            .build()

        style_dict = style.to_dict()
        assert "font" in style_dict
        assert style_dict["font"]["bold"] is True
        assert style_dict["font"]["fontSize"] == "14pt/1.5"
        assert style_dict["backColor"] == "#e6f2ff"

    def test_alignment_values(self):
        """测试不同的对齐方式值"""
        # 左对齐，顶部对齐
        style_left_top = CellStyle.builder() \
            .h_align(0) \
            .v_align(0) \
            .build()

        style_dict = style_left_top.to_dict()
        assert style_dict["hAlign"] == 0
        assert style_dict["vAlign"] == 0

        # 居中对齐
        style_center = CellStyle.builder() \
            .h_align(1) \
            .v_align(1) \
            .build()

        style_dict = style_center.to_dict()
        assert style_dict["hAlign"] == 1
        assert style_dict["vAlign"] == 1

        # 右对齐，底部对齐
        style_right_bottom = CellStyle.builder() \
            .h_align(2) \
            .v_align(2) \
            .build()

        style_dict = style_right_bottom.to_dict()
        assert style_dict["hAlign"] == 2
        assert style_dict["vAlign"] == 2

    def test_to_dict_serialization(self):
        """测试 to_dict 序列化功能"""
        font = Font.builder() \
            .bold() \
            .italic() \
            .font_size("12pt/1.5") \
            .build()

        style = CellStyle.builder() \
            .font(font) \
            .fore_color("#000000") \
            .back_color("#21d11f") \
            .text_decoration(0) \
            .h_align(1) \
            .v_align(1) \
            .border_type("FULL_BORDER") \
            .border_color("#ff0000") \
            .build()

        # 转换为字典
        style_dict = style.to_dict()

        # 验证字典结构
        assert isinstance(style_dict, dict)
        assert "font" in style_dict
        assert isinstance(style_dict["font"], dict)

        # 验证可以被JSON序列化（通过dumps测试）
        import json
        json_str = json.dumps(style_dict, ensure_ascii=False)
        assert json_str is not None

        # 验证可以反序列化
        deserialized = json.loads(json_str)
        assert deserialized == style_dict
