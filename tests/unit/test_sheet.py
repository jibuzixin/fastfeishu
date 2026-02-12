"""
FeiShuSheet 类的单元测试

测试高层API接口的功能。
"""

import pytest
from unittest.mock import patch, Mock

from fastfeishu.core.sheet import FeiShuSheet
from fastfeishu.exceptions.exception import FeiShuColumnNotExist


@pytest.mark.unit
class TestFeiShuSheet:
    """FeiShuSheet 类的测试"""

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_get_index_by_col_name_success(self, mock_get, mock_post,
                                          mock_tenant_token_response,
                                          mock_sheet_metadata_response,
                                          mock_read_response,
                                          feishu_url):
        """测试根据列名获取索引"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()

        mock_read_resp = Mock()
        mock_read_resp.json.return_value = mock_read_response
        mock_read_resp.raise_for_status = Mock()

        mock_get.side_effect = [mock_meta_resp, mock_read_resp]

        sheet = FeiShuSheet(feishu_url, readonly=True)
        index = sheet.get_index_by_col_name("查询")

        # "查询" 是第二列，索引应该是 2
        assert index == 2

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_get_index_by_col_name_not_found(self, mock_get, mock_post,
                                            mock_tenant_token_response,
                                            mock_sheet_metadata_response,
                                            mock_read_response,
                                            feishu_url):
        """测试列名不存在时抛出异常"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()

        mock_read_resp = Mock()
        mock_read_resp.json.return_value = mock_read_response
        mock_read_resp.raise_for_status = Mock()

        mock_get.side_effect = [mock_meta_resp, mock_read_resp]

        sheet = FeiShuSheet(feishu_url, readonly=True)

        with pytest.raises(FeiShuColumnNotExist):
            sheet.get_index_by_col_name("不存在的列")

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_get_letter_by_col_name(self, mock_get, mock_post,
                                   mock_tenant_token_response,
                                   mock_sheet_metadata_response,
                                   mock_read_response,
                                   feishu_url):
        """测试根据列名获取字母索引"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()

        mock_read_resp = Mock()
        mock_read_resp.json.return_value = mock_read_response
        mock_read_resp.raise_for_status = Mock()

        mock_get.side_effect = [mock_meta_resp, mock_read_resp]

        sheet = FeiShuSheet(feishu_url, readonly=True)
        letter = sheet.get_letter_by_col_name("CaseID")

        # "CaseID" 是第一列，字母应该是 A
        assert letter == "A"

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_convert_data_to_grid_with_dict(self, mock_get, mock_post,
                                           mock_tenant_token_response,
                                           mock_sheet_metadata_response,
                                           feishu_url,
                                           sample_header,
                                           sample_dict_data):
        """测试将字典数据转换为网格"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        sheet = FeiShuSheet(feishu_url, readonly=False)

        # 测试字典转换
        grid, header, heads_len = sheet._convert_data_to_grid(
            sample_dict_data,
            sample_header,
            write_row=2
        )

        assert len(grid) == 3
        assert grid[0][0] == "1"  # CaseID
        assert grid[0][1] == "查询1"  # 查询
        assert heads_len == len(sample_header)

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_convert_data_to_grid_with_list(self, mock_get, mock_post,
                                          mock_tenant_token_response,
                                          mock_sheet_metadata_response,
                                          feishu_url,
                                          sample_header,
                                          sample_data_rows):
        """测试将列表数据转换为网格"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        sheet = FeiShuSheet(feishu_url, readonly=False)

        # 测试列表转换
        grid, header, heads_len = sheet._convert_data_to_grid(
            sample_data_rows,
            sample_header,
            write_row=2
        )

        assert len(grid) == 3
        assert grid[0] == sample_data_rows[0]
        assert heads_len == len(sample_header)

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_convert_data_to_grid_write_to_row_one(self, mock_get, mock_post,
                                                   mock_tenant_token_response,
                                                   mock_sheet_metadata_response,
                                                   feishu_url):
        """测试写入第一行（表头行）"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        sheet = FeiShuSheet(feishu_url, readonly=False)

        # 写入第一行必须是列表格式
        data = [
            ["新表头1", "新表头2", "新表头3"],
            ["数据1", "数据2", "数据3"]
        ]

        grid, header, heads_len = sheet._convert_data_to_grid(
            data,
            ["旧表头1", "旧表头2"],
            write_row=1
        )

        # 第一行被识别为新表头
        assert header == ["新表头1", "新表头2", "新表头3"]
        assert len(grid) == 2

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_convert_data_invalid_type(self, mock_get, mock_post,
                                      mock_tenant_token_response,
                                      mock_sheet_metadata_response,
                                      feishu_url,
                                      sample_header):
        """测试无效数据类型"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()
        mock_get.return_value = mock_meta_resp

        sheet = FeiShuSheet(feishu_url, readonly=False)

        # 传入无效类型（字符串）
        with pytest.raises(ValueError, match="需要写入的值可以是二维数组"):
            sheet._convert_data_to_grid(
                ["string_value"],  # 应该是列表或字典
                sample_header,
                write_row=2
            )
