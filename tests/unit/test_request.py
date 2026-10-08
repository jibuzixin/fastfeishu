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


def _make_resp(status, body=None, *, reason="Bad Request", url="https://open.feishu.cn/x"):
    """构造一个行为接近真实 requests.Response 的 Mock，用于 _raise_for_status 测试。"""
    r = Mock(spec=requests.Response)
    r.status_code = status
    r.reason = reason
    r.url = url
    r.headers = {"content-type": "application/json"} if body is not None else {"content-type": "text/html"}
    if body is None:
        r.json.side_effect = ValueError("not json")
        r.text = "<html>502 Bad Gateway</html>"
    else:
        r.json.return_value = body
        r.text = ""
    if status >= 400:
        r.raise_for_status.side_effect = requests.HTTPError(f"{status} Client Error", response=r)
    else:
        r.raise_for_status.return_value = None
    return r


@pytest.mark.unit
class TestRaiseForStatus:
    """_raise_for_status 是唯一的响应错误检查点，锁住下沉后的行为，防回归。"""

    def test_http_error_with_json_body_surfaces_code_msg(self):
        """HTTP 4xx 但响应体是 JSON 时，应带出服务端 code/msg，而非只报 400。"""
        req = FeiShuRequest.__new__(FeiShuRequest)
        with pytest.raises(FeiShuException) as exc_info:
            req._raise_for_status(_make_resp(400, {"code": 99991663, "msg": "request body format error"}))
        msg = str(exc_info.value)
        assert "HTTP 400" in msg
        assert "99991663" in msg
        assert "request body format error" in msg

    def test_http_error_with_non_json_body_falls_back_to_text(self):
        """HTTP 5xx 返回 HTML 时，回退到纯文本，不炸。"""
        req = FeiShuRequest.__new__(FeiShuRequest)
        with pytest.raises(FeiShuException, match="502 Bad Gateway"):
            req._raise_for_status(_make_resp(502, None, reason="Bad Gateway"))

    def test_business_code_nonzero_on_http200_raises(self):
        """关键回归：HTTP 200 但业务 code != 0 时，request 层现在直接抛异常。

        下沉前由 operations._response_json 抛；下沉后由 _raise_for_status 抛。
        类型仍是 FeiShuException，保证向后兼容。
        """
        req = FeiShuRequest.__new__(FeiShuRequest)
        with pytest.raises(FeiShuException) as exc_info:
            req._raise_for_status(_make_resp(200, {"code": 99991668, "msg": "range format error"}))
        msg = str(exc_info.value)
        assert "99991668" in msg
        assert "range format error" in msg

    def test_http200_code_zero_passes(self):
        """HTTP 200 + code 0 正常通过，不抛。"""
        req = FeiShuRequest.__new__(FeiShuRequest)
        # 不应抛
        req._raise_for_status(_make_resp(200, {"code": 0, "msg": "success"}))

    def test_check_body_false_skips_business_code(self):
        """二进制下载传 check_body=False 时，即便 body 有 code 字段也不校验（流不解析）。"""
        req = FeiShuRequest.__new__(FeiShuRequest)
        # 假设一个 200 响应，body 里其实是个 dict（真实场景是二进制流，json 会抛）
        # 这里验证 check_body=False 完全跳过 body 读取
        resp = _make_resp(200, {"code": 9999, "msg": "should be ignored"})
        resp.json.reset_mock(return_value=True, side_effect=True)
        # 不论 body 是什么，check_body=False 都不应抛、不应读 json
        req._raise_for_status(resp, check_body=False)
        assert not resp.json.called, "check_body=False 不应读取响应体"

    def test_check_body_false_still_raises_on_http_error(self):
        """check_body=False 只跳过业务码校验，HTTP 错误仍照常抛。"""
        req = FeiShuRequest.__new__(FeiShuRequest)
        with pytest.raises(FeiShuException, match="HTTP 404"):
            req._raise_for_status(
                _make_resp(404, {"code": 99991663, "msg": "not found"}, reason="Not Found"),
                check_body=False,
            )
