# 测试指南

本目录包含 fastfeishu 项目的完整测试套件。

## 📁 目录结构

```
tests/
├── conftest.py              # Pytest配置和共享fixtures
├── unit/                    # 单元测试（不依赖外部服务）
│   ├── test_request.py      # FeiShuRequest API层测试
│   ├── test_operations.py   # FeiShuSheetOperations操作层测试
│   ├── test_sheet.py        # FeiShuSheet高层接口测试
│   ├── test_utils.py        # 通用工具函数测试
│   ├── test_partition_grid.py # 网格分区算法测试
│   ├── test_models.py       # SheetProperties等模型测试
│   └── test_types.py        # 单元格类型测试
├── integration/             # 集成测试（需要真实API）
│   ├── test_write_batch.py
│   ├── test_write_row_smart.py
│   └── test_heuristic_accuracy.py
└── fixtures/                # 测试数据fixtures
```

## 🚀 快速开始

### 1. 安装测试依赖

```bash
# 安装所有依赖（包括测试依赖）
pip install -r requirements.txt

# 或者只安装开发/测试依赖
pip install -r requirements-dev.txt
```

### 2. 运行所有测试

```bash
# 运行所有测试
pytest

# 运行测试并显示覆盖率
pytest --cov=fastfeishu --cov-report=html

# 运行测试（详细输出）
pytest -v -s
```

### 3. 运行特定类型的测试

```bash
# 只运行单元测试（快速，不需要API）
pytest -m unit

# 只运行集成测试（需要真实的Feishu API凭证）
pytest -m integration

# 只运行冒烟测试（快速验证）
pytest -m smoke

# 排除慢速测试
pytest -m "not slow"
```

### 4. 运行特定文件或测试

```bash
# 运行单个测试文件
pytest tests/unit/test_request.py

# 运行特定测试类
pytest tests/unit/test_request.py::TestFeiShuRequest

# 运行特定测试方法
pytest tests/unit/test_request.py::TestFeiShuRequest::test_parse_feishu_url_with_sheet_id

# 根据名称模糊匹配运行测试
pytest -k "test_parse"
```

## ✅ 测试标记（Markers）

测试使用pytest标记进行分类：

- `@pytest.mark.unit` - 单元测试，不依赖外部服务，执行快速
- `@pytest.mark.integration` - 集成测试，需要真实的Feishu API
- `@pytest.mark.slow` - 慢速测试，执行时间较长
- `@pytest.mark.smoke` - 冒烟测试，快速验证基本功能

示例：
```python
@pytest.mark.unit
def test_something():
    pass

@pytest.mark.integration
@pytest.mark.slow
def test_real_api():
    pass
```

## 📝 编写新测试

### 单元测试示例

创建新的测试文件 `tests/unit/test_your_module.py`：

```python
"""
你的模块的单元测试
"""

import pytest
from unittest.mock import Mock, patch

from fastfeishu.your_module import YourClass


@pytest.mark.unit
class TestYourClass:
    """YourClass 的测试"""

    def test_basic_functionality(self):
        """测试基本功能"""
        obj = YourClass()
        result = obj.some_method()

        assert result == expected_value

    @patch('fastfeishu.your_module.external_dependency')
    def test_with_mock(self, mock_dep):
        """测试使用mock对象"""
        mock_dep.return_value = "mocked_value"

        obj = YourClass()
        result = obj.method_using_dependency()

        assert result == "expected_result"
        mock_dep.assert_called_once()

    def test_error_handling(self):
        """测试错误处理"""
        obj = YourClass()

        with pytest.raises(ValueError, match="error message"):
            obj.method_that_should_raise()
```

### 使用共享Fixtures

在 `conftest.py` 中定义的fixtures可以在所有测试中使用：

```python
def test_with_fixtures(feishu_url, mock_tenant_token_response):
    """使用共享fixtures"""
    # feishu_url 和 mock_tenant_token_response 自动注入
    assert feishu_url.startswith("https://")
    assert mock_tenant_token_response["code"] == 0
```

### 创建自定义Fixtures

在测试文件中定义局部fixtures：

```python
@pytest.fixture
def sample_data():
    """提供测试数据"""
    return {
        "key": "value",
        "list": [1, 2, 3]
    }

def test_with_custom_fixture(sample_data):
    """使用自定义fixture"""
    assert sample_data["key"] == "value"
```

### 参数化测试

使用 `@pytest.mark.parametrize` 测试多组输入：

```python
@pytest.mark.parametrize("input,expected", [
    (1, "A"),
    (26, "Z"),
    (27, "AA"),
    (702, "ZZ"),
])
def test_num_to_excel_col(input, expected):
    """测试数字转Excel列"""
    from fastfeishu.utils import num_to_excel_col
    assert num_to_excel_col(input) == expected
```

## 🎯 测试最佳实践

### 1. 测试命名规范

- 测试文件：`test_*.py` 或 `*_test.py`
- 测试类：`Test*`（如 `TestFeiShuRequest`）
- 测试函数：`test_*`（如 `test_parse_url`）

### 2. 测试结构（AAA模式）

```python
def test_example():
    # Arrange - 准备测试数据和环境
    obj = MyClass()
    input_data = "test"

    # Act - 执行被测试的操作
    result = obj.process(input_data)

    # Assert - 验证结果
    assert result == expected
```

### 3. Mock外部依赖

单元测试应该隔离外部依赖：

```python
from unittest.mock import patch, Mock

@patch('requests.get')
def test_api_call(mock_get):
    """Mock HTTP请求"""
    mock_response = Mock()
    mock_response.json.return_value = {"data": "test"}
    mock_get.return_value = mock_response

    # 测试代码...
```

### 4. 使用合适的断言

```python
# 基本断言
assert value == expected
assert value != unexpected
assert value > 0
assert value in collection

# 异常断言
with pytest.raises(ValueError):
    function_that_raises()

# 匹配异常消息
with pytest.raises(ValueError, match="specific error"):
    function_that_raises()

# 近似相等（浮点数）
assert result == pytest.approx(3.14, rel=1e-2)
```

### 5. 测试覆盖率目标

- 核心模块（core/）：目标 >80%
- 工具函数（utils/）：目标 >90%
- 模型类（models/）：目标 >70%

查看覆盖率报告：
```bash
pytest --cov=fastfeishu --cov-report=html
# 打开 htmlcov/index.html 查看详细报告
```

## 🔧 常见问题

### Q: 测试运行很慢怎么办？

```bash
# 只运行单元测试（跳过集成测试）
pytest -m unit

# 并行运行测试（需要安装 pytest-xdist）
pip install pytest-xdist
pytest -n auto
```

### Q: 如何调试失败的测试？

```bash
# 显示print输出
pytest -s

# 在第一个失败处停止
pytest -x

# 进入pdb调试器
pytest --pdb

# 显示详细的失败信息
pytest -vv --tb=long
```

### Q: 如何跳过某些测试？

```python
@pytest.mark.skip(reason="暂时跳过")
def test_to_skip():
    pass

@pytest.mark.skipif(sys.version_info < (3, 11), reason="需要Python 3.11+")
def test_requires_py311():
    pass
```

### Q: 集成测试需要什么？

集成测试需要真实的Feishu API凭证，在 `.env` 文件中配置：
```bash
FS_APP_ID=your_app_id
FS_APP_SECRET=your_app_secret
```

运行集成测试：
```bash
pytest -m integration
```

## 📊 持续集成（CI）

项目可以配置CI/CD流程自动运行测试：

```yaml
# .github/workflows/test.yml 示例
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest -m unit --cov=fastfeishu
```

## 📚 更多资源

- [Pytest官方文档](https://docs.pytest.org/)
- [unittest.mock文档](https://docs.python.org/3/library/unittest.mock.html)
- [pytest-cov文档](https://pytest-cov.readthedocs.io/)

## 🤝 贡献指南

添加新功能时，请同时：
1. 编写相应的单元测试
2. 确保所有测试通过：`pytest`
3. 确保覆盖率不降低：`pytest --cov=fastfeishu`
4. 更新相关文档
