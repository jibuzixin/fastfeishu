"""
FeiShuSheetOperations 类的单元测试

测试操作层的核心逻辑。
"""

import pytest
from unittest.mock import patch, Mock, MagicMock

from fastfeishu.core.operations import FeiShuSheetOperations
from fastfeishu.exceptions.exception import FeiShuException


@pytest.mark.unit
class TestFeiShuSheetOperations:
    """FeiShuSheetOperations 类的测试"""

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_init_readonly_mode(self, mock_get, mock_post,
                               mock_tenant_token_response,
                               mock_sheet_metadata_response,
                               feishu_url):
        """测试只读模式初始化"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        ops = FeiShuSheetOperations(feishu_url, readonly=True)

        assert ops.is_readonly() is True
        assert ops._readonly is True

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_readonly_mode_prevents_write(self, mock_get, mock_post,
                                          mock_tenant_token_response,
                                          mock_sheet_metadata_response,
                                          feishu_url):
        """测试只读模式阻止写入操作"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        ops = FeiShuSheetOperations(feishu_url, readonly=True)

        # 调用内部的写入拦截方法应该抛出异常
        with pytest.raises(FeiShuException, match="只读模式，禁止写入操作"):
            ops._deny_if_readonly()

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_get_header_caching(self, mock_get, mock_post,
                               mock_tenant_token_response,
                               mock_sheet_metadata_response,
                               mock_read_response,
                               feishu_url):
        """测试表头缓存功能"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()

        mock_read_resp = Mock()
        mock_read_resp.json.return_value = mock_read_response
        mock_read_resp.raise_for_status = Mock()

        # 第一次是 metadata，后续是 read
        mock_get.side_effect = [mock_meta_resp, mock_read_resp, mock_read_resp]

        ops = FeiShuSheetOperations(feishu_url, readonly=False)

        # 第一次获取表头
        header1 = ops.get_header()
        call_count_after_first = mock_get.call_count

        # 第二次获取表头（应该使用缓存，不增加调用次数）
        header2 = ops.get_header()
        call_count_after_second = mock_get.call_count

        assert header1 == header2
        # 第二次调用不应该增加 API 调用次数（缓存生效）
        assert call_count_after_first == call_count_after_second

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_detect_header_modification(self, mock_get, mock_post,
                                       mock_tenant_token_response,
                                       mock_sheet_metadata_response,
                                       feishu_url):
        """测试检测表头修改"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        ops = FeiShuSheetOperations(feishu_url, readonly=False)

        # 测试修改第一行会触发表头修改标记
        result = ops._detect_header_modification("A1:C1")
        assert result is True
        assert ops._alter_header is True

        # 重置标记
        ops._alter_header = False

        # 测试修改其他行不会触发
        result = ops._detect_header_modification("A2:C2")
        assert result is False

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_read_operation(self, mock_get, mock_post,
                           mock_tenant_token_response,
                           mock_sheet_metadata_response,
                           mock_read_response,
                           feishu_url):
        """测试读取操作"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_read_resp = Mock()
        mock_read_resp.json.return_value = mock_read_response
        mock_read_resp.raise_for_status = Mock()

        # 由于 feishu_url 包含 sheet_id，初始化时不会调用 get_sheet_metadata()
        # 所以只需要 mock read 响应
        mock_get.return_value = mock_read_resp

        ops = FeiShuSheetOperations(feishu_url, readonly=True)
        data = ops.read("A1:C3")

        assert len(data) == 3
        assert data[0] == ["CaseID", "查询", "意图类型"]

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_get_sheet_info(self, mock_get, mock_post,
                           mock_tenant_token_response,
                           mock_sheet_metadata_response,
                           feishu_url):
        """测试获取 sheet info"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        ops = FeiShuSheetOperations(feishu_url, readonly=True)
        info = ops.get_sheet_info()

        assert info is not None
        assert info["sheetId"] == "TestSheet456"
        assert info["columnCount"] == 26

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_properties_access(self, mock_get, mock_post,
                              mock_tenant_token_response,
                              mock_sheet_metadata_response,
                              feishu_url):
        """测试属性访问"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        ops = FeiShuSheetOperations(feishu_url, readonly=False)

        assert ops.sheet_token == "TestToken123"
        assert ops.sheet_id == "TestSheet456"
        assert ops.link == feishu_url
