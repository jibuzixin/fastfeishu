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


@pytest.mark.unit
class TestDoRequestTokenRetry:
    """_do_request 的 token 失效自动刷新重试 + 手动刷新 + 并发去重回归测试。"""

    def _make_request(self, tat="old_tat"):
        """构造一个绕过 HTTP 初始化的 FeiShuRequest，初始化锁与代际计数器。

        把 get_tenant_token 打 spy：_ensure_fresh_token 内部会调它刷新。
        """
        import threading
        req = FeiShuRequest.__new__(FeiShuRequest)
        req._tat_lock = threading.Lock()
        req._tat_epoch = 0
        req.tat = tat
        req.sheet_token = "T"
        req.sheet_id = "S"
        # 默认 spy：刷新时把 tat 换成新值
        req.get_tenant_token = Mock()
        return req

    def _spy_refresh(self, req, new_tat="new_tat"):
        """让 get_tenant_token 返回新 token（_ensure_fresh_token 会用它的返回值赋给 tat）。"""
        req.get_tenant_token.return_value = new_tat

    def test_business_token_expired_triggers_refresh_and_retry(self):
        """HTTP 200 + code 99991663 -> 刷新 token -> 用新 token 重试 -> 成功。"""
        req = self._make_request()
        self._spy_refresh(req, "new_tat")
        err_resp = _make_resp(200, {"code": 99991663, "msg": "token expired"}, reason="OK")
        ok_resp = _make_resp(200, {"code": 0, "msg": "ok", "data": {}}, reason="OK")

        with patch("fastfeishu.core.request.requests.get", side_effect=[err_resp, ok_resp]) as mock_get:
            resp = req._do_request("GET", "https://x")

        assert resp is ok_resp
        assert mock_get.call_count == 2  # 原始 + 1 次重试
        req.get_tenant_token.assert_called_once()
        # 重试请求的 Authorization 头用了刷新后的 token
        retry_headers = mock_get.call_args_list[1].kwargs["headers"]
        assert retry_headers["Authorization"] == "Bearer new_tat"

    def test_http_error_with_token_code_triggers_retry(self):
        """HTTP 401 + body code 99991663 同样触发刷新重试。"""
        req = self._make_request()
        self._spy_refresh(req, "new_tat")
        err_resp = _make_resp(401, {"code": 99991663, "msg": "invalid token"}, reason="Unauthorized")
        ok_resp = _make_resp(200, {"code": 0, "msg": "ok"}, reason="OK")

        with patch("fastfeishu.core.request.requests.get", side_effect=[err_resp, ok_resp]) as mock_get:
            resp = req._do_request("GET", "https://x")

        assert resp is ok_resp
        assert mock_get.call_count == 2
        req.get_tenant_token.assert_called_once()

    def test_non_token_error_no_refresh_no_retry(self):
        """普通业务错误码（非 token 失效）不刷新、不重试，直接抛。"""
        req = self._make_request()
        err_resp = _make_resp(200, {"code": 1254000, "msg": "some business error"}, reason="OK")

        with patch("fastfeishu.core.request.requests.get", return_value=err_resp) as mock_get:
            with pytest.raises(FeiShuException) as exc_info:
                req._do_request("GET", "https://x")

        assert exc_info.value.code == 1254000
        assert mock_get.call_count == 1
        req.get_tenant_token.assert_not_called()

    def test_retry_only_once_then_raise(self):
        """重试后仍失效只重试一次，第二次失败直接抛，不无限递归。"""
        req = self._make_request()
        self._spy_refresh(req, "new_tat")
        err_resp = _make_resp(200, {"code": 99991663, "msg": "still expired"}, reason="OK")

        with patch("fastfeishu.core.request.requests.get", return_value=err_resp) as mock_get:
            with pytest.raises(FeiShuException) as exc_info:
                req._do_request("GET", "https://x")

        assert exc_info.value.code == 99991663
        assert mock_get.call_count == 2  # 原始 + 1 次重试，不再多
        req.get_tenant_token.assert_called_once()

    @pytest.mark.parametrize("code", [99991663, 99991665, 4001, 20013, 20005])
    def test_each_token_expired_code_triggers_retry(self, code):
        """所有 tenant token 失效码都触发刷新重试。"""
        req = self._make_request()
        self._spy_refresh(req, "new_tat")
        err_resp = _make_resp(200, {"code": code, "msg": "x"}, reason="OK")
        ok_resp = _make_resp(200, {"code": 0, "msg": "ok"}, reason="OK")

        with patch("fastfeishu.core.request.requests.get", side_effect=[err_resp, ok_resp]) as mock_get:
            req._do_request("GET", "https://x")

        assert mock_get.call_count == 2
        req.get_tenant_token.assert_called_once()

    def test_refresh_tenant_token_updates_tat(self):
        """手动刷新方法把新 token 写入 self.tat，并推进代际。"""
        req = FeiShuRequest.__new__(FeiShuRequest)
        import threading
        req._tat_lock = threading.Lock()
        req._tat_epoch = 0
        req.tat = None
        with patch.object(FeiShuRequest, "get_tenant_token", return_value="fresh_tat"):
            req.refresh_tenant_token()
        assert req.tat == "fresh_tat"
        assert req._tat_epoch == 1

    def test_binary_download_retries_on_token_expired(self):
        """二进制下载（check_body=False）命中 token 失效码也刷新重试，且不读 body。"""
        req = self._make_request()
        self._spy_refresh(req, "new_tat")
        # HTTP 200 + body 含 token 失效码，但 check_body=False 时 _raise_for_status 只做 HTTP 校验
        # 所以 token 失效必须以 HTTP 错误形式出现（如 401 + JSON body）
        err_resp = _make_resp(401, {"code": 99991663, "msg": "expired"}, reason="Unauthorized")
        ok_resp = _make_resp(200, None, reason="OK")  # 二进制成功，json 抛 ValueError
        ok_resp.iter_content.return_value = iter([b"\x89PNG"])

        with patch("fastfeishu.core.request.requests.get", side_effect=[err_resp, ok_resp]) as mock_get:
            resp = req._do_request(
                "GET", "https://x",
                headers={"Authorization": "Bearer old_tat"},
                stream=True,
                check_body=False,
            )
        assert resp is ok_resp
        assert mock_get.call_count == 2
        # 重试的 headers 保留了调用方的自定义结构，仅 Authorization 被刷新
        retry_headers = mock_get.call_args_list[1].kwargs["headers"]
        assert retry_headers["Authorization"] == "Bearer new_tat"

    def test_ensure_fresh_token_dedups_concurrent_expiry(self):
        """并发去重：同一代际的多次失效刷新只发生一次，后续复用新 token。

        直接测 _ensure_fresh_token：两个"同时发出"的请求都用 used_epoch=0，
        第一个刷新（epoch 0->1），第二个进锁时 epoch 已=1 跳过刷新。
        """
        req = self._make_request(tat="T0")
        req.get_tenant_token.return_value = "T1"

        # 第一次：epoch(0) == used_epoch(0) -> 刷新
        req._ensure_fresh_token(0)
        assert req.tat == "T1"
        assert req._tat_epoch == 1
        assert req.get_tenant_token.call_count == 1

        # 第二个并发请求：used_epoch 仍是 0，但 epoch 已=1 -> 跳过刷新复用 T1
        req.get_tenant_token.reset_mock()
        req._ensure_fresh_token(0)
        assert req.get_tenant_token.call_count == 0, "代际已变，应跳过刷新"
        assert req.tat == "T1"  # 复用第一次刷新的结果

    def test_concurrent_real_threads_refresh_once(self):
        """真多线程：N 个线程同时命中 token 失效，get_tenant_token 只被调用一次。"""
        import threading
        req = self._make_request(tat="T0")

        refresh_count = {"n": 0}
        counter_lock = threading.Lock()

        # 真实的 get_tenant_token：换新 token 并计数
        def fake_get_token():
            with counter_lock:
                refresh_count["n"] += 1
            req.tat = f"T_new_{refresh_count['n']}"
            return req.tat
        req.get_tenant_token = Mock(side_effect=fake_get_token)

        barrier = threading.Barrier(5)
        # 所有带 T0 的请求都失效，带 T_new 的成功
        def fake_get(url, headers=None, **kw):
            barrier.wait(timeout=5)
            auth = headers["Authorization"]
            r = Mock()
            r.url = url; r.text = ""; r.headers = {"content-type": "application/json"}
            if "T0" in auth:
                r.status_code = 200
                r.json.return_value = {"code": 99991663, "msg": "expired"}
                r.raise_for_status.return_value = None
            else:
                r.status_code = 200
                r.json.return_value = {"code": 0, "msg": "ok"}
                r.raise_for_status.return_value = None
            return r

        errors = []
        with patch("fastfeishu.core.request.requests.get", side_effect=fake_get):
            def worker():
                try:
                    req._do_request("GET", "https://x")
                except Exception as e:
                    errors.append(e)
            threads = [threading.Thread(target=worker) for _ in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

        assert errors == [], f"不应有异常: {errors}"
        assert refresh_count["n"] == 1, (
            f"5 线程并发失效应只刷新 1 次，实际 {refresh_count['n']}"
        )
