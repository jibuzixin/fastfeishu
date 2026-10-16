"""
单元格类型的单元测试

测试特殊单元格类型（TextLink, Email, Formula等）。
"""

import pytest
from fastfeishu.models.type import TextLink, NotTextLink, Email, Formula


@pytest.mark.unit
class TestCellTypes:
    """单元格类型测试"""

    def test_text_link_creation(self):
        """测试创建文本链接"""
        link = TextLink("https://example.com", "示例链接").to_json()

        assert link['link'] == "https://example.com"
        assert link['text'] == "示例链接"
        assert link['type'] == "url"

    def test_email_creation(self):
        """测试创建邮箱类型"""
        email = Email("test@example.com")

        assert email.text == "test@example.com"

    def test_formula_creation(self):
        """测试创建公式"""
        formula = Formula("=SUM(A1:A10)").to_json()

        assert formula['text'] == "=SUM(A1:A10)"
        assert formula['type'] == "formula"

    def test_text_link_with_chinese(self):
        """测试包含中文的文本链接"""
        link = TextLink("https://example.com/中文路径", "中文链接")

        assert link.link == "https://example.com/中文路径"
        assert link.text == "中文链接"

    def test_formula_with_complex_expression(self):
        """测试复杂公式"""
        formula = Formula("=IF(A1>10, SUM(B1:B10), AVERAGE(C1:C10))").to_json()

        assert "IF" in formula['text']
        assert "SUM" in formula['text']
        assert "AVERAGE" in formula['text']


@pytest.mark.unit
class TestCellTypeConverter:
    """批量类型转换测试"""

    def test_auto_convert_recognizes_types(self):
        """自动识别文本类型"""
        from fastfeishu.models.type import CellTypeConverter

        assert isinstance(CellTypeConverter.auto_convert("=A1+B1"), Formula)
        assert isinstance(CellTypeConverter.auto_convert("https://example.com"), NotTextLink)
        assert isinstance(CellTypeConverter.auto_convert("test@example.com"), Email)

    def test_auto_convert_passes_through_primitives(self):
        """数字/布尔/None 原样返回，不会被包装成单元格类型"""
        from fastfeishu.models.type import CellTypeConverter

        assert CellTypeConverter.auto_convert(123) == 123
        assert CellTypeConverter.auto_convert(1.5) == 1.5
        assert CellTypeConverter.auto_convert(None) is None

    def test_auto_convert_to_json_handles_primitives(self):
        """回归：非单元格类型不应因缺少 to_json() 而崩溃"""
        from fastfeishu.models.type import CellTypeConverter

        assert CellTypeConverter.auto_convert_to_json("=A1+B1")['type'] == 'formula'
        assert CellTypeConverter.auto_convert_to_json(123) == 123
        assert CellTypeConverter.auto_convert_to_json(None) is None

    def test_from_table_returns_cell_types(self):
        """回归：from_table 不应调用不存在的 from_list_to_type"""
        from fastfeishu.models.type import CellTypeConverter

        result = CellTypeConverter.from_table([["=A1+B1", "test@example.com"]])

        assert isinstance(result[0][0], Formula)
        assert isinstance(result[0][1], Email)

    def test_from_table_to_json_returns_json(self):
        """回归：from_table_to_json 必须返回 JSON 而非单元格对象"""
        from fastfeishu.models.type import CellTypeConverter

        result = CellTypeConverter.from_table_to_json([["=A1+B1", 123]])

        assert result[0][0]['type'] == 'formula'
        assert result[0][1] == 123

    def test_from_list_to_json_with_numbers(self):
        """回归：含裸数字的列表转 JSON 不应抛 AttributeError"""
        from fastfeishu.models.type import CellTypeConverter

        result = CellTypeConverter.from_list_to_json(["=A1+B1", 123, None])

        assert result[0]['type'] == 'formula'
        assert result[1] == 123
        assert result[2] is None

    def test_from_dict_single_mapping(self):
        """from_dict 接收单个 dict"""
        from fastfeishu.models.type import CellTypeConverter

        result = CellTypeConverter.from_dict({"formula": "=A1+B1", "num": 5})

        assert isinstance(result["formula"], Formula)
        assert result["num"] == 5

    def test_validate_email_disabled(self):
        """关闭邮箱校验时不识别为 Email"""
        from fastfeishu.models.type import CellTypeConverter

        result = CellTypeConverter.auto_convert("not-an-email", validate_email=False)

        assert not isinstance(result, Email)
