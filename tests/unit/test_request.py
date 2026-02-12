"""
FeiShuRequest 类的单元测试

测试 API 请求层的功能，所有外部 HTTP 请求都会被 mock。
"""

import pytest
import os
from unittest.mock import patch, Mock, MagicMock
import requests

from fastfeishu.core.request import FeiShuRequest
from fastfeishu.exceptions.exception import FeiShuException


@pytest.mark.unit
class TestFeiShuRequest:
    """FeiShuRequest 类的测试"""

    def test_parse_feishu_url_with_sheet_id(self):
        """测试解析包含 sheet_id 的飞书URL"""
        url = "https://li.feishu.cn/sheets/TestToken123?sheet=TestSheet456"
        token, sheet_id = FeiShuRequest.parse_feishu_url(url)

        assert token == "TestToken123"
        assert sheet_id == "TestSheet456"

    def test_parse_feishu_url_without_sheet_id(self):
        """测试解析不包含 sheet_id 的飞书URL"""
        url = "https://li.feishu.cn/sheets/TestToken123"
        token, sheet_id = FeiShuRequest.parse_feishu_url(url)

        assert token == "TestToken123"
        assert sheet_id is None

    def test_parse_feishu_url_invalid(self):
        """测试解析无效的飞书URL"""
        url = "https://invalid-url.com"
        token, sheet_id = FeiShuRequest.parse_feishu_url(url)

        assert token is None
        assert sheet_id is None

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_init_success(self, mock_get, mock_post, mock_tenant_token_response,
                         mock_sheet_metadata_response, feishu_url):
        """测试成功初始化 FeiShuRequest"""
        # Mock tenant token 请求
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # Mock metadata 请求
        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        # 创建实例
        request = FeiShuRequest(feishu_url)

        assert request.tat == "mock_tenant_token_12345"
        assert request.sheet_token == "TestToken123"
        assert request.sheet_id == "TestSheet456"
        assert request.link == feishu_url

    @patch.dict(os.environ, {}, clear=True)
    def test_get_tenant_token_missing_credentials(self):
        """测试缺少环境变量时获取 tenant token 失败"""
        with pytest.raises(ValueError, match="请设置飞书必要的环境变量"):
            # 尝试直接调用，需要先临时创建对象
            with patch('fastfeishu.core.request.requests.post'):
                with patch('fastfeishu.core.request.requests.get'):
                    FeiShuRequest.get_tenant_token(Mock())

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_get_request_headers(self, mock_get, mock_post,
                                 mock_tenant_token_response,
                                 mock_sheet_metadata_response,
                                 feishu_url):
        """测试获取请求头"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        request = FeiShuRequest(feishu_url)
        headers = request._get_request_headers()

        assert headers["content-type"] == "application/json; charset=utf-8"
        assert headers["Authorization"] == "Bearer mock_tenant_token_12345"

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_get_sheet_metadata(self, mock_get, mock_post,
                               mock_tenant_token_response,
                               mock_sheet_metadata_response,
                               feishu_url):
        """测试获取 sheet metadata"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        request = FeiShuRequest(feishu_url)
        metadata = request.get_sheet_metadata()

        assert metadata["code"] == 0
        assert metadata["data"]["spreadsheetToken"] == "TestToken123"
        assert len(metadata["data"]["sheets"]) == 1

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_read_request(self, mock_get, mock_post,
                         mock_tenant_token_response,
                         mock_sheet_metadata_response,
                         mock_read_response,
                         feishu_url):
        """测试读取数据请求"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # 因为 feishu_url 中包含 sheet_id，初始化时不会调用 get_sheet_metadata
        # 所以只需要 mock read 请求
        mock_read_resp = Mock()
        mock_read_resp.json.return_value = mock_read_response
        mock_read_resp.raise_for_status = Mock()

        mock_get.return_value = mock_read_resp

        request = FeiShuRequest(feishu_url)
        response = request.read("A1:C3")

        # 只调用一次 json() 并存储结果
        response_data = response.json()
        assert response_data["code"] == 0
        assert len(response_data["data"]["valueRange"]["values"]) == 3

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    @patch('fastfeishu.core.request.requests.put')
    def test_write_request(self, mock_put, mock_get, mock_post,
                          mock_tenant_token_response,
                          mock_sheet_metadata_response,
                          mock_write_response,
                          feishu_url):
        """测试写入数据请求"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        mock_write_resp = Mock()
        mock_write_resp.json.return_value = mock_write_response
        mock_write_resp.raise_for_status = Mock()
        mock_put.return_value = mock_write_resp

        request = FeiShuRequest(feishu_url)
        response = request.write("A2:C3", [[1, 2, 3], [4, 5, 6]])

        # 只调用一次 json() 并存储结果
        response_data = response.json()
        assert response_data["code"] == 0
        assert response_data["data"]["updatedCells"] == 6

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_readonly_properties(self, mock_get, mock_post,
                                mock_tenant_token_response,
                                mock_sheet_metadata_response,
                                feishu_url):
        """测试只读属性（应该不能修改）"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        request = FeiShuRequest(feishu_url)

        # 尝试修改只读属性应该失败
        with pytest.raises(AttributeError):
            request.link = "https://new-url.com"

        with pytest.raises(AttributeError):
            request.sheet_token = "NewToken"

        with pytest.raises(AttributeError):
            request.sheet_id = "NewSheetId"
