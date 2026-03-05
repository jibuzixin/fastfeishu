"""
set_style 和 set_styles 方法的单元测试

测试单元格样式设置功能，包括边界检查、只读模式保护等。
"""

import pytest
from unittest.mock import patch, Mock, MagicMock
from typing import Dict, Any, List

from fastfeishu.core.operations import FeiShuSheetOperations
from fastfeishu.models import CellStyle, Font, StyleRangeData
from fastfeishu.exceptions.exception import FeiShuException, FeiShuStyleException


@pytest.mark.unit
class TestSetStyle:
    """set_style 方法测试"""

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    @patch('fastfeishu.core.request.requests.put')
    def test_set_style_with_cellstyle_object(
        self, mock_put, mock_get, mock_post,
        mock_tenant_token_response,
        mock_sheet_metadata_response,
        feishu_url
    ):
        """测试使用 CellStyle 对象设置样式"""
        # Mock token
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # Mock metadata
        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        # Mock style response
        mock_style_resp = Mock()
        mock_style_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {}
        }
        mock_style_resp.raise_for_status = Mock()
        mock_put.return_value = mock_style_resp

        ops = FeiShuSheetOperations(feishu_url, readonly=False)

        # 创建 CellStyle 对象
        style = CellStyle.builder() \
            .font(Font.builder().bold().font_size("12pt/1.5").build()) \
            .fore_color("#000000") \
            .back_color("#ffff00") \
            .h_align(1) \
            .build()

        # 设置样式
        ops.set_style("A1:C3", style)

        # 验证 put 被调用
        assert mock_put.called
        # 验证调用参数包含正确的数据
        call_args = mock_put.call_args
        assert call_args is not None

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    @patch('fastfeishu.core.request.requests.put')
    def test_set_style_with_dict(
        self, mock_put, mock_get, mock_post,
        mock_tenant_token_response,
        mock_sheet_metadata_response,
        feishu_url
    ):
        """测试使用字典设置样式"""
        # Mock token
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # Mock metadata
        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        # Mock style response
        mock_style_resp = Mock()
        mock_style_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {}
        }
        mock_style_resp.raise_for_status = Mock()
        mock_put.return_value = mock_style_resp

        ops = FeiShuSheetOperations(feishu_url, readonly=False)

        # 使用字典设置样式
        style_dict = {
            "font": {"bold": True, "fontSize": "14pt/1.5"},
            "hAlign": 1,
            "foreColor": "#000000",
            "backColor": "#ffffff"
        }

        ops.set_style("A1:C3", style_dict)

        # 验证 put 被调用
        assert mock_put.called

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_set_style_readonly_mode(
        self, mock_get, mock_post,
        mock_tenant_token_response,
        mock_sheet_metadata_response,
        feishu_url
    ):
        """测试只读模式拒绝设置样式"""
        # Mock token
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # Mock metadata
        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        ops = FeiShuSheetOperations(feishu_url, readonly=True)

        style = CellStyle.builder().fore_color("#000000").build()

        # 只读模式应该抛出异常
        with pytest.raises(FeiShuException, match="只读模式，禁止写入操作"):
            ops.set_style("A1:C3", style)


@pytest.mark.unit
class TestSetStyles:
    """set_styles 方法测试"""

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    @patch('fastfeishu.core.request.requests.put')
    def test_set_styles_basic(
        self, mock_put, mock_get, mock_post,
        mock_tenant_token_response,
        mock_sheet_metadata_response,
        feishu_url
    ):
        """测试批量设置样式基本功能"""
        # Mock token
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # Mock metadata
        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        # Mock style response
        mock_style_resp = Mock()
        mock_style_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {}
        }
        mock_style_resp.raise_for_status = Mock()
        mock_put.return_value = mock_style_resp

        ops = FeiShuSheetOperations(feishu_url, readonly=False)

        # 创建样式
        style1 = CellStyle.builder() \
            .fore_color("#000000") \
            .back_color("#ffff00") \
            .build()

        style2 = {
            "font": {"bold": True},
            "foreColor": "#ff0000"
        }

        # 批量设置样式
        data: List[StyleRangeData] = [
            {
                "ranges": ["A1:C3", "E5:G7"],
                "style": style1
            },
            {
                "ranges": ["B2:D4"],
                "style": style2
            }
        ]

        ops.set_styles(data)

        # 验证 put 被调用
        assert mock_put.called

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_set_styles_exceed_row_limit(
        self, mock_get, mock_post,
        mock_tenant_token_response,
        mock_sheet_metadata_response,
        feishu_url
    ):
        """测试超过行数限制（5000行）"""
        # Mock token
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # Mock metadata
        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        ops = FeiShuSheetOperations(feishu_url, readonly=False)

        style = {"foreColor": "#000000"}

        # 创建超过5000行的范围（A1:C5001，共5001行）
        data: List[StyleRangeData] = [
            {
                "ranges": ["A1:C5001"],
                "style": style
            }
        ]

        # 应该抛出行数超限异常
        with pytest.raises(FeiShuStyleException, match="行数.*超过限制.*5000 行"):
            ops.set_styles(data)

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_set_styles_exceed_column_limit(
        self, mock_get, mock_post,
        mock_tenant_token_response,
        mock_sheet_metadata_response,
        feishu_url
    ):
        """测试超过列数限制（100列）"""
        # Mock token
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # Mock metadata
        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        ops = FeiShuSheetOperations(feishu_url, readonly=False)

        style = {"foreColor": "#000000"}

        # 创建超过100列的范围（A1:CX10，A是第1列，CX是第102列，共102列）
        data: List[StyleRangeData] = [
            {
                "ranges": ["A1:CX10"],
                "style": style
            }
        ]

        # 应该抛出列数超限异常
        with pytest.raises(FeiShuStyleException, match="列数.*超过限制.*100 列"):
            ops.set_styles(data)

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_set_styles_border_cell_limit(
        self, mock_get, mock_post,
        mock_tenant_token_response,
        mock_sheet_metadata_response,
        feishu_url
    ):
        """测试边框样式总单元格数限制（30,000个）"""
        # Mock token
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # Mock metadata
        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        ops = FeiShuSheetOperations(feishu_url, readonly=False)

        # 创建带边框样式的配置，总单元格数超过30,000
        # A1:CV100 = 100行 × 100列 = 10,000个单元格
        # A1:CV301 = 301行 × 100列 = 30,100个单元格（超过限制）
        style_with_border = {
            "foreColor": "#000000",
            "borderType": "FULL_BORDER",
            "borderColor": "#ff0000"
        }

        data: List[StyleRangeData] = [
            {
                "ranges": ["A1:CV301"],
                "style": style_with_border
            }
        ]

        # 应该抛出边框单元格数超限异常
        with pytest.raises(FeiShuStyleException, match="总单元格数.*超过限制.*30,000"):
            ops.set_styles(data)

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    @patch('fastfeishu.core.request.requests.put')
    def test_set_styles_border_within_limit(
        self, mock_put, mock_get, mock_post,
        mock_tenant_token_response,
        mock_sheet_metadata_response,
        feishu_url
    ):
        """测试边框样式在限制内（正常通过）"""
        # Mock token
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # Mock metadata
        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        # Mock style response
        mock_style_resp = Mock()
        mock_style_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {}
        }
        mock_style_resp.raise_for_status = Mock()
        mock_put.return_value = mock_style_resp

        ops = FeiShuSheetOperations(feishu_url, readonly=False)

        # 创建带边框样式的配置，总单元格数在限制内
        # A1:CV100 = 100行 × 100列 = 10,000个单元格（未超限）
        style_with_border = {
            "foreColor": "#000000",
            "borderType": "FULL_BORDER",
            "borderColor": "#ff0000"
        }

        data: List[StyleRangeData] = [
            {
                "ranges": ["A1:CV100"],
                "style": style_with_border
            }
        ]

        # 应该正常执行
        ops.set_styles(data)

        # 验证 put 被调用
        assert mock_put.called

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_set_styles_readonly_mode(
        self, mock_get, mock_post,
        mock_tenant_token_response,
        mock_sheet_metadata_response,
        feishu_url
    ):
        """测试只读模式拒绝批量设置样式"""
        # Mock token
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # Mock metadata
        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        ops = FeiShuSheetOperations(feishu_url, readonly=True)

        style = {"foreColor": "#000000"}

        data: List[StyleRangeData] = [
            {
                "ranges": ["A1:C3"],
                "style": style
            }
        ]

        # 只读模式应该抛出异常
        with pytest.raises(FeiShuException, match="只读模式，禁止写入操作"):
            ops.set_styles(data)

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    @patch('fastfeishu.core.request.requests.put')
    def test_set_styles_mixed_cellstyle_and_dict(
        self, mock_put, mock_get, mock_post,
        mock_tenant_token_response,
        mock_sheet_metadata_response,
        feishu_url
    ):
        """测试混合使用 CellStyle 对象和字典"""
        # Mock token
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # Mock metadata
        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        # Mock style response
        mock_style_resp = Mock()
        mock_style_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {}
        }
        mock_style_resp.raise_for_status = Mock()
        mock_put.return_value = mock_style_resp

        ops = FeiShuSheetOperations(feishu_url, readonly=False)

        # CellStyle 对象
        style_obj = CellStyle.builder() \
            .font(Font.builder().bold().build()) \
            .fore_color("#000000") \
            .build()

        # 字典样式
        style_dict = {
            "foreColor": "#ff0000",
            "backColor": "#ffff00"
        }

        # 混合使用
        data: List[StyleRangeData] = [
            {
                "ranges": ["A1:B2"],
                "style": style_obj
            },
            {
                "ranges": ["C3:D4"],
                "style": style_dict
            }
        ]

        ops.set_styles(data)

        # 验证 put 被调用
        assert mock_put.called

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    @patch('fastfeishu.core.request.requests.put')
    def test_set_styles_multiple_ranges_per_style(
        self, mock_put, mock_get, mock_post,
        mock_tenant_token_response,
        mock_sheet_metadata_response,
        feishu_url
    ):
        """测试单个样式应用到多个范围"""
        # Mock token
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # Mock metadata
        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        # Mock style response
        mock_style_resp = Mock()
        mock_style_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {}
        }
        mock_style_resp.raise_for_status = Mock()
        mock_put.return_value = mock_style_resp

        ops = FeiShuSheetOperations(feishu_url, readonly=False)

        style = CellStyle.builder() \
            .fore_color("#000000") \
            .back_color("#ffff00") \
            .build()

        # 单个样式应用到多个范围
        data: List[StyleRangeData] = [
            {
                "ranges": ["A1:B2", "C3:D4", "E5:F6"],
                "style": style
            }
        ]

        ops.set_styles(data)

        # 验证 put 被调用
        assert mock_put.called

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    @patch('fastfeishu.core.request.requests.put')
    def test_set_styles_no_border_no_cell_limit(
        self, mock_put, mock_get, mock_post,
        mock_tenant_token_response,
        mock_sheet_metadata_response,
        feishu_url
    ):
        """测试无边框样式时不受30,000单元格限制"""
        # Mock token
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # Mock metadata
        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        # Mock style response
        mock_style_resp = Mock()
        mock_style_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {}
        }
        mock_style_resp.raise_for_status = Mock()
        mock_put.return_value = mock_style_resp

        ops = FeiShuSheetOperations(feishu_url, readonly=False)

        # 无边框样式，即使单元格数超过30,000也应该通过
        # A1:CV301 = 301行 × 100列 = 30,100个单元格
        style_no_border = {
            "foreColor": "#000000",
            "backColor": "#ffffff"
        }

        data: List[StyleRangeData] = [
            {
                "ranges": ["A1:CV301"],
                "style": style_no_border
            }
        ]

        # 应该正常执行（无边框样式不受30,000限制）
        ops.set_styles(data)

        # 验证 put 被调用
        assert mock_put.called

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    @patch('fastfeishu.core.request.requests.put')
    def test_set_styles_using_stylerangedata_constructor(
        self, mock_put, mock_get, mock_post,
        mock_tenant_token_response,
        mock_sheet_metadata_response,
        feishu_url
    ):
        """测试使用 StyleRangeData 构造函数创建数据（验证类型兼容性）"""
        # Mock token
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # Mock metadata
        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        # Mock style response
        mock_style_resp = Mock()
        mock_style_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {}
        }
        mock_style_resp.raise_for_status = Mock()
        mock_put.return_value = mock_style_resp

        ops = FeiShuSheetOperations(feishu_url, readonly=False)

        # 创建样式
        style = CellStyle.builder() \
            .fore_color("#000000") \
            .back_color("#ffff00") \
            .h_align(1) \
            .build()

        # 使用 StyleRangeData() 构造函数（而非字典）
        data: List[StyleRangeData] = [
            StyleRangeData(
                ranges=["A1:C3"],
                style=style
            ),
            StyleRangeData(
                ranges=["E5:G7"],
                style={"foreColor": "#ff0000"}
            )
        ]

        # 应该正常执行
        ops.set_styles(data)

        # 验证 put 被调用
        assert mock_put.called
