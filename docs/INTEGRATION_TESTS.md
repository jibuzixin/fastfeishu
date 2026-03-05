# 集成测试指南

## 📖 概述

本文档说明哪些功能应该编写集成测试，以及如何编写集成测试。

**单元测试 vs 集成测试**：
- ✅ **单元测试**：测试单个函数的逻辑，使用 mock 隔离外部依赖（当前覆盖率 57%）
- ✅ **集成测试**：测试真实的 API 调用和完整的业务流程，使用真实的飞书测试环境

---

## 🚀 快速开始

### 步骤 1: 创建测试表格

1. 访问 https://feishu.cn
2. 创建新的电子表格，命名为"FastFeishu 集成测试"
3. 设置基本表头（如：CaseID、query、result 等）
4. 复制表格 URL

### 步骤 2: 配置环境变量

```bash
# 方式1: 复制 .env.example 并填入实际值（推荐）
cp .env.example .env

# 编辑 .env 文件
vi .env
```

在 `.env` 文件中填入：

```bash
# 飞书应用凭证（必需）
FS_APP_ID=cli_xxx
FS_APP_SECRET=xxx

# 主测试表格（必需，用于大部分测试）
FS_TEST_MAIN_URL=https://li.feishu.cn/sheets/YOUR_SHEET_TOKEN?sheet=YOUR_SHEET_ID

# 其他测试表格（可选）
FS_TEST_BATCH_OPERATIONS_URL=https://li.feishu.cn/sheets/...
FS_TEST_LARGE_DATASET_URL=https://li.feishu.cn/sheets/...
FS_TEST_READONLY_URL=https://li.feishu.cn/sheets/...
```

**方式2: 直接设置环境变量**

```bash
export FS_APP_ID="cli_xxx"
export FS_APP_SECRET="xxx"
export FS_TEST_MAIN_URL="https://li.feishu.cn/sheets/YOUR_SHEET_TOKEN?sheet=YOUR_SHEET_ID"
```

### 步骤 3: 查看配置状态

```bash
# 运行配置检查脚本
python tests/integration/config.py
```

输出示例：
```
============================================================
可用的测试表格：
============================================================

main - ✅ 已配置
  描述: 主要测试表格，用于大部分读写测试
  环境变量: FS_TEST_MAIN_URL
  URL: https://li.feishu.cn/sheets...

batch_operations - ❌ 未配置
  描述: 批量操作测试表格，用于测试批量写入、批量读取等
  环境变量: FS_TEST_BATCH_OPERATIONS_URL
```

### 步骤 4: 运行集成测试

```bash
# 运行所有集成测试
pytest tests/integration -v -m integration

# 运行单个测试文件
pytest tests/integration/test_iterrows_columns.py -v

# 运行单个测试类
pytest tests/integration/test_iterrows_columns.py::TestIterrowsColumns -v

# 跳过慢速测试
pytest tests/integration -v -m "integration and not slow"
```

---

## 📋 测试表格配置管理

### 配置架构

项目使用统一的配置管理系统：

```
.env                           # 环境变量配置（本地，不提交到 git）
.env.example                   # 配置模板（提交到 git）
tests/integration/config.py    # 配置管理模块
tests/conftest.py              # Pytest fixtures
```

### 可用的测试表格类型

| 表格名称 | 环境变量 | 用途 |
|---------|---------|------|
| `main` | `FS_TEST_MAIN_URL` | 主要测试表格，用于大部分读写测试 |
| `batch_operations` | `FS_TEST_BATCH_OPERATIONS_URL` | 批量操作测试 |
| `large_dataset` | `FS_TEST_LARGE_DATASET_URL` | 大数据集测试（建议1000+行） |
| `readonly` | `FS_TEST_READONLY_URL` | 只读模式测试 |

### 在测试中使用配置

#### 方式1: 直接使用（推荐）

大部分测试应该直接从 config 获取 URL：

```python
import pytest
from fastfeishu.core import FeiShuSheet
from tests.integration.config import get_test_sheet_url


@pytest.mark.integration
class TestMyFeature:
    """我的功能测试"""

    def test_read_data(self):
        """直接获取 URL 并创建 sheet 对象"""
        url = get_test_sheet_url("main")
        sheet = FeiShuSheet(url, readonly=True)

        result = sheet.read('A1:A10')
        assert len(result) > 0

    def test_batch_operations(self):
        """使用不同的测试表格"""
        url = get_test_sheet_url("batch_operations")
        sheet = FeiShuSheet(url)
        # 执行批量操作测试...
```

#### 方式2: 使用 clean_sheet fixture（需要自动清理时）

只有需要自动清理数据的测试才使用 fixture：

```python
@pytest.mark.integration
def test_write_data(clean_sheet):
    """clean_sheet 会在测试前后自动清理数据"""
    clean_sheet.write_row([{"name": "test"}], write_row=2)
    result = clean_sheet.read('A2:A2')
    assert result[0][0] == "test"
    # 测试后自动清理
```

### 可用的 Fixtures

| Fixture 名称 | 类型 | 说明 |
|-------------|------|------|
| `clean_sheet` | `FeiShuSheet` | 自动清理数据的测试表格（测试前后自动清空） |

**注意：** 大部分测试应该直接使用 `get_test_sheet_url("main")`，只有需要自动清理时才使用 `clean_sheet` fixture。

---

## 🎯 需要集成测试的功能

### 1. 写入操作（高优先级 🔥）

这些方法在真实环境中的行为很复杂，需要集成测试验证：

| 方法 | 为什么需要集成测试 | 测试重点 |
|------|-------------------|---------|
| `write_column` | 需要验证真实的列追加和覆盖行为 | 新列创建、已有列覆盖、数据对齐 |
| `append_to_column` | 需要真实查找空白行并追加 | 空白行检测、追加位置、None处理 |
| `write_row` | `skip_none` + 分区算法需要真实验证 | None跳过、批量写入、性能 |
| `write_row_by_hang_header` | 悬挂表头 + 复杂范围解析 | 范围解析、数据对齐、批量写入 |
| `replace_placeholder` | 占位符替换的真实效果 | 纯占位符、混合文本、批量替换 |

### 2. 读取操作（中优先级 ⭐）

| 方法 | 为什么需要集成测试 | 测试重点 |
|------|-------------------|---------|
| `iterrows` | 流式读取大数据集的性能和正确性 | 分批读取、内存控制、dict/list模式 |
| `read_column` | 真实读取整列数据 | 数据完整性、格式化选项 |
| `read_human` vs `read_raw` | 不同渲染选项的真实效果 | 链接、公式、格式化文本 |

### 3. 删除操作（中优先级 ⭐）

| 方法 | 为什么需要集成测试 | 测试重点 |
|------|-------------------|---------|
| `delete_columns_by_name` | 真实删除列的副作用 | 数据移位、表头更新 |
| `delete_series_by_index` | 批量删除的效果 | 范围删除、数据完整性 |

### 4. 批量操作（高优先级 🔥）

| 方法 | 为什么需要集成测试 | 测试重点 |
|------|-------------------|---------|
| `write_batch` | 批量写入性能和API限制 | 并发写入、10MB限制、错误恢复 |
| 批量图片下载 | 异步并发、QPS控制 | 并发数、超时、失败重试 |

### 5. 端到端场景（高优先级 🔥）

| 场景 | 测试目的 |
|------|---------|
| 读取 → 处理 → 写入 | 验证完整数据流 |
| 大数据集处理 | 性能和内存测试 |
| 错误恢复 | 网络异常、重试逻辑 |
| 并发操作 | 多线程安全性 |

---

## 📝 如何编写集成测试

### 准备工作

#### 1. 创建测试环境

```bash
# 1. 在飞书中创建测试文档
# 访问 https://feishu.cn 创建一个专门用于测试的电子表格

# 2. 获取测试凭证
# 在飞书开放平台获取测试应用的 APP_ID 和 APP_SECRET

# 3. 设置环境变量
export FS_APP_ID="your_test_app_id"
export FS_APP_SECRET="your_test_app_secret"
export FS_TEST_SHEET_URL="https://example.feishu.cn/sheets/shtcn***"
```

#### 2. 配置 pytest

在 `pytest.ini` 中已经配置了集成测试标记：

```ini
[pytest]
markers =
    integration: 集成测试（需要真实API）
    slow: 慢速测试（超过10秒）
```

运行集成测试：

```bash
# 运行所有集成测试
PYTHONPATH=. pytest tests/integration -v -m integration

# 运行特定文件
pytest tests/integration/test_write_operations.py -v

# 跳过慢速测试
pytest tests/integration -v -m "integration and not slow"
```

---

## 🔨 集成测试示例

### 示例 1: 写入和读取操作

创建文件：`tests/integration/test_write_operations.py`

```python
"""
测试真实的写入操作
"""

import pytest
import os
from fastfeishu import FeiShuSheet


@pytest.fixture
def test_sheet_url():
    """测试表格 URL"""
    url = os.getenv("FS_TEST_SHEET_URL")
    if not url:
        pytest.skip("需要设置 FS_TEST_SHEET_URL 环境变量")
    return url


@pytest.fixture
def clean_sheet(test_sheet_url):
    """清理测试表格（每个测试前后）"""
    sheet = FeiShuSheet(test_sheet_url)

    # 清空表格（保留表头）
    info = sheet.get_sheet_info()
    if info["rowCount"] > 1:
        sheet.delete_series(2, info["rowCount"], "ROWS")

    yield sheet

    # 测试后清理（可选）
    # 如果需要保留测试数据用于调试，注释掉清理代码


@pytest.mark.integration
class TestWriteColumn:
    """write_column 方法的集成测试"""

    def test_write_to_existing_column(self, clean_sheet):
        """测试写入已存在的列"""
        # 假设第一列是 "姓名"
        data = ["张三", "李四", "王五"]

        clean_sheet.write_column("姓名", data, start_row=2)

        # 验证写入结果
        result = clean_sheet.read_column("姓名")
        assert result[:3] == data

    def test_write_to_new_column(self, clean_sheet):
        """测试写入新列（不存在的列）"""
        data = ["数据1", "数据2"]

        clean_sheet.write_column("新列", data, start_row=2)

        # 验证列被创建
        assert "新列" in clean_sheet.get_header()

        # 验证数据
        result = clean_sheet.read_column("新列")
        assert result[:2] == data


@pytest.mark.integration
class TestAppendToColumn:
    """append_to_column 方法的集成测试"""

    def test_append_to_empty_column(self, clean_sheet):
        """测试向空列追加数据"""
        # 先写入一些数据
        clean_sheet.write_column("姓名", ["张三"], start_row=2)

        # 追加数据
        clean_sheet.append_to_column("姓名", ["李四", "王五"])

        # 验证数据连续
        result = clean_sheet.read_column("姓名")
        assert result[:3] == ["张三", "李四", "王五"]

    def test_append_with_gaps(self, clean_sheet):
        """测试向有空白的列追加数据"""
        # 写入数据，留空白
        clean_sheet.write_column("姓名", ["A", "B"], start_row=2)

        # 追加应该从最后有数据的行开始
        clean_sheet.append_to_column("姓名", ["C"])

        result = clean_sheet.read_column("姓名")
        assert "C" in result
```

### 示例 2: 批量写入和性能测试

创建文件：`tests/integration/test_batch_operations.py`

```python
"""
测试批量操作和性能
"""

import pytest
import time
from fastfeishu import FeiShuSheet


@pytest.mark.integration
@pytest.mark.slow
class TestBatchWrite:
    """批量写入性能测试"""

    def test_write_large_dataset(self, clean_sheet):
        """测试写入大量数据（1000行）"""
        # 生成测试数据
        data = [
            {"姓名": f"用户{i}", "年龄": 20 + i % 50}
            for i in range(1000)
        ]

        start_time = time.time()
        clean_sheet.write_row(data, write_row=2)
        elapsed = time.time() - start_time

        # 验证写入成功
        info = clean_sheet.get_sheet_info()
        assert info["rowCount"] >= 1001  # 表头 + 1000行

        # 性能要求：1000行应该在30秒内完成
        assert elapsed < 30, f"写入1000行耗时 {elapsed:.2f}秒，超过30秒"

    def test_write_with_skip_none(self, clean_sheet):
        """测试 skip_none 参数的真实效果"""
        # 先写入一些基础数据
        clean_sheet.write_row([
            {"姓名": "张三", "年龄": 25, "部门": "技术部"}
        ], write_row=2)

        # 使用 skip_none 部分更新（不覆盖 None）
        clean_sheet.write_row([
            {"姓名": "张三", "年龄": None, "部门": "市场部"}
        ], write_row=2, skip_none=True)

        # 验证：年龄应该保持 25（未被 None 覆盖）
        result = clean_sheet.read_human("A2:C2")
        assert result[0][1] == 25  # 年龄未改变
        assert result[0][2] == "市场部"  # 部门已更新
```

### 示例 3: 流式读取测试

创建文件：`tests/integration/test_read_operations.py`

```python
"""
测试读取操作
"""

import pytest
from fastfeishu import FeiShuSheet


@pytest.mark.integration
class TestIterrows:
    """iterrows 流式读取测试"""

    def test_iterrows_large_dataset(self, clean_sheet):
        """测试流式读取大数据集"""
        # 先写入500行数据
        data = [{"姓名": f"用户{i}"} for i in range(500)]
        clean_sheet.write_row(data, write_row=2)

        # 使用 iterrows 读取
        count = 0
        for index, row in clean_sheet.iterrows(start_row=2):
            assert "姓名" in row
            count += 1
            if count >= 500:
                break

        assert count == 500

    def test_iterrows_dict_vs_list(self, clean_sheet):
        """测试不同的返回类型"""
        # 写入测试数据
        clean_sheet.write_row([
            {"姓名": "张三", "年龄": 25}
        ], write_row=2)

        # dict 模式
        for index, row in clean_sheet.iterrows(start_row=2, return_type=dict):
            assert isinstance(row, dict)
            assert "姓名" in row
            break

        # list 模式
        for index, row in clean_sheet.iterrows(start_row=2, return_type=list):
            assert isinstance(row, list)
            assert len(row) > 0
            break
```

### 示例 4: 占位符替换测试

创建文件：`tests/integration/test_placeholder.py`

```python
"""
测试占位符替换功能
"""

import pytest
from fastfeishu import FeiShuSheet
from fastfeishu.utils.feishu_util import FeiShuUtil


@pytest.mark.integration
class TestReplacePlaceholder:
    """replace_placeholder 方法的集成测试"""

    def test_replace_pure_placeholder(self, clean_sheet):
        """测试纯占位符替换（保持数据类型）"""
        # 写入占位符
        clean_sheet.write("A1:B1", [["{name}", "{age}"]])

        # 替换
        FeiShuUtil.replace_placeholder(clean_sheet, "A1:B1", name="Alice", age=30)

        # 验证（使用 UnformattedValue 读取原始类型）
        result = clean_sheet.read("A1:B1", value_render_option="UnformattedValue")
        assert result[0][0] == "Alice"
        assert result[0][1] == 30  # 应该是数字类型

    def test_replace_mixed_text(self, clean_sheet):
        """测试混合文本中的占位符"""
        # 写入混合文本
        clean_sheet.write("A1:A1", [["Hello {name}, you are {age} years old"]])

        # 替换
        FeiShuUtil.replace_placeholder(clean_sheet, "A1:A1", name="Bob", age=25)

        # 验证
        result = clean_sheet.read_human("A1:A1")
        assert result[0][0] == "Hello Bob, you are 25 years old"
```

### 示例 5: 端到端场景测试

创建文件：`tests/integration/test_end_to_end.py`

```python
"""
测试完整的业务场景
"""

import pytest
from fastfeishu import FeiShuSheet


@pytest.mark.integration
class TestEndToEndScenarios:
    """端到端场景测试"""

    def test_data_pipeline(self, clean_sheet):
        """测试完整的数据处理流程"""
        # 1. 写入原始数据
        raw_data = [
            {"姓名": "张三", "年龄": 25, "部门": "技术部"},
            {"姓名": "李四", "年龄": 30, "部门": "市场部"},
            {"姓名": "王五", "年龄": 28, "部门": "技术部"}
        ]
        clean_sheet.write_row(raw_data, write_row=2)

        # 2. 读取并处理数据
        processed_data = []
        for index, row in clean_sheet.iterrows(start_row=2):
            # 业务逻辑：给技术部员工加薪
            if row["部门"] == "技术部":
                processed_data.append({
                    "姓名": row["姓名"],
                    "奖金": 1000
                })

        # 3. 写入处理结果到新列
        if processed_data:
            clean_sheet.write_column("奖金",
                [d["奖金"] for d in processed_data],
                start_row=2
            )

        # 4. 验证结果
        bonus_col = clean_sheet.read_column("奖金")
        assert bonus_col[0] == 1000  # 张三
        assert bonus_col[2] == 1000  # 王五
```

---

## 🎯 集成测试最佳实践

### 1. 数据隔离
```python
# ✅ 好：每个测试使用独立的表格或清理数据
@pytest.fixture
def clean_sheet():
    sheet = FeiShuSheet(TEST_URL)
    # 清理旧数据
    yield sheet
    # 清理测试数据

# ❌ 坏：多个测试共享数据，相互影响
```

### 2. 使用真实但安全的测试数据
```python
# ✅ 好：使用明显的测试数据
data = [{"姓名": "TEST_USER_001", "年龄": 99}]

# ❌ 坏：使用可能混淆的真实姓名
data = [{"姓名": "张三", "年龄": 25}]
```

### 3. 验证副作用
```python
# ✅ 好：验证操作的副作用
clean_sheet.delete_columns_by_name("临时列")
assert "临时列" not in clean_sheet.get_header()  # 验证列确实被删除

# ❌ 坏：只检查返回值
result = clean_sheet.delete_columns_by_name("临时列")
assert result == 1
```

### 4. 性能断言
```python
# ✅ 好：设置合理的性能预期
import time
start = time.time()
clean_sheet.write_row(large_data)
elapsed = time.time() - start
assert elapsed < 30  # 30秒内完成

# ❌ 坏：没有性能限制
clean_sheet.write_row(large_data)
```

### 5. 错误场景测试
```python
# ✅ 好：测试异常情况
with pytest.raises(FeiShuColumnNotExist):
    clean_sheet.delete_columns_by_name("不存在的列")
```

---

## 🚀 快速开始

### 步骤 1: 创建测试表格
1. 访问 https://feishu.cn
2. 创建新的电子表格，命名为"FastFeishu 集成测试"
3. 设置基本表头（姓名、年龄、部门等）
4. 复制表格 URL

### 步骤 2: 设置环境变量
```bash
# 在项目根目录创建 .env 文件（注意添加到 .gitignore）
cat > .env << 'EOF'
FS_APP_ID=cli_xxx
FS_APP_SECRET=xxx
FS_TEST_SHEET_URL=https://example.feishu.cn/sheets/shtcnxxx
EOF

# 加载环境变量
source .env
```

### 步骤 3: 运行测试
```bash
# 运行所有集成测试
pytest tests/integration -v -m integration

# 运行单个测试
pytest tests/integration/test_write_operations.py::TestWriteColumn::test_write_to_existing_column -v
```

---

## ⚠️ 注意事项

1. **不要使用生产环境**：集成测试应该使用专门的测试表格，避免污染生产数据
2. **控制测试频率**：注意飞书 API 的速率限制，避免频繁调用
3. **清理测试数据**：每次测试后清理数据，避免累积
4. **并行测试风险**：多个集成测试可能冲突，考虑使用不同的测试表格或串行执行
5. **CI/CD 配置**：在 CI 中跳过集成测试（除非有专门的测试环境）：
   ```bash
   # 在 CI 中只运行单元测试
   pytest tests/unit -v -m unit
   ```

---

## 📚 相关文档

- [测试指南](./TESTING.md) - 单元测试的编写规范
- [开发者贡献指南](./CONTRIBUTING.md) - 开发工作流和代码规范
- [项目架构指南](./CLAUDE.md) - 架构设计和开发模式

---

**记住**：集成测试是验证真实世界行为的最后防线，单元测试保证代码逻辑正确，集成测试保证系统整体工作！ 🎉
