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


@pytest.mark.unit
class TestReadRow:
    """read_row 方法的单元测试"""

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_read_row_basic(self, mock_get, mock_post,
                           mock_tenant_token_response,
                           mock_sheet_metadata_response,
                           feishu_url):
        """测试基本行读取功能"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # Mock 获取元数据 (需要两次：初始化时一次，get_header时一次)
        mock_meta_resp1 = Mock()
        mock_meta_resp1.json.return_value = mock_sheet_metadata_response
        mock_meta_resp1.raise_for_status = Mock()

        mock_meta_resp2 = Mock()
        mock_meta_resp2.json.return_value = mock_sheet_metadata_response
        mock_meta_resp2.raise_for_status = Mock()

        # Mock 读取表头
        mock_header_resp = Mock()
        mock_header_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {
                "valueRange": {
                    "values": [["姓名", "年龄", "城市"]]
                }
            }
        }
        mock_header_resp.raise_for_status = Mock()

        # Mock 读取第2行数据（read_human 会调用 read，需要完整的响应结构）
        mock_row_resp = Mock()
        mock_row_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {
                "valueRange": {
                    "range": "TestSheet456!A2:C2",
                    "values": [["张三", 25, "北京"]]
                }
            }
        }
        mock_row_resp.raise_for_status = Mock()

        # 顺序：元数据(初始化) -> 元数据(get_sheet_info) -> 表头 -> 行数据
        mock_get.side_effect = [mock_meta_resp1, mock_meta_resp2, mock_header_resp, mock_row_resp]

        sheet = FeiShuSheet(feishu_url, readonly=True)
        result = sheet.read_row(2)

        # 验证返回字典格式
        assert isinstance(result, dict)
        assert result["姓名"] == "张三"
        assert result["年龄"] == 25
        assert result["城市"] == "北京"

    @pytest.mark.skip(reason="需要额外调查 full_row 模式下的 mock 调用顺序")
    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_read_row_with_full_row(self, mock_get, mock_post,
                                   mock_tenant_token_response,
                                   mock_sheet_metadata_response,
                                   feishu_url):
        """测试读取整行（包含表头范围外的列）"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # Mock 获取元数据
        mock_meta_resp1 = Mock()
        mock_meta_resp1.json.return_value = mock_sheet_metadata_response
        mock_meta_resp1.raise_for_status = Mock()

        mock_meta_resp2 = Mock()
        mock_meta_resp2.json.return_value = mock_sheet_metadata_response
        mock_meta_resp2.raise_for_status = Mock()

        mock_meta_resp3 = Mock()
        mock_meta_resp3.json.return_value = mock_sheet_metadata_response
        mock_meta_resp3.raise_for_status = Mock()

        # Mock 读取表头（只有2列）
        mock_header_resp = Mock()
        mock_header_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {
                "valueRange": {
                    "values": [["姓名", "年龄"]]
                }
            }
        }
        mock_header_resp.raise_for_status = Mock()

        # Mock 读取整行数据（有4列）
        mock_row_resp = Mock()
        mock_row_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {
                "valueRange": {
                    "range": "TestSheet456!A2:Z2",
                    "values": [["张三", 25, "备注信息", "其他数据"]]
                }
            }
        }
        mock_row_resp.raise_for_status = Mock()

        mock_get.side_effect = [mock_meta_resp1, mock_meta_resp2, mock_header_resp, mock_meta_resp3, mock_row_resp]

        sheet = FeiShuSheet(feishu_url, readonly=True)
        result = sheet.read_row(2, full_row=True)

        # 验证返回字典包含表头名称和列字母
        assert result["姓名"] == "张三"
        assert result["年龄"] == 25
        assert result["C"] == "备注信息"  # 超出表头部分使用列字母
        assert result["D"] == "其他数据"

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_read_row_header_row(self, mock_get, mock_post,
                                mock_tenant_token_response,
                                mock_sheet_metadata_response,
                                feishu_url):
        """测试读取第1行（表头行）"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # Mock 获取元数据
        mock_meta_resp1 = Mock()
        mock_meta_resp1.json.return_value = mock_sheet_metadata_response
        mock_meta_resp1.raise_for_status = Mock()

        mock_meta_resp2 = Mock()
        mock_meta_resp2.json.return_value = mock_sheet_metadata_response
        mock_meta_resp2.raise_for_status = Mock()

        # Mock 读取表头
        mock_header_resp = Mock()
        mock_header_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {
                "valueRange": {
                    "values": [["姓名", "年龄", "城市"]]
                }
            }
        }
        mock_header_resp.raise_for_status = Mock()

        # Mock 读取第1行（表头行本身）
        mock_row_resp = Mock()
        mock_row_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {
                "valueRange": {
                    "range": "TestSheet456!A1:C1",
                    "values": [["姓名", "年龄", "城市"]]
                }
            }
        }
        mock_row_resp.raise_for_status = Mock()

        mock_get.side_effect = [mock_meta_resp1, mock_meta_resp2, mock_header_resp, mock_row_resp]

        sheet = FeiShuSheet(feishu_url, readonly=True)
        result = sheet.read_row(1)

        # 验证读取第1行时使用列字母作为键
        assert result["A"] == "姓名"
        assert result["B"] == "年龄"
        assert result["C"] == "城市"

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_read_row_with_read_raw_method(self, mock_get, mock_post,
                                          mock_tenant_token_response,
                                          mock_sheet_metadata_response,
                                          feishu_url):
        """测试使用 read_raw 方法读取（包含公式）"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # Mock 获取元数据
        mock_meta_resp1 = Mock()
        mock_meta_resp1.json.return_value = mock_sheet_metadata_response
        mock_meta_resp1.raise_for_status = Mock()

        mock_meta_resp2 = Mock()
        mock_meta_resp2.json.return_value = mock_sheet_metadata_response
        mock_meta_resp2.raise_for_status = Mock()

        # Mock 读取表头
        mock_header_resp = Mock()
        mock_header_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {
                "valueRange": {
                    "values": [["姓名", "年龄", "出生年份"]]
                }
            }
        }
        mock_header_resp.raise_for_status = Mock()

        mock_get.side_effect = [mock_meta_resp1, mock_meta_resp2, mock_header_resp]

        sheet = FeiShuSheet(feishu_url, readonly=True)

        # 创建自定义的 read_method mock
        def mock_read_raw(range_str):
            return [["李四", 30, "=2024-B2"]]

        result = sheet.read_row(2, read_method=mock_read_raw)

        # 验证返回包含公式
        assert result["姓名"] == "李四"
        assert result["年龄"] == 30
        assert result["出生年份"] == "=2024-B2"  # 公式未计算

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_read_row_empty_cells(self, mock_get, mock_post,
                                 mock_tenant_token_response,
                                 mock_sheet_metadata_response,
                                 feishu_url):
        """测试读取包含空单元格的行"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # Mock 获取元数据
        mock_meta_resp1 = Mock()
        mock_meta_resp1.json.return_value = mock_sheet_metadata_response
        mock_meta_resp1.raise_for_status = Mock()

        mock_meta_resp2 = Mock()
        mock_meta_resp2.json.return_value = mock_sheet_metadata_response
        mock_meta_resp2.raise_for_status = Mock()

        # Mock 读取表头
        mock_header_resp = Mock()
        mock_header_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {
                "valueRange": {
                    "values": [["姓名", "年龄", "城市"]]
                }
            }
        }
        mock_header_resp.raise_for_status = Mock()

        # Mock 读取包含 None 的行
        mock_row_resp = Mock()
        mock_row_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {
                "valueRange": {
                    "range": "TestSheet456!A2:C2",
                    "values": [["王五", None, "上海"]]
                }
            }
        }
        mock_row_resp.raise_for_status = Mock()

        mock_get.side_effect = [mock_meta_resp1, mock_meta_resp2, mock_header_resp, mock_row_resp]

        sheet = FeiShuSheet(feishu_url, readonly=True)
        result = sheet.read_row(2)

        # 验证空单元格处理
        assert result["姓名"] == "王五"
        assert result["年龄"] is None
        assert result["城市"] == "上海"

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_read_row_with_none_header(self, mock_get, mock_post,
                                      mock_tenant_token_response,
                                      mock_sheet_metadata_response,
                                      feishu_url):
        """测试表头包含None值时使用列字母索引"""
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # Mock 获取元数据
        mock_meta_resp1 = Mock()
        mock_meta_resp1.json.return_value = mock_sheet_metadata_response
        mock_meta_resp1.raise_for_status = Mock()

        mock_meta_resp2 = Mock()
        mock_meta_resp2.json.return_value = mock_sheet_metadata_response
        mock_meta_resp2.raise_for_status = Mock()

        # Mock 读取表头（第二列为None，第三列为空字符串）
        mock_header_resp = Mock()
        mock_header_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {
                "valueRange": {
                    "values": [["姓名", None, "", "城市"]]
                }
            }
        }
        mock_header_resp.raise_for_status = Mock()

        # Mock 读取第2行数据
        mock_row_resp = Mock()
        mock_row_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {
                "valueRange": {
                    "range": "TestSheet456!A2:D2",
                    "values": [["张三", 25, "测试", "北京"]]
                }
            }
        }
        mock_row_resp.raise_for_status = Mock()

        mock_get.side_effect = [mock_meta_resp1, mock_meta_resp2, mock_header_resp, mock_row_resp]

        sheet = FeiShuSheet(feishu_url, readonly=True)
        result = sheet.read_row(2)

        # 验证：表头有值用表头名，表头为None或空字符串用列字母
        assert result["姓名"] == "张三"      # 第一列，表头有值
        assert result["B"] == 25           # 第二列，表头为None，使用列字母
        assert result["C"] == "测试"       # 第三列，表头为空字符串，使用列字母
        assert result["城市"] == "北京"    # 第四列，表头有值

        # 确保结果中没有None或空字符串作为键
        assert None not in result
        assert "" not in result


@pytest.mark.unit
class TestReadRows:
    """测试 read_rows 批量读取多行方法"""

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_read_rows_basic(self, mock_get, mock_post,
                            mock_tenant_token_response,
                            mock_sheet_metadata_response,
                            feishu_url):
        """测试基本的批量读取多行功能"""
        # Mock tenant token
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # Mock metadata（初始化需要）
        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()

        # Mock 读取表头
        mock_header_resp = Mock()
        mock_header_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {
                "valueRange": {
                    "values": [["姓名", "年龄", "城市"]]
                }
            }
        }
        mock_header_resp.raise_for_status = Mock()

        # Mock read_batch 批量读取响应
        mock_batch_resp = Mock()
        mock_batch_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {
                "revision": 87,
                "spreadsheetToken": "TestToken123",
                "totalCells": 9,
                "valueRanges": [
                    {
                        "majorDimension": "ROWS",
                        "range": "TestSheet456!A2:C2",
                        "revision": 87,
                        "values": [["张三", 25, "北京"]]
                    },
                    {
                        "majorDimension": "ROWS",
                        "range": "TestSheet456!A3:C3",
                        "revision": 87,
                        "values": [["李四", 30, "上海"]]
                    },
                    {
                        "majorDimension": "ROWS",
                        "range": "TestSheet456!A5:C5",
                        "revision": 87,
                        "values": [["王五", 28, "广州"]]
                    }
                ]
            }
        }
        mock_batch_resp.raise_for_status = Mock()

        # 调用顺序：初始化metadata -> 读取header -> read_batch
        mock_get.side_effect = [
            mock_meta_resp,    # 初始化 metadata
            mock_header_resp,  # 读取表头
            mock_batch_resp    # read_batch
        ]

        sheet = FeiShuSheet(feishu_url, readonly=True)
        result = sheet.read_rows([2, 3, 5])

        # 验证返回值
        assert len(result) == 3
        assert result[0] == {"姓名": "张三", "年龄": 25, "城市": "北京"}
        assert result[1] == {"姓名": "李四", "年龄": 30, "城市": "上海"}
        assert result[2] == {"姓名": "王五", "年龄": 28, "城市": "广州"}

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_read_rows_with_full_row(self, mock_get, mock_post,
                                     mock_tenant_token_response,
                                     mock_sheet_metadata_response,
                                     feishu_url):
        """测试读取整行（包含表头范围外的列）"""
        # Mock tenant token
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # Mock metadata（初始化需要）
        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()

        # Mock 读取表头
        mock_header_resp = Mock()
        mock_header_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {
                "valueRange": {
                    "values": [["姓名", "年龄"]]
                }
            }
        }
        mock_header_resp.raise_for_status = Mock()

        # Mock read_batch 响应（包含表头范围外的列）
        mock_batch_resp = Mock()
        mock_batch_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {
                "revision": 87,
                "spreadsheetToken": "TestToken123",
                "totalCells": 8,
                "valueRanges": [
                    {
                        "majorDimension": "ROWS",
                        "range": "TestSheet456!A2:Z2",
                        "revision": 87,
                        "values": [["张三", 25, "备注1", "其他1"]]
                    },
                    {
                        "majorDimension": "ROWS",
                        "range": "TestSheet456!A3:Z3",
                        "revision": 87,
                        "values": [["李四", 30, "备注2", "其他2"]]
                    }
                ]
            }
        }
        mock_batch_resp.raise_for_status = Mock()

        # 调用顺序：初始化metadata -> 读取header -> read_batch
        # 因为 full_row 不再单独调用 get_sheet_info，所以和 full_row=False 一样
        mock_get.side_effect = [
            mock_meta_resp,    # 初始化 metadata
            mock_header_resp,  # 读取表头
            mock_batch_resp    # read_batch
        ]

        sheet = FeiShuSheet(feishu_url, readonly=True)
        result = sheet.read_rows([2, 3], full_row=True)

        # 验证返回值（包含表头范围外的列，使用字母索引）
        assert len(result) == 2
        assert result[0]["姓名"] == "张三"
        assert result[0]["年龄"] == 25
        assert result[0]["C"] == "备注1"  # 表头范围外，使用列字母
        assert result[0]["D"] == "其他1"
        assert result[1]["姓名"] == "李四"
        assert result[1]["年龄"] == 30
        assert result[1]["C"] == "备注2"
        assert result[1]["D"] == "其他2"

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_read_rows_empty_list(self, mock_get, mock_post,
                                  mock_tenant_token_response,
                                  mock_sheet_metadata_response,
                                  feishu_url):
        """测试空行号列表"""
        # Mock tenant token
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # Mock metadata
        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()

        mock_get.side_effect = [mock_meta_resp]

        sheet = FeiShuSheet(feishu_url, readonly=True)
        result = sheet.read_rows([])

        # 验证空列表返回空数组
        assert result == []

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_read_rows_with_none_header(self, mock_get, mock_post,
                                       mock_tenant_token_response,
                                       mock_sheet_metadata_response,
                                       feishu_url):
        """测试表头为None时使用列字母索引"""
        # Mock tenant token
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # Mock metadata（初始化需要）
        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()

        # Mock 读取表头（第二列为None，第三列为空字符串）
        mock_header_resp = Mock()
        mock_header_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {
                "valueRange": {
                    "values": [["姓名", None, "", "城市"]]
                }
            }
        }
        mock_header_resp.raise_for_status = Mock()

        # Mock read_batch 响应
        mock_batch_resp = Mock()
        mock_batch_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {
                "revision": 87,
                "spreadsheetToken": "TestToken123",
                "totalCells": 8,
                "valueRanges": [
                    {
                        "majorDimension": "ROWS",
                        "range": "TestSheet456!A2:D2",
                        "revision": 87,
                        "values": [["张三", 25, "测试1", "北京"]]
                    },
                    {
                        "majorDimension": "ROWS",
                        "range": "TestSheet456!A3:D3",
                        "revision": 87,
                        "values": [["李四", 30, "测试2", "上海"]]
                    }
                ]
            }
        }
        mock_batch_resp.raise_for_status = Mock()

        # 调用顺序：初始化metadata -> 读取header -> read_batch
        mock_get.side_effect = [
            mock_meta_resp,    # 初始化 metadata
            mock_header_resp,  # 读取表头
            mock_batch_resp    # read_batch
        ]

        sheet = FeiShuSheet(feishu_url, readonly=True)
        result = sheet.read_rows([2, 3])

        # 验证：表头有值用表头名，表头为None或空字符串用列字母
        assert len(result) == 2

        # 第一行
        assert result[0]["姓名"] == "张三"
        assert result[0]["B"] == 25  # 表头为None，使用列字母
        assert result[0]["C"] == "测试1"  # 表头为空字符串，使用列字母
        assert result[0]["城市"] == "北京"

        # 第二行
        assert result[1]["姓名"] == "李四"
        assert result[1]["B"] == 30
        assert result[1]["C"] == "测试2"
        assert result[1]["城市"] == "上海"

        # 确保结果中没有None或空字符串作为键
        for row in result:
            assert None not in row
            assert "" not in row

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_read_rows_include_header_row(self, mock_get, mock_post,
                                         mock_tenant_token_response,
                                         mock_sheet_metadata_response,
                                         feishu_url):
        """测试包含表头行（第1行）的批量读取"""
        # Mock tenant token
        mock_token_resp = Mock()
        mock_token_resp.json.return_value = mock_tenant_token_response
        mock_post.return_value = mock_token_resp

        # Mock metadata（初始化需要）
        mock_meta_resp = Mock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.raise_for_status = Mock()

        # Mock 读取表头
        mock_header_resp = Mock()
        mock_header_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {
                "valueRange": {
                    "values": [["姓名", "年龄", "城市"]]
                }
            }
        }
        mock_header_resp.raise_for_status = Mock()

        # Mock read_batch 响应（包含第1行）
        mock_batch_resp = Mock()
        mock_batch_resp.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {
                "revision": 87,
                "spreadsheetToken": "TestToken123",
                "totalCells": 6,
                "valueRanges": [
                    {
                        "majorDimension": "ROWS",
                        "range": "TestSheet456!A1:C1",
                        "revision": 87,
                        "values": [["姓名", "年龄", "城市"]]
                    },
                    {
                        "majorDimension": "ROWS",
                        "range": "TestSheet456!A2:C2",
                        "revision": 87,
                        "values": [["张三", 25, "北京"]]
                    }
                ]
            }
        }
        mock_batch_resp.raise_for_status = Mock()

        # 调用顺序：初始化metadata -> 读取header -> read_batch
        mock_get.side_effect = [
            mock_meta_resp,    # 初始化 metadata
            mock_header_resp,  # 读取表头
            mock_batch_resp    # read_batch
        ]

        sheet = FeiShuSheet(feishu_url, readonly=True)
        result = sheet.read_rows([1, 2])

        # 验证返回值
        assert len(result) == 2

        # 第1行（表头行）使用列字母作为键
        assert result[0] == {"A": "姓名", "B": "年龄", "C": "城市"}

        # 第2行使用表头名称作为键
        assert result[1] == {"姓名": "张三", "年龄": 25, "城市": "北京"}


@pytest.mark.unit
class TestCheckColumns:
    """测试列存在性检测方法"""

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_check_columns_exist_all_exist(self, mock_get, mock_post,
                                          mock_tenant_token_response,
                                          mock_sheet_metadata_response,
                                          mock_read_response,
                                          feishu_url):
        """测试所有列都存在的情况"""
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
        result = sheet.check_columns_exist(["CaseID", "查询"])

        # 验证返回字典格式，所有列都存在
        assert isinstance(result, dict)
        assert result["CaseID"] is True
        assert result["查询"] is True

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_check_columns_exist_partial(self, mock_get, mock_post,
                                        mock_tenant_token_response,
                                        mock_sheet_metadata_response,
                                        mock_read_response,
                                        feishu_url):
        """测试部分列存在的情况"""
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
        result = sheet.check_columns_exist(["CaseID", "不存在的列", "查询"])

        # 验证返回字典格式，只有部分列存在
        assert isinstance(result, dict)
        assert result["CaseID"] is True
        assert result["不存在的列"] is False
        assert result["查询"] is True

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_check_columns_exist_none_exist(self, mock_get, mock_post,
                                           mock_tenant_token_response,
                                           mock_sheet_metadata_response,
                                           mock_read_response,
                                           feishu_url):
        """测试所有列都不存在的情况"""
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
        result = sheet.check_columns_exist(["不存在列1", "不存在列2"])

        # 验证返回字典格式，所有列都不存在
        assert isinstance(result, dict)
        assert result["不存在列1"] is False
        assert result["不存在列2"] is False

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_check_columns_exist_empty_list(self, mock_get, mock_post,
                                           mock_tenant_token_response,
                                           mock_sheet_metadata_response,
                                           mock_read_response,
                                           feishu_url):
        """测试空数组的情况"""
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
        result = sheet.check_columns_exist([])

        # 验证返回空字典
        assert isinstance(result, dict)
        assert result == {}

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_has_columns_all_exist(self, mock_get, mock_post,
                                  mock_tenant_token_response,
                                  mock_sheet_metadata_response,
                                  mock_read_response,
                                  feishu_url):
        """测试所有列都存在时返回 True"""
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
        result = sheet.has_columns(["CaseID", "查询"])

        # 验证所有列都存在时返回 True
        assert result is True

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_has_columns_partial_exist(self, mock_get, mock_post,
                                      mock_tenant_token_response,
                                      mock_sheet_metadata_response,
                                      mock_read_response,
                                      feishu_url):
        """测试部分列存在时返回 False"""
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
        result = sheet.has_columns(["CaseID", "不存在的列"])

        # 验证部分列不存在时返回 False
        assert result is False

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_has_columns_none_exist(self, mock_get, mock_post,
                                   mock_tenant_token_response,
                                   mock_sheet_metadata_response,
                                   mock_read_response,
                                   feishu_url):
        """测试所有列都不存在时返回 False"""
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
        result = sheet.has_columns(["不存在列1", "不存在列2"])

        # 验证所有列都不存在时返回 False
        assert result is False

    @patch('fastfeishu.core.request.requests.post')
    @patch('fastfeishu.core.request.requests.get')
    def test_has_columns_empty_list(self, mock_get, mock_post,
                                   mock_tenant_token_response,
                                   mock_sheet_metadata_response,
                                   mock_read_response,
                                   feishu_url):
        """测试空数组时返回 True（all([]) 在 Python 中为 True）"""
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
        result = sheet.has_columns([])

        # 验证空数组时返回 True（all([]) 为 True）
        assert result is True
