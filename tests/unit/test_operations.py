"""
FeiShuSheetOperations 类的单元测试

测试操作层的核心逻辑。
"""

import base64
import io

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


@pytest.mark.unit
class TestDownloadImageBase64Compress:
    """download_image_base64(compress=...) 压缩分支的回归测试。

    修复前：压缩循环算出的 compressed_data 被丢弃，最终返回原始 data 的 base64，
    compress 参数实际不生效。本测试锁住「压缩后数据更小且仍为有效图片」。
    """

    def _make_ops(self):
        """构造一个绕过 HTTP 初始化的 FeiShuSheetOperations，_request 为 Mock。"""
        ops = FeiShuSheetOperations.__new__(FeiShuSheetOperations)
        ops._request = Mock()
        ops._readonly = False
        return ops

    def _big_image_bytes(self):
        """用 Pillow 生成一张 >1MB 的随机噪声 JPEG（高熵内容，降质量能真正缩小）。"""
        from PIL import Image
        import os
        # 2200x2200 随机 RGB 噪声 → quality 95 的 JPEG 明显大于 1MB
        w = h = 2200
        img = Image.frombytes("RGB", (w, h), os.urandom(w * h * 3))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=95)
        return buf.getvalue()

    def test_compress_returns_smaller_valid_image(self):
        """compress 阈值触发时，返回的 base64 解码后应小于原图，且仍是有效图片。

        修复前这里会得到与原图等大的数据（compress 参数不生效）。
        """
        pytest.importorskip("PIL")  # 未装 Pillow 时跳过（可选依赖）
        from PIL import Image
        original = self._big_image_bytes()
        assert len(original) > 1 * 1024 * 1024, "测试图片应大于 1MB 才能触发压缩"

        ops = self._make_ops()
        ops._request.download_media_raw.return_value = (None, original)

        result_b64 = ops.download_image_base64("fake_token", compress=1)
        decoded = base64.b64decode(result_b64)

        # 核心断言：压缩后必须比原始数据小（修复前这里会相等）
        assert len(decoded) < len(original), (
            f"压缩后({len(decoded)})应小于原图({len(original)})，compress 参数未生效"
        )
        # 仍是有效图片（能用 Pillow 重新打开）
        Image.open(io.BytesIO(decoded)).verify()

    def test_no_compress_returns_original(self):
        """compress=None 时不压缩，返回原图 base64。"""
        pytest.importorskip("PIL")
        original = self._big_image_bytes()
        ops = self._make_ops()
        ops._request.download_media_raw.return_value = (None, original)

        result_b64 = ops.download_image_base64("fake_token", compress=None)
        decoded = base64.b64decode(result_b64)
        assert decoded == original, "compress=None 应原样返回"

    def test_compress_below_threshold_no_compression(self):
        """原图小于阈值时不应压缩，原样返回。"""
        pytest.importorskip("PIL")
        # 一张很小的 PNG
        from PIL import Image
        buf = io.BytesIO()
        Image.new("RGB", (10, 10), color=(0, 255, 0)).save(buf, format="PNG")
        small = buf.getvalue()
        assert len(small) < 1024 * 1024

        ops = self._make_ops()
        ops._request.download_media_raw.return_value = (None, small)

        result_b64 = ops.download_image_base64("fake_token", compress=1)
        assert base64.b64decode(result_b64) == small, "小于阈值应原样返回"

    def test_compress_without_pillow_raises_friendly(self):
        """未装 Pillow 时调用压缩应抛 FeiShuException 且提示安装命令。"""
        import sys
        original_mod = sys.modules.get("PIL")
        sys.modules["PIL"] = None  # 让 `from PIL import Image` 直接 ImportError

        try:
            ops = self._make_ops()
            # >1MB 的非图片数据，仅用于触发压缩分支（不会走到真正解码图片）
            big = b"\x89PNG\r\n\x1a\n" + b"x" * (2 * 1024 * 1024)
            ops._request.download_media_raw.return_value = (None, big)

            with pytest.raises(FeiShuException, match=r"fastfeishu\[image\]"):
                ops.download_image_base64("fake_token", compress=1)
        finally:
            if original_mod is not None:
                sys.modules["PIL"] = original_mod
            else:
                sys.modules.pop("PIL", None)


def _make_ops():
    """构造一个绕过 HTTP 初始化的 FeiShuSheetOperations，_request 为 Mock。"""
    ops = FeiShuSheetOperations.__new__(FeiShuSheetOperations)
    ops._request = Mock()
    ops._readonly = False
    ops._alter_header = False  # 避免表头检测副作用
    ops._header = None
    return ops


def _flatten_ranges(ranges_data):
    """把 write_batch 收到的 [{range, values}] 展平成 {(col, row): value}。"""
    from fastfeishu.helpers import match_col_letter_by_range, match_row_num_by_range, excel_col_to_num
    written = {}
    for item in ranges_data:
        start_col, end_col = match_col_letter_by_range(item["range"])
        start_row, end_row = match_row_num_by_range(item["range"])
        sc, ec = excel_col_to_num(start_col), excel_col_to_num(end_col)
        sr, er = int(start_row), int(end_row)
        values = item["values"]
        for r in range(er - sr + 1):
            row_vals = values[r] if r < len(values) else []
            for c in range(ec - sc + 1):
                v = row_vals[c] if c < len(row_vals) else None
                written[(num_to_excel_col(sc + c), sr + r)] = v
    return written


from fastfeishu.helpers import num_to_excel_col  # 供 _flatten_ranges 使用


@pytest.mark.unit
class TestSkipNone:
    """skip_none 语义回归：不写 None 单元格、保留原位置、不紧凑。"""

    def test_write_default_no_skip_none_calls_write(self):
        """skip_none=False（默认）走单范围 write，写全部数据含 None。"""
        ops = _make_ops()
        data = [[1, None, 3], [None, 5, None]]
        ops.write("A2:C3", data)  # 默认 skip_none=False
        assert ops._request.write.called
        assert not ops._request.write_batch.called
        # 原数据原样传给 write
        sent_range, sent_data = ops._request.write.call_args[0]
        assert sent_range == "A2:C3"
        assert sent_data == data

    def test_write_skip_none_excludes_none_preserves_position(self):
        """skip_none=True：None 格子不写，非 None 值落在原列位置（不紧凑）。"""
        ops = _make_ops()
        # (0,0)=1 -> A2; (0,2)=3 -> C2; (1,1)=5 -> B3。None 位置 B2/A3/C3 不写
        data = [[1, None, 3], [None, 5, None]]
        ops.write("A2:C3", data, skip_none=True)
        assert not ops._request.write.called
        assert ops._request.write_batch.called
        written = _flatten_ranges(ops._request.write_batch.call_args[0][0])
        assert written == {("A", 2): 1, ("C", 2): 3, ("B", 3): 5}, (
            f"None 应被跳过、位置不变，实际写入: {written}"
        )

    def test_write_skip_none_no_compaction(self):
        """核心语义（用户强调）：[[1, None, 3]] -> 1 在 A1，3 在 C1，不是 A1/B1。"""
        ops = _make_ops()
        ops.write("A1:C1", [[1, None, 3]], skip_none=True)
        written = _flatten_ranges(ops._request.write_batch.call_args[0][0])
        assert written == {("A", 1): 1, ("C", 1): 3}, (
            f"None 位置不紧凑：3 应在 C1 而非 B1，实际: {written}"
        )

    def test_write_batch_default_no_skip_none(self):
        """write_batch skip_none=False 原样透传。"""
        ops = _make_ops()
        value_ranges = [{"range": "A2:B3", "values": [[1, None], [None, 4]]}]
        ops.write_batch(value_ranges)
        assert ops._request.write_batch.call_args[0][0] is value_ranges

    def test_write_batch_skip_none_expands_and_excludes_none(self):
        """write_batch skip_none=True：每个范围分区展开，None 不写、位置不变。"""
        ops = _make_ops()
        value_ranges = [{"range": "A2:C2", "values": [[1, None, 3]]}]
        ops.write_batch(value_ranges, skip_none=True)
        # 走 _request.write_batch（write_batch 内部最终调用），且只含非 None
        written = _flatten_ranges(ops._request.write_batch.call_args[0][0])
        assert written == {("A", 2): 1, ("C", 2): 3}, f"实际: {written}"
        # 确保没有 None 被写进去
        assert None not in written.values()

    def test_write_skip_none_all_none_no_write(self):
        """全 None 数据 skip_none=True 时不触发任何写入。"""
        ops = _make_ops()
        ops.write("A2:B3", [[None, None], [None, None]], skip_none=True)
        assert not ops._request.write.called
        # write_batch 可能被调但 ranges_data 为空 -> partition_grid 返回空时不调用
        assert not ops._request.write_batch.called

    def test_write_grid_skip_none_helper_preserves_position(self):
        """直接测 helper：N×1 列数据，None 行不写、不紧凑。"""
        ops = _make_ops()
        # 列数据：第 0 行=1，第 1 行=None，第 2 行=3；起始 B5
        grid = [[1], [None], [3]]
        ops._write_grid_skip_none(grid, start_row=5, start_col_num=2, partition_strategy='auto')
        written = _flatten_ranges(ops._request.write_batch.call_args[0][0])
        # 1 -> B5，3 -> B7；B6 不写
        assert written == {("B", 5): 1, ("B", 7): 3}, (
            f"列方向也保持行对齐不紧凑，实际: {written}"
        )
