# 测试指南

本文档提供 fastfeishu 项目的完整测试指南，包括单元测试和集成测试。

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
│   ├── test_types.py        # 单元格类型测试
│   ├── test_common.py       # 工具函数测试
│   ├── test_helpers.py      # helpers模块测试
│   ├── test_feishu_util.py  # FeiShuUtil工具类测试
│   └── test_sheet_advanced.py # Sheet高级功能测试
├── integration/             # 集成测试（需要真实API）
│   └── (参见集成测试指南)
└── fixtures/                # 测试数据fixtures
```

## 📊 当前测试覆盖率

| 模块 | 覆盖率 | 测试数量 | 状态 |
|------|--------|---------|------|
| **整体** | **57%** | **123个** | ✅ 良好 |
| fastfeishu/helpers.py | 95% | 13个 | 🌟 优秀 |
| fastfeishu/utils/feishu_util.py | 100% | 9个 | 🌟 完美 |
| fastfeishu/models/cell_style.py | 93% | 15个 | ✅ 优秀 |
| fastfeishu/models/feishu_cfg.py | 91% | 6个 | ✅ 优秀 |
| fastfeishu/core/request.py | 52% | 10个 | 📈 中等 |
| fastfeishu/utils/common.py | 48% | 36个 | 📈 改善 |
| fastfeishu/core/operations.py | 44% | 8个 | 📊 待提升 |
| fastfeishu/core/sheet.py | 38% | 14个 | 📊 待提升 |

---

## 🚀 快速开始

### 1. 安装测试依赖

```bash
# 方式1：使用开发环境一键安装脚本
./setup_dev.sh

# 方式2：手动安装
pip install -r requirements-dev.txt

# 方式3：只安装项目依赖
pip install -r requirements.txt
```

### 2. 运行所有测试

```bash
# 运行所有单元测试（推荐）
pytest tests/unit -v -m unit

# 运行测试并显示覆盖率
pytest tests/unit -m unit --cov=fastfeishu --cov-report=html

# 运行测试（详细输出）
pytest tests/unit -v -s -m unit
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

---

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

---

## 📝 编写单元测试

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
    from fastfeishu.helpers import num_to_excel_col
    assert num_to_excel_col(input) == expected
```

---

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

- 核心模块（core/）：目标 >70%
- 工具函数（utils/）：目标 >80%
- 模型类（models/）：目标 >80%

查看覆盖率报告：
```bash
pytest tests/unit -m unit --cov=fastfeishu --cov-report=html
# 打开 htmlcov/index.html 查看详细报告
```

---

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

### Q: 单元测试 vs 集成测试的区别？

| 特性 | 单元测试 | 集成测试 |
|------|---------|---------|
| **依赖** | 使用 Mock，隔离外部依赖 | 使用真实API |
| **速度** | 快速（秒级） | 较慢（分钟级） |
| **环境** | 不需要配置 | 需要API凭证 |
| **覆盖** | 逻辑正确性 | 真实场景验证 |
| **运行时机** | 每次提交/推送 | PR时或手动运行 |

**何时使用单元测试**：
- ✅ 测试纯函数逻辑
- ✅ 测试数据转换
- ✅ 测试参数校验
- ✅ 测试错误处理

**何时需要集成测试**：
- ⚠️ 真实API调用行为
- ⚠️ 复杂的端到端流程
- ⚠️ 性能和并发测试
- ⚠️ 网络异常恢复

详见：[集成测试指南](./INTEGRATION_TESTS.md)

---

## 📊 持续集成（CI）

项目已配置 GitHub Actions 自动运行测试：

```yaml
# .github/workflows/test.yml
name: Unit Tests
on:
  pull_request:
    branches: [ main, dev ]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -r requirements-dev.txt
      - run: pytest tests/unit -v -m unit --cov=fastfeishu
```

**CI 流程**：
- ✅ PR 时自动运行单元测试
- ✅ 多 Python 版本测试（3.11, 3.12）
- ✅ 生成覆盖率报告
- ✅ 测试失败时阻止合并

---

## 📚 相关文档

- **[集成测试指南](./INTEGRATION_TESTS.md)** - 如何编写和运行集成测试
- **[开发者贡献指南](./CONTRIBUTING.md)** - 开发工作流和代码规范
- **[项目架构指南](./CLAUDE.md)** - 架构设计和开发模式
- [Pytest官方文档](https://docs.pytest.org/)
- [unittest.mock文档](https://docs.python.org/3/library/unittest.mock.html)
- [pytest-cov文档](https://pytest-cov.readthedocs.io/)

---

## 🤝 贡献指南

添加新功能时，请同时：

1. ✅ 编写相应的单元测试
2. ✅ 确保所有测试通过：`pytest tests/unit -m unit`
3. ✅ 确保覆盖率不降低：`pytest tests/unit -m unit --cov=fastfeishu`
4. ✅ 更新相关文档
5. ✅ 遵循代码规范和Commit规范

**测试驱动开发（TDD）工作流**：
```bash
# 1. 编写失败的测试
# 2. 编写最少的代码使测试通过
# 3. 重构代码
# 4. 重复

pytest tests/unit/test_your_module.py -v
```

---

## 🎉 测试覆盖里程碑

| 里程碑 | 覆盖率 | 状态 | 日期 |
|--------|--------|------|------|
| 初始版本 | ~30% | ✅ | 2024 |
| 添加基础测试 | 48% | ✅ | 2025-02 |
| **当前** | **57%** | ✅ | 2025-02-13 |
| 下一目标 | 65% | 🎯 | - |
| 最终目标 | 70%+ | 🚀 | - |

**最近改进**：
- ✅ 新增 helpers.py 测试（95% 覆盖率）
- ✅ 新增 feishu_util.py 测试（100% 覆盖率）
- ✅ 新增 common.py 测试（48% 覆盖率）
- ✅ 新增 sheet 高级功能测试
- ✅ 测试数量从 66 个增加到 123 个

---

**记住**：好的测试是代码质量的保障！编写测试不是负担，而是对未来自己的投资。🎯
