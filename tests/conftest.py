"""
Pytest 配置和共享 Fixtures

此文件提供了整个测试套件共享的 fixtures 和配置。
"""

import os
import pytest
from typing import Dict, Any, List
from unittest.mock import Mock, MagicMock
import requests


# ================================
# 环境配置 Fixtures
# ================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """
    自动设置测试环境变量（仅用于单元测试）

    如果环境变量已存在（如集成测试配置了真实值），则不覆盖。
    """
    # 只有当环境变量不存在时才设置假值（用于单元测试）
    if "FS_APP_ID" not in os.environ:
        os.environ["FS_APP_ID"] = "test_app_id"

    if "FS_APP_SECRET" not in os.environ:
        os.environ["FS_APP_SECRET"] = "test_app_secret"

    yield
    # 清理可以在这里进行


@pytest.fixture
def feishu_url():
    """提供测试用的飞书URL（单元测试用）"""
    return "https://li.feishu.cn/sheets/TestToken123?sheet=TestSheet456"


@pytest.fixture
def sheet_token():
    """提供测试用的 sheet token"""
    return "TestToken123"


@pytest.fixture
def sheet_id():
    """提供测试用的 sheet id"""
    return "TestSheet456"


# ================================
# 集成测试专用 Fixtures
# ================================
#
# 大多数测试应该直接使用：
#   from tests.integration.config import get_test_sheet_url
#   url = get_test_sheet_url("main")
#   sheet = FeiShuSheet(url)
#
# 只有需要自动清理数据的测试才使用 clean_sheet fixture

@pytest.fixture
def clean_sheet():
    """
    提供一个干净的测试表格（每次测试前清空数据）

    这个 fixture 会自动清理数据，适合需要干净环境的测试。
    如果表格未配置，测试会自动跳过。

    示例：
        def test_write(clean_sheet):
            clean_sheet.write_row([{"name": "test"}], write_row=2)
            # 测试后会自动清理数据
    """
    from fastfeishu.core import FeiShuSheet
    from tests.integration.config import get_test_sheet_url

    try:
        url = get_test_sheet_url("main")
    except ValueError as e:
        pytest.skip(f"集成测试表格未配置: {e}")

    sheet = FeiShuSheet(url)

    # 测试前：清空所有数据行（保留表头）
    try:
        info = sheet.get_sheet_info()
        if info["rowCount"] > 1:
            sheet.delete_series(2, info["rowCount"], "ROWS")
    except Exception:
        # 如果清理失败（如表格为空），继续执行
        pass

    yield sheet

    # 测试后：再次清理
    try:
        info = sheet.get_sheet_info()
        if info["rowCount"] > 1:
            sheet.delete_series(2, info["rowCount"], "ROWS")
    except Exception:
        pass


# ================================
# Mock API 响应 Fixtures
# ================================

@pytest.fixture
def mock_tenant_token_response():
    """模拟获取 tenant token 的响应"""
    return {
        "code": 0,
        "msg": "success",
        "tenant_access_token": "mock_tenant_token_12345",
        "expire": 7200
    }


@pytest.fixture
def mock_sheet_metadata_response():
    """模拟获取 sheet metadata 的响应"""
    return {
        "code": 0,
        "msg": "success",
        "data": {
            "spreadsheetToken": "TestToken123",
            "properties": {
                "title": "测试表格",
                "ownerUser": 123456,
                "sheetCount": 1,
                "revision": 10
            },
            "sheets": [
                {
                    "sheetId": "TestSheet456",
                    "title": "Sheet1",
                    "index": 0,
                    "rowCount": 100,
                    "columnCount": 26,
                    "frozenRowCount": 0,
                    "frozenColCount": 0,
                    "hidden": False
                }
            ]
        }
    }


@pytest.fixture
def mock_read_response():
    """模拟读取数据的响应"""
    return {
        "code": 0,
        "msg": "success",
        "data": {
            "valueRange": {
                "range": "TestSheet456!A1:C3",
                "revision": 10,
                "values": [
                    ["CaseID", "查询", "意图类型"],
                    ["1", "测试查询1", "type1"],
                    ["2", "测试查询2", "type2"]
                ]
            }
        }
    }


@pytest.fixture
def mock_write_response():
    """模拟写入数据的响应"""
    return {
        "code": 0,
        "msg": "success",
        "data": {
            "spreadsheetToken": "TestToken123",
            "revision": 11,
            "updatedCells": 6,
            "updatedColumns": 3,
            "updatedRange": "TestSheet456!A2:C3",
            "updatedRows": 2
        }
    }


@pytest.fixture
def mock_sheet_info_response():
    """模拟 sheet info 响应"""
    mock_response = Mock(spec=requests.Response)
    mock_response.json.return_value = {
        "code": 0,
        "msg": "success",
        "data": {
            "sheets": [
                {
                    "sheetId": "TestSheet456",
                    "title": "Sheet1",
                    "index": 0,
                    "rowCount": 100,
                    "columnCount": 26
                }
            ]
        }
    }
    mock_response.status_code = 200
    return mock_response


# ================================
# Mock 对象 Fixtures
# ================================

@pytest.fixture
def mock_feishu_request(
    mock_tenant_token_response,
    mock_sheet_metadata_response,
    mock_read_response,
    mock_write_response,
    mock_sheet_info_response
):
    """提供一个完整的 mock FeiShuRequest 对象"""
    from unittest.mock import patch, MagicMock

    with patch('fastfeishu.core.request.requests') as mock_requests:
        # Mock tenant token 请求
        mock_token_resp = MagicMock()
        mock_token_resp.json.return_value = mock_tenant_token_response

        # Mock metadata 请求
        mock_meta_resp = MagicMock()
        mock_meta_resp.json.return_value = mock_sheet_metadata_response
        mock_meta_resp.status_code = 200

        # Mock read 请求
        mock_read_resp = MagicMock()
        mock_read_resp.json.return_value = mock_read_response
        mock_read_resp.status_code = 200

        # Mock write 请求
        mock_write_resp = MagicMock()
        mock_write_resp.json.return_value = mock_write_response
        mock_write_resp.status_code = 200

        # 设置返回值序列
        mock_requests.post.return_value = mock_token_resp
        mock_requests.get.return_value = mock_meta_resp
        mock_requests.put.return_value = mock_write_resp

        yield mock_requests


# ================================
# 测试数据 Fixtures
# ================================

@pytest.fixture
def sample_header():
    """示例表头数据"""
    return ["CaseID", "查询", "意图类型", "端到端回复", "状态"]


@pytest.fixture
def sample_data_rows():
    """示例数据行"""
    return [
        ["1", "查询1", "type1", "回复1", "完成"],
        ["2", "查询2", "type2", "回复2", "进行中"],
        ["3", "查询3", "type3", "回复3", "完成"]
    ]


@pytest.fixture
def sample_dict_data():
    """示例字典格式数据"""
    return [
        {"CaseID": "1", "查询": "查询1", "意图类型": "type1"},
        {"CaseID": "2", "查询": "查询2", "意图类型": "type2"},
        {"CaseID": "3", "查询": "查询3", "意图类型": "type3"}
    ]


@pytest.fixture
def sample_grid_with_none():
    """包含 None 的稀疏网格数据"""
    return [
        [1, None, 3, None],
        [None, 5, None, 7],
        [8, None, None, 11]
    ]


# ================================
# 工具函数
# ================================

def create_mock_response(data: Dict[str, Any], status_code: int = 200) -> Mock:
    """创建一个 mock 的 requests.Response 对象

    Args:
        data: 响应的 JSON 数据
        status_code: HTTP 状态码

    Returns:
        Mock 对象模拟 requests.Response
    """
    mock_response = Mock(spec=requests.Response)
    mock_response.json.return_value = data
    mock_response.status_code = status_code
    mock_response.raise_for_status = Mock()
    return mock_response


# ================================
# Pytest 配置钩子
# ================================

def pytest_configure(config):
    """Pytest 配置钩子"""
    config.addinivalue_line(
        "markers", "unit: 单元测试（不依赖外部服务）"
    )
    config.addinivalue_line(
        "markers", "integration: 集成测试（需要真实的Feishu API）"
    )
    config.addinivalue_line(
        "markers", "slow: 慢速测试（执行时间较长）"
    )
    config.addinivalue_line(
        "markers", "smoke: 冒烟测试（快速验证基本功能）"
    )


def pytest_collection_modifyitems(config, items):
    """
    自动标记测试
    - integration 目录下的测试自动标记为 integration
    - unit 目录下的测试自动标记为 unit
    """
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
