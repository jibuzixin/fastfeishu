"""
单元格类型的单元测试

测试特殊单元格类型（TextLink, Email, Formula等）。
"""

import pytest
from fastfeishu.models.type import TextLink, Email, Formula


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
