"""
fastfeishu.helpers 模块的单元测试

测试纯工具函数，包括 base64 转换、JSON 提取等功能。
"""

import pytest
import tempfile
import os
from fastfeishu.helpers import (
    base64_image,
    extract_json_content,
)


@pytest.mark.unit
class TestBase64Image:
    """base64_image 函数的测试"""

    def test_base64_from_file_path(self):
        """测试从文件路径转换"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            test_data = b"test image data"
            f.write(test_data)
            temp_path = f.name

        try:
            result = base64_image(temp_path)

            # 验证返回的是字符串
            assert isinstance(result, str)
            # 验证可以解码回原始数据
            import base64
            decoded = base64.b64decode(result)
            assert decoded == test_data
        finally:
            # 清理临时文件
            os.unlink(temp_path)

    def test_base64_from_bytes(self):
        """测试从字节数据转换"""
        test_data = b"test image data"
        result = base64_image(test_data)

        # 验证返回的是字符串
        assert isinstance(result, str)
        # 验证可以解码回原始数据
        import base64
        decoded = base64.b64decode(result)
        assert decoded == test_data

    def test_base64_empty_bytes(self):
        """测试空字节数据"""
        result = base64_image(b"")
        assert result == ""

    def test_base64_special_characters(self):
        """测试包含特殊字符的数据"""
        test_data = b"\x00\x01\x02\xff\xfe\xfd"
        result = base64_image(test_data)

        import base64
        decoded = base64.b64decode(result)
        assert decoded == test_data


@pytest.mark.unit
class TestExtractJsonContent:
    """extract_json_content 函数的测试"""

    def test_extract_json_default_tags(self):
        """测试使用默认标签提取 JSON"""
        input_str = "Some text <json>{\"key\": \"value\"}</json> more text"
        result = extract_json_content(input_str)
        assert result == "{\"key\": \"value\"}"

    def test_extract_json_with_whitespace(self):
        """测试带空白字符的 JSON"""
        input_str = "<json>\n    {\"key\": \"value\"}\n</json>"
        result = extract_json_content(input_str)
        assert result == "{\"key\": \"value\"}"

    def test_extract_json_custom_tags(self):
        """测试自定义标签"""
        input_str = "text ```json\n{\"data\": 123}\n``` end"
        result = extract_json_content(input_str, start_flag="```json", end_flag="```")
        assert result == "{\"data\": 123}"

    def test_extract_json_no_match(self):
        """测试没有匹配的标签"""
        input_str = "just plain text without tags"
        result = extract_json_content(input_str)
        assert result is None

    def test_extract_json_incomplete_tags(self):
        """测试不完整的标签"""
        input_str = "<json>incomplete"
        result = extract_json_content(input_str)
        assert result is None

    def test_extract_json_multiple_matches(self):
        """测试多个匹配（应返回第一个）"""
        input_str = "<json>first</json> text <json>second</json>"
        result = extract_json_content(input_str)
        assert result == "first"

    def test_extract_json_multiline(self):
        """测试多行 JSON"""
        input_str = """<json>
{
    "name": "test",
    "value": 123,
    "nested": {
        "key": "value"
    }
}
</json>"""
        result = extract_json_content(input_str)
        assert "name" in result
        assert "nested" in result

    def test_extract_json_empty_content(self):
        """测试空内容"""
        input_str = "<json></json>"
        result = extract_json_content(input_str)
        assert result == ""

    def test_extract_json_special_characters(self):
        """测试包含特殊字符的内容"""
        input_str = '<json>{"text": "包含中文和特殊字符!@#$%"}</json>'
        result = extract_json_content(input_str)
        assert "包含中文" in result
