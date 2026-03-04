"""
FeiShuSheet 类的高级功能单元测试

测试更多的写入、读取和操作方法。
"""

import pytest
from unittest.mock import patch, Mock, MagicMock

from fastfeishu.core.sheet import FeiShuSheet
from fastfeishu.exceptions.exception import FeiShuColumnNotExist


@pytest.mark.unit
class TestFeiShuSheetAdvanced:
    """FeiShuSheet 高级功能测试"""

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_delete_series_by_index_columns(self, mock_get, mock_post,
                                           mock_tenant_token_response,
                                           mock_sheet_metadata_response,
                                           feishu_url):
        """测试按字母索引删除列"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        sheet = FeiShuSheet(feishu_url, readonly=False)

        with patch.object(sheet, 'delete_series', return_value=3) as mock_delete:
            result = sheet.delete_series_by_index('A', 'C')

            # 应该调用 delete_series，从列1到列3
            mock_delete.assert_called_once_with(1, 3, "COLUMNS")
            assert result == 3

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_delete_series_by_index_rows(self, mock_get, mock_post,
                                        mock_tenant_token_response,
                                        mock_sheet_metadata_response,
                                        feishu_url):
        """测试按数字索引删除行"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        sheet = FeiShuSheet(feishu_url, readonly=False)

        with patch.object(sheet, 'delete_series', return_value=5) as mock_delete:
            result = sheet.delete_series_by_index(2, 6)

            # 应该调用 delete_series，从行2到行6
            mock_delete.assert_called_once_with(2, 6, "ROWS")
            assert result == 5

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_delete_series_by_index_single(self, mock_get, mock_post,
                                          mock_tenant_token_response,
                                          mock_sheet_metadata_response,
                                          feishu_url):
        """测试删除单行/列"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        sheet = FeiShuSheet(feishu_url, readonly=False)

        with patch.object(sheet, 'delete_series', return_value=1) as mock_delete:
            result = sheet.delete_series_by_index('B')

            # end_index 应该等于 start_index
            mock_delete.assert_called_once_with(2, 2, "COLUMNS")
            assert result == 1

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_delete_series_by_index_type_mismatch(self, mock_get, mock_post,
                                                  mock_tenant_token_response,
                                                  mock_sheet_metadata_response,
                                                  feishu_url):
        """测试索引类型不匹配"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        sheet = FeiShuSheet(feishu_url, readonly=False)

        # 一个是字符串，一个是数字
        with pytest.raises(ValueError, match="不是一个相同的类型"):
            sheet.delete_series_by_index('A', 3)

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_read_human(self, mock_get, mock_post,
                       mock_tenant_token_response,
                       mock_sheet_metadata_response,
                       feishu_url):
        """测试人类可读方式读取"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        sheet = FeiShuSheet(feishu_url, readonly=True)

        # 使用 patch 直接模拟 read 方法的返回值
        with patch.object(sheet, 'read', return_value=[
            [{"text": "链接文本"}, ["嵌套", {"text": "数据"}]],
            ["普通文本", 123]
        ]):
            result = sheet.read_human("A1:B2")

            # 应该将复杂类型转换为字符串
            assert result[0][0] == "链接文本"
            assert result[1][0] == "普通文本"

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_read_raw(self, mock_get, mock_post,
                     mock_tenant_token_response,
                     mock_sheet_metadata_response,
                     feishu_url):
        """测试原始方式读取（包含公式）"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()

        mock_read_resp = Mock()
        mock_read_resp.json.return_value = {
            "code": 0,
            "data": {
                "valueRange": {
                    "values": [
                        ["=SUM(A1:A10)", "数据"]
                    ]
                }
            }
        }
        mock_read_resp.raise_for_status = Mock()

        mock_get.side_effect = [mock_meta_resp, mock_read_resp]

        sheet = FeiShuSheet(feishu_url, readonly=True)

        with patch.object(sheet, 'read', return_value=[["=SUM(A1:A10)", "数据"]]):
            result = sheet.read_raw("A1:B1")
            assert result[0][0] == "=SUM(A1:A10)"

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_get_title(self, mock_get, mock_post,
                      mock_tenant_token_response,
                      mock_sheet_metadata_response,
                      feishu_url):
        """测试获取表格标题"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # 修改元数据响应，添加 title
        metadata_with_title = mock_sheet_metadata_response.copy()
        metadata_with_title['data']['sheets'][0]['title'] = "测试表格"

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = metadata_with_title
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        sheet = FeiShuSheet(feishu_url, readonly=True)

        with patch.object(sheet, 'get_sheet_info', return_value={"title": "测试表格"}):
            title = sheet.get_title()
            assert title == "测试表格"

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_get_title_no_title(self, mock_get, mock_post,
                                mock_tenant_token_response,
                                mock_sheet_metadata_response,
                                feishu_url):
        """测试获取标题但无标题字段"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        sheet = FeiShuSheet(feishu_url, readonly=True)

        with patch.object(sheet, 'get_sheet_info', return_value={}):
            title = sheet.get_title()
            assert title == ''

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_cell_value_type_judge_dict(self, mock_get, mock_post,
                                       mock_tenant_token_response,
                                       mock_sheet_metadata_response,
                                       feishu_url):
        """测试单元格值类型判断 - 字典"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        sheet = FeiShuSheet(feishu_url, readonly=True)

        result = sheet._cell_value_type_judge({"text": "测试文本"})
        assert result == "测试文本"

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_cell_value_type_judge_list(self, mock_get, mock_post,
                                       mock_tenant_token_response,
                                       mock_sheet_metadata_response,
                                       feishu_url):
        """测试单元格值类型判断 - 列表"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        sheet = FeiShuSheet(feishu_url, readonly=True)

        result = sheet._cell_value_type_judge([{"text": "部分1"}, {"text": "部分2"}])
        assert result == "部分1部分2"

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_cell_value_type_judge_simple(self, mock_get, mock_post,
                                         mock_tenant_token_response,
                                         mock_sheet_metadata_response,
                                         feishu_url):
        """测试单元格值类型判断 - 简单类型"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        sheet = FeiShuSheet(feishu_url, readonly=True)

        assert sheet._cell_value_type_judge("文本") == "文本"
        assert sheet._cell_value_type_judge(123) == 123
        assert sheet._cell_value_type_judge(True) is True


@pytest.mark.unit
class TestFeiShuSheetInsertColumn:
    """测试列插入功能"""

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_insert_column_to_right_with_style(self, mock_get, mock_post,
                                               mock_tenant_token_response,
                                               mock_sheet_metadata_response,
                                               feishu_url):
        """测试向右插入列并继承样式"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        sheet = FeiShuSheet(feishu_url, readonly=False)

        with patch.object(sheet, 'insert_series') as mock_insert:
            sheet.insert_column_to_right('B', insert_number=2, inherit_style=True)

            # B列是第2列，插入2列，应该在第2列和第4列之间插入
            mock_insert.assert_called_once_with(2, 4, "COLUMNS", "BEFORE")

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_insert_column_to_right_without_style(self, mock_get, mock_post,
                                                  mock_tenant_token_response,
                                                  mock_sheet_metadata_response,
                                                  feishu_url):
        """测试向右插入列不继承样式"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        sheet = FeiShuSheet(feishu_url, readonly=False)

        with patch.object(sheet, 'insert_series') as mock_insert:
            sheet.insert_column_to_right('B', insert_number=2, inherit_style=False)

            # 不继承样式时不传 "BEFORE" 参数
            mock_insert.assert_called_once_with(2, 4, "COLUMNS")

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_insert_column_to_left_with_style(self, mock_get, mock_post,
                                              mock_tenant_token_response,
                                              mock_sheet_metadata_response,
                                              feishu_url):
        """测试向左插入列并继承样式"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        sheet = FeiShuSheet(feishu_url, readonly=False)

        with patch.object(sheet, 'insert_series') as mock_insert:
            sheet.insert_column_to_left('B', insert_number=2, inherit_style=True)

            # B列是第2列，向左插入，应该在第1列之后插入
            mock_insert.assert_called_once_with(1, 3, "COLUMNS", "AFTER")
