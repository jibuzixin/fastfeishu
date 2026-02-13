"""
fastfeishu.utils.common 模块的单元测试

测试工具函数，包括采样、图片格式检测等功能。
"""

import pytest
from fastfeishu.utils.common import (
    sample_from_array,
    get_real_extension_from_bytes,
)


@pytest.mark.unit
class TestSampleFromArray:
    """sample_from_array 函数的测试"""

    def test_sample_none_config_default(self):
        """测试随机抽取1个（默认行为）"""
        labels = ['[安全]', '[涉政]', '[安全]', '[涉政]', '[其他]']
        result = sample_from_array(labels)

        # 应该返回一个列表（不是字典）
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] in labels

    def test_sample_none_config_with_max_samples(self):
        """测试随机抽取指定数量"""
        labels = ['[安全]', '[涉政]', '[安全]', '[涉政]', '[其他]']
        result = sample_from_array(labels, label_config=None, max_samples=3)

        assert isinstance(result, list)
        assert len(result) == 3
        # 所有抽取的标签都应该在原数组中
        for label in result:
            assert label in labels

    def test_sample_none_config_empty_array(self):
        """测试空数组"""
        result = sample_from_array([], label_config=None, max_samples=3)
        assert result == {}

    def test_sample_none_config_zero_count(self):
        """测试抽取0个"""
        labels = ['[安全]', '[涉政]']
        result = sample_from_array(labels, label_config=None, max_samples=0)
        assert result == {}

    def test_sample_dict_config_specific_labels(self):
        """测试按指定字典抽取"""
        labels = ['[安全]', '[涉政]', '[安全]', '[涉政]', '[其他]']
        result = sample_from_array(labels, label_config={'[安全]': 2, '[涉政]': 1})

        assert isinstance(result, dict)
        assert len(result['[安全]']) == 2
        assert len(result['[涉政]']) == 1
        # 索引应该是排序的
        assert result['[安全]'] == sorted(result['[安全]'])
        assert result['[涉政]'] == sorted(result['[涉政]'])

    def test_sample_dict_config_empty_dict(self):
        """测试空字典配置（针对所有独特标签）"""
        labels = ['[安全]', '[涉政]', '[安全]', '[涉政]', '[其他]']
        result = sample_from_array(labels, label_config={}, max_samples=2)

        assert isinstance(result, dict)
        # 应该包含所有独特标签
        assert '[安全]' in result
        assert '[涉政]' in result
        assert '[其他]' in result
        # 每个标签最多2个
        assert len(result['[安全]']) <= 2
        assert len(result['[涉政]']) <= 2
        assert len(result['[其他]']) <= 2

    def test_sample_dict_config_label_not_exist(self):
        """测试标签不存在的情况"""
        labels = ['[安全]', '[涉政]']
        result = sample_from_array(labels, label_config={'[不存在]': 2})

        # 不存在的标签不会在结果中
        assert '[不存在]' not in result

    def test_sample_dict_config_count_exceeds_available(self):
        """测试请求数量超过可用数量"""
        labels = ['[安全]', '[涉政]']
        result = sample_from_array(labels, label_config={'[安全]': 10})

        # 最多只能返回1个（因为只有1个[安全]）
        assert len(result['[安全]']) == 1

    def test_sample_invalid_config_type(self):
        """测试无效的配置类型"""
        labels = ['[安全]', '[涉政]']

        with pytest.raises(ValueError, match="label_config must be None or dict"):
            sample_from_array(labels, label_config="invalid")


@pytest.mark.unit
class TestGetRealExtension:
    """get_real_extension_from_bytes 函数的测试"""

    def test_jpg_format(self):
        """测试 JPG 格式检测"""
        jpg_data = b"\xff\xd8\xff\xe0\x00\x10JFIF"
        assert get_real_extension_from_bytes(jpg_data) == ".jpg"

    def test_png_format(self):
        """测试 PNG 格式检测"""
        png_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        assert get_real_extension_from_bytes(png_data) == ".png"

    def test_gif_format(self):
        """测试 GIF 格式检测"""
        gif_data = b"\x47\x49\x46\x38\x39\x61"
        assert get_real_extension_from_bytes(gif_data) == ".gif"

    def test_webp_format(self):
        """测试 WEBP 格式检测"""
        webp_data = b"\x52\x49\x46\x46\x00\x00\x00\x00WEBP"
        assert get_real_extension_from_bytes(webp_data) == ".webp"

    def test_heic_format(self):
        """测试 HEIC 格式检测"""
        heic_data = b"\x00\x00\x00\x20ftypheic\x00\x00\x00\x00"
        assert get_real_extension_from_bytes(heic_data) == ".heic"

    def test_avif_format(self):
        """测试 AVIF 格式检测"""
        avif_data = b"\x00\x00\x00\x20ftypavif\x00\x00\x00\x00"
        assert get_real_extension_from_bytes(avif_data) == ".avif"

    def test_bmp_format(self):
        """测试 BMP 格式检测"""
        bmp_data = b"BM\x00\x00\x00\x00\x00\x00"
        assert get_real_extension_from_bytes(bmp_data) == ".bmp"

    def test_tiff_format_little_endian(self):
        """测试 TIFF 格式检测（Little Endian）"""
        tiff_data = b"\x49\x49\x2A\x00\x00\x00\x00\x00"
        assert get_real_extension_from_bytes(tiff_data) == ".tiff"

    def test_tiff_format_big_endian(self):
        """测试 TIFF 格式检测（Big Endian）"""
        tiff_data = b"\x4D\x4D\x00\x2A\x00\x00\x00\x00"
        assert get_real_extension_from_bytes(tiff_data) == ".tiff"

    def test_unknown_format_defaults_to_jpg(self):
        """测试未知格式默认返回 JPG"""
        unknown_data = b"\x00\x00\x00\x00\x00\x00"
        assert get_real_extension_from_bytes(unknown_data) == ".jpg"

    def test_empty_data(self):
        """测试空数据"""
        assert get_real_extension_from_bytes(b"") == ".jpg"

    def test_short_data(self):
        """测试数据长度不足"""
        short_data = b"\x00\x00"
        assert get_real_extension_from_bytes(short_data) == ".jpg"
