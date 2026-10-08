# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

fastfeishu is a Python package for interacting with Feishu (Lark) Sheets API v3. It provides a high-level interface for reading, writing, and managing spreadsheets with support for batch operations, image handling, and streaming reads.

**Tech Stack:** Python 3.11+, pydantic, pandas, aiohttp, requests, Pillow

**Package Name:** fastfeishu
**Current Version:** 0.1.0 (see `fastfeishu/__init__.py`)

## Development Setup

### Environment
- Python 3.11+ (3.11 recommended, 3.12 may have dependency conflicts)
- Uses standard PyPI by default (can configure internal PyPI if needed)

### Installation
```bash
# Create and activate virtual environment
conda create -n feishu python=3.11 -y
conda activate feishu

# Install in editable mode
cd fastfeishu
pip install -e .

# If using internal PyPI, add --index-url parameter:
# pip install -e . --index-url YOUR_INTERNAL_PYPI_URL
```

### Environment Variables
Create `.env` file in project root:
- `FS_APP_ID` - Feishu application ID
- `FS_APP_SECRET` - Feishu application secret
- `FEISHU_CONFIG` - Custom config file path (optional, defaults to `fastfeishu/configs/properties.yaml`)

### Running Tests
```bash
# Run all tests
pytest

# Run only unit tests (fast, no API credentials needed)
pytest -m unit

# Run only integration tests (requires .env API credentials)
pytest -m integration

# Run with coverage report
pytest --cov=fastfeishu --cov-report=html

# Run specific test file
pytest tests/unit/test_request.py

# Run specific test class or method
pytest tests/unit/test_request.py::TestFeiShuRequest
pytest tests/unit/test_request.py::TestFeiShuRequest::test_parse_feishu_url
```

**Note:** Integration tests require valid Feishu API credentials in `.env` file. Unit tests use mocks and run without network.

## Architecture

### Three-Layer Design Pattern

The codebase follows a strict three-layer architecture with clear separation of concerns:

```
User Code
    ↓
FeiShuSheet (fastfeishu/core/sheet.py)
    ↓ delegates to
FeiShuSheetOperations (fastfeishu/core/operations.py)
    ↓ calls
FeiShuRequest (fastfeishu/core/request.py)
    ↓ HTTP
Feishu API
```

**Layer 1: FeiShuSheet (High-Level Interface)**
- User-facing API with convenient methods
- Column name mapping (write by column name instead of cell ranges)
- Batch operations and streaming reads
- Image handling with multiple formats (path, bytes, stream, base64)
- Implements `FeiShuInterface` abstract base class

**Layer 2: FeiShuSheetOperations (Operations Layer)**
- Core business logic and validation
- Readonly mode enforcement via `FeishuVariable` descriptor
- Header caching for performance
- Cell range parsing and manipulation
- Smart grid partitioning for optimized batch writes

**Layer 3: FeiShuRequest (API Communication Layer)**
- HTTP communication with Feishu API
- Tenant token management and auto-refresh
- URL construction from YAML config
- Error handling and retry logic

**Layer 0: Helpers Module (Bottom Layer)**
- Pure utility functions with zero dependencies
- Can be safely imported by any layer
- Contains: `num_to_excel_col()`, `excel_col_to_num()`, `match_row_num_by_range()`, `base64_image()`, etc.

**Dependency Hierarchy** (bottom to top):

```
helpers.py (pure utility functions, zero dependencies)
    ↑
models/ (data models, can use helpers)
    ↑
core/ (business logic, can use models + helpers)
    ↑
utils/ (advanced tools, can use core + models + helpers)
```

### Key Classes

- `FeiShuSheet` (`fastfeishu/core/sheet.py`) - Main entry point, inherits from `FeiShuSheetOperations`
- `FeiShuSheetOperations` (`fastfeishu/core/operations.py`) - Core operations implementation
- `FeiShuRequest` (`fastfeishu/core/request.py`) - API communication layer
- `FeiShuInterface` (`fastfeishu/core/interface.py`) - Abstract base class defining the contract
- `FeiShuUtil` (`fastfeishu/utils/feishu_util.py`) - Utility class for batch processing across sheets
- `SheetProperties` (`fastfeishu/models/sheet_properties.py`) - Builder pattern for sheet configuration
- `CellStyle` (`fastfeishu/models/cell_style.py`) - Builder pattern for cell style configuration
- `Font` (`fastfeishu/models/cell_style.py`) - Builder pattern for font configuration

### Design Patterns

- **Builder Pattern:** `SheetProperties.Builder()`, `Protect.Builder()`, `CellStyle.Builder()`, `Font.Builder()` for fluent configuration
- **Descriptor Pattern:** `FeishuVariable` descriptor for readonly property validation and type checking
- **Protocol/ABC:** `FeiShuInterface` abstract base class enforces contract across implementations
- **Singleton Pattern:** Thread-safe `get_feishu_property()` for config management
- **Lazy Evaluation:** Header caching with `_header` attribute to minimize API calls
- **Strategy Pattern:** `partition_grid()` with 'horizontal', 'vertical', 'auto' strategies for smart batch writes

### Important Implementation Details

**Smart Grid Partitioning** (`fastfeishu/utils/partition_grid.py`):
- Used by `write_row()` when `skip_none=True`
- Splits sparse data grids into optimal rectangular regions to minimize API calls
- Strategies: 'horizontal' (row-first), 'vertical' (column-first), 'auto' (choose fewer rectangles)

**Column Name Mapping**:
- First row (row 1) is always treated as header
- Column names are cached on first access via `get_header()`
- Methods like `write_column()`, `write_row()` use header mapping internally

**Readonly Mode**:
- Set via `readonly=True` constructor parameter
- Enforced by `FeiShuVariable` descriptor on `spreadsheet_token`, `sheet_id`
- Prevents accidental writes to important sheets

## Configuration

**YAML Configuration** (`fastfeishu/configs/properties.yaml`):
- Defines all API endpoints with placeholders (`{SHEET_TOKEN}`, `{FILE_TOKEN}`)
- Supports environment variable substitution: `${VAR_NAME:-default_value}`
- Structure: `feishu.links.baseUrl` + `feishu.links.<target>.<operation>.url`

**Configuration Priority** (highest to lowest):
1. Constructor parameters (e.g., `FeiShuSheet(url, app_id='...')`)
2. Environment variables (`FS_APP_ID`, `FS_APP_SECRET`)
3. `.env` file in project root
4. YAML config file (`properties.yaml`)
5. Secrets file (if configured)

**Access Config**: Use `get_feishu_property()` from `fastfeishu/configs/settings.py` for thread-safe singleton access

## Key Features & Usage Patterns

### Basic Usage
```python
from fastfeishu.core import FeiShuSheet

# Read-only mode (recommended for data analysis)
s = FeiShuSheet('飞书链接', readonly=True)

# Read single cell or range
cell = s.read('M2:M2')
range_data = s.read('A2:C10')

# Stream large datasets efficiently
for row in s.iterrows(start_row=2, batch_size=500):
    print(row['CaseID'], row['query'])
    # Note: iterrows() accepts read_method parameter to customize read behavior
    # e.g., iterrows(read_method=s.read_raw) to read formulas
```

### Writing Data
```python
# Write by range
s.write('A2:B3', [[1, 2], [3, 4]])

# Write by column name (creates column if missing)
s.write_column("自动化", [1, 2, 3], start_row=2)

# Write rows using dict mapping (most convenient)
s.write_row([
    {'CaseID': 1, '意图类型': 'type1', '回复': 'content'},
    {'CaseID': 2, '意图类型': 'type2', '回复': 'content2'},
], write_row=4, skip_none=True)  # skip_none=True preserves existing data

# Advanced: write with custom header range
s.write_row_by_hang_header(
    hang_header_range='C22:JK22',  # Use any row as header
    data=[{'col1': 'val1', 'col2': 'val2'}],
    write_row=23,
    partition_strategy='auto'  # Optimize batch writes
)

# Batch write multiple ranges (performance optimization)
s.write_batch([
    {"range": "A2:B3", "values": [[1, 2], [3, 4]]},
    {"range": "D2:E3", "values": [[5, 6], [7, 8]]},
])
```

### Image Handling
```python
# Read image metadata
data = s.read_images('A2:A2')
file_token = data['fileToken']

# Download in various formats
s.download_image_to_path(file_token, 'output.png')
img_bytes = s.download_image_bytes(file_token)
base64_str = s.download_image_base64(file_token, compress=True)

# Write image (accepts path or bytes)
s.write_image('A2', 'path/to/image.png', 'filename.png')
s.write_image('A2', image_bytes, 'filename.png')
```

### Batch Processing with FeiShuUtil
```python
from fastfeishu.core import FeiShuSheet
from fastfeishu.utils import FeiShuUtil

# Copy data between sheets
FeiShuUtil.process_rows_to_new_sheet(source_sheet, target_sheet)

# Transform rows during copy
def transform_handler(row: pd.Series) -> List[Dict[str, Any]]:
    # Return list of dicts to write (can return multiple rows per input)
    if row['status'] == 'active':
        return [row.to_dict()]
    return []  # Skip inactive rows

FeiShuUtil.process_rows_to_new_sheet(
    source_sheet,
    target_sheet,
    row_handler=transform_handler,
    batch_write=2000
)

# Replace placeholders with type preservation
FeiShuUtil.replace_placeholder(
    sheet=s,
    sheet_range='A1:A5',
    name='张三',
    age=25,
    price=99.99
)
```

### Cell Types (Rich Content)
```python
from fastfeishu.models.type import TextLink, Email, Formula, RichText, DateValue, MentionUser

# Text link
s.write('a1', [[TextLink('https://example.com', '点击访问')]])

# Email
s.write('b1', [[Email('test@example.com')]])

# Formula
s.write('c1', [[Formula('=A1+B1')]])

# Date
s.write('d1', [[DateValue.today()]])

# Rich text with builder
rich = (RichText.builder()
        .add_plain("状态：")
        .add_bold("成功")
        .add_plain("，共")
        .add_colored("100", "#00cc00")
        .add_plain("条")
        .build())
s.write('e1', [[rich]])

# @ user
s.write('f1', [[MentionUser(user_info='user@example.com', text_type='email', notify=True)]])
```

### Batch Download Images (General Utility)
```python
from fastfeishu.utils.common import batch_download_images, sync_batch_download_images

# Async batch download
success_list, failed_list = await batch_download_images(
    urls=["https://example.com/1.jpg", "https://example.com/2.png"],
    qps=10,
    save_dir="./downloaded_images",
    return_type="both",
    failed_log_path="logs/failed.json",
    headers={"Referer": "https://example.com"}
)

# Sync wrapper for use in synchronous code
success_list, failed_list = sync_batch_download_images(
    urls=["https://example.com/1.jpg"],
    qps=5,
    save_dir="./images",
    return_type="binary"
)
```

### Sampling Utility
```python
from fastfeishu.utils.common import sample_from_array

labels = ['[安全]', '[涉政]', '[安全]', '[涉政]', '[其他]']

# Random sample 3 items
result = sample_from_array(labels, label_config=None, max_samples=3)

# Sample by label with specific counts
result = sample_from_array(labels, label_config={'[安全]': 2, '[涉政]': 1})

# Sample max 2 per unique label
result = sample_from_array(labels, label_config={}, max_samples=2)
```

## Core Modules

**Helpers Module:**
- `fastfeishu/helpers.py` - Pure utility functions with zero dependencies (bottom layer)

**Core Layer:**
- `fastfeishu/core/interface.py` - `FeiShuInterface` abstract base class with Protocol definitions
- `fastfeishu/core/operations.py` - `FeiShuSheetOperations` with validation, caching, range parsing
- `fastfeishu/core/request.py` - `FeiShuRequest` for HTTP communication and token management
- `fastfeishu/core/sheet.py` - `FeiShuSheet` high-level user-facing API

**Models:**
- `fastfeishu/models/sheet_properties.py` - `SheetProperties` and `Protect` with Builder pattern
- `fastfeishu/models/cell_style.py` - `CellStyle`, `Font`, and `StyleRangeData`
- `fastfeishu/models/type.py` - Special cell types (`TextLink`, `Email`, `Formula`, `RichText`, `MentionUser`, `MentionDoc`, `MultipleValue`, `DateValue`, etc.)
- `fastfeishu/models/feishu_var.py` - `FeishuVariable` descriptor for property validation
- `fastfeishu/models/feishu_cfg.py` - Configuration models
- `fastfeishu/models/export_task.py` - Export task models (`ExportTaskRequest`, `ExportTaskResult`, etc.)

**Utilities:**
- `fastfeishu/utils/feishu_util.py` - `FeiShuUtil` for batch cross-sheet operations
- `fastfeishu/utils/common.py` - High-level utilities including `batch_download_images()`, `sample_from_array()`, etc.
- `fastfeishu/utils/partition_grid.py` - Smart grid partitioning algorithm for optimized batch writes

**Configuration:**
- `fastfeishu/configs/settings.py` - Configuration loader with `get_feishu_property()` singleton
- `fastfeishu/configs/properties.yaml` - API endpoint definitions

**Exceptions:**
- `fastfeishu/exceptions/exception.py` - `FeiShuException`, `FeiShuRequestException`, `FeiShuColumnNotExist`, `FeiShuStyleException`, etc.

## Common Development Patterns

### Adding New Cell Types
1. Define new class in `fastfeishu/models/type.py` inheriting from `FeiShuCellType`
2. Implement `to_json()` method for serialization to Feishu API format
3. Register in `CellTypeConverter.auto_convert()` if applicable
4. Document usage in README.md

### Extending API Operations
1. Add endpoint to `fastfeishu/configs/properties.yaml`
2. Implement in `FeiShuRequest` if it's low-level HTTP
3. Add operation logic to `FeiShuSheetOperations`
4. Expose convenience method in `FeiShuSheet` if user-facing

### Working with Utility Functions
- **Pure utility functions** (no dependencies) → Add to `fastfeishu/helpers.py`
- **High-level utilities** (can depend on core/models) → Add to `fastfeishu/utils/`
- Always import from `helpers` when possible to avoid circular dependencies
- Example imports:
  ```python
  from fastfeishu.helpers import num_to_excel_col  # Pure utility
  from fastfeishu.utils import FeiShuUtil  # High-level utility
  ```

### Debugging API Calls
- Check `fastfeishu/configs/properties.yaml` for endpoint structure
- Token management happens in `FeiShuRequest.get_tenant_token()`
- Use `readonly=False` to enable write operations (default is writable)

## Git Commit Convention

This project follows the Conventional Commits format. All commit messages MUST include a type tag:

### Commit Format

```
[type] Brief description

Detailed description (optional)
```

### Commit Types

| Type | Description | Example |
|------|-------------|---------|
| `[feat]` | New feature | `[feat] 增加 CellStyle 单元格样式` |
| `[fix]` | Bug fix | `[fix] 修复写图片 bug，为 iterrows 方法增加读取方法引用` |
| `[perf]` | Performance optimization | `[perf] 优化 write_row 方法和 request.py 内部请求方法代码结构` |
| `[refactor]` | Code refactoring | `[refactor] 提取 helpers 模块消除循环依赖隐患` |
| `[docs]` | Documentation | `[docs] 更新 README.md 文档` |
| `[test]` | Tests | `[test] 增加单元测试覆盖率` |
| `[chore]` | Build/tools | `[chore] 更新依赖版本` |
| `[style]` | Code formatting | `[style] 统一代码缩进格式` |

### Commit Examples

```bash
git commit -m "[feat] 增加批量下载图片功能"
git commit -m "[fix] 修复列名映射在特殊字符下的异常"
git commit -m "[perf] 优化 write_row 使用网格分区减少API调用"
git commit -m "[refactor] 提取 helpers 模块到独立文件"
```

### Commit Best Practices

1. **Single Responsibility** - One commit does one thing
2. **Clear Description** - Be specific, avoid vague terms
3. **Atomic Commits** - Each commit should leave code in working state
4. **Timely Commits** - Commit after completing a feature, don't accumulate changes

### Pre-commit Checklist

```bash
# 1. Check changed files
git status

# 2. Review changes
git diff

# 3. Run tests
pytest

# 4. Commit with proper message
git add <files>
git commit -m "[feat] Your commit message"

# 5. Push to remote
git push origin dev
```

## Development Best Practices & Lessons Learned

> **文档维护原则**：不要一直增加文档，对经验进行浓缩，删除冗余内容，保持文档精简高效。

### Adding New Methods - Key Points

**Method Design:**
- Naming: `read_row` (singular), scope clear, limitations documented
- Parameters: Consistent defaults (`read_method=None` → `read_human`), type hints
- Return: Descriptive dict keys, use `cell_is_blank()` for empty checks, fallback to column letters

**Documentation Checklist:**
- All parameters: type, default, description (use table for 3+ params)
- Return value structure
- 3-5 usage examples: basic → full params → edge cases → performance tips
- Parameter interactions and API limits

**Testing & Updates:**
- Unit tests (basic + edge cases)
- Update README + API reference

### Optimizing Iterator Methods

**重构 iterrows 增加列选择功能的经验**：

**参数设计决策：**
- ✅ 使用 `columns` 替代 `header`：语义更清晰（选择列 vs 重命名列）
- ✅ 支持列名和列字母混用：`columns=['CaseID', 'A', 'query']`
- ✅ 不考虑向后兼容：直接移除低使用率参数（`header` 仅在文档示例中出现1次）

**性能优化策略（按列分布自动选择）：**
```python
# 策略1：所有列（columns=None）
range_str = f"A{row}:Z{row}"  # 单次读取

# 策略2：连续列（columns=['A', 'B', 'C']）
range_str = f"A{row}:C{row}"  # 单次读取

# 策略3：离散列（columns=['A', 'D', 'G']）
ranges = [f"A{row}:A{row}", f"D{row}:D{row}", f"G{row}:G{row}"]
batch_result = self.read_batch(ranges)  # 批量 API
```

**实现要点：**
1. 列解析支持两种格式：列名（通过 `get_index_by_col_name`）、列字母（通过 `excel_col_to_num`）
2. 判断连续性：`all(indices[i]+1 == indices[i+1] for i in range(len(indices)-1))`
3. read_batch 结果转换：`valueRanges` 数组按列拼接成行数据
4. 表头自动映射：根据 `columns` 从 `full_header` 中提取对应列名

**文档重点：**
- 参数表格必须包含 `columns` 参数说明
- 示例展示列选择的性能优势（如：50列表格只读3列，减少94%数据传输）
- 说明自动优化策略（连续 vs 离散）

### Common Pitfalls

```python
# ✅ Good: Use helper to check empty values
from fastfeishu.helpers import cell_is_blank

if not cell_is_blank(header_value):
    result[header_value] = value
else:
    result[num_to_excel_col(i + 1)] = value

# ❌ Bad: Direct checks miss edge cases
if header_value is not None and header_value != '':
    result[header_value] = value  # Misses NaN, whitespace
```

**Key Rules:**
1. Respect layer architecture: helpers → models → core → utils
2. Cache method results, avoid repeated calls
3. Follow existing patterns before creating new ones
4. README updates are mandatory, not optional

### Integration Test Configuration Management

**统一管理集成测试表格链接的完整方案**：

**架构设计：**
```
.env                         # 本地配置（不提交 git）
.env.example                 # 配置模板（提交 git）
tests/integration/config.py  # 配置管理模块
tests/conftest.py            # Pytest fixtures
```

**核心原则：**
1. **集中管理**：所有测试表格链接在 `config.py` 中统一管理
2. **环境变量优先**：支持从 `.env` 文件或环境变量读取配置
3. **类型化配置**：使用 `@dataclass` 定义 `TestSheet` 类型
4. **自动跳过**：未配置的测试自动跳过（`pytest.skip`）
5. **多表格支持**：支持多个不同用途的测试表格（main, batch, large_dataset, readonly）

**配置管理模块实现要点：**
```python
# config.py
@dataclass
class TestSheet:
    name: str
    url: str
    description: str

class IntegrationTestConfig:
    DEFAULT_SHEETS = {"main": TestSheet(...), "batch": TestSheet(...)}

    @classmethod
    def get_sheet_url(cls, sheet_name: str) -> str:
        # 优先级：环境变量 > 默认配置
        env_key = f"FS_TEST_{sheet_name.upper()}_URL"
        return os.getenv(env_key) or cls.DEFAULT_SHEETS[sheet_name].url
```

**Fixtures 设计（简化后）：**
```python
# conftest.py - 只保留必要的 fixture
@pytest.fixture
def clean_sheet():
    """自动清理数据的测试表格（只在需要清理时用）"""
    from tests.integration.config import get_test_sheet_url

    url = get_test_sheet_url("main")
    sheet = FeiShuSheet(url)
    # 测试前清理
    yield sheet
    # 测试后清理
```

**测试编写模式（推荐）：**
```python
# ✅ 推荐：大部分测试直接获取 URL
from tests.integration.config import get_test_sheet_url

@pytest.mark.integration
class TestMyFeature:
    def test_basic(self):
        url = get_test_sheet_url("main")
        sheet = FeiShuSheet(url, readonly=True)
        result = sheet.read('A1:A10')
        assert len(result) > 0

    # 只有需要清理时才用 fixture
    def test_write(self, clean_sheet):
        clean_sheet.write_row([{"name": "test"}], write_row=2)
```

**优势：**
- ✅ 新增测试表格只需在 `config.py` 中添加一项配置
- ✅ 未配置的测试自动跳过，不会报错
- ✅ 支持查看配置状态（`python tests/integration/config.py`）
- ✅ 环境变量覆盖方便 CI/CD 集成

### Batch API Implementation Pattern

**Type System:**
- TypedDict in relevant model files (e.g., `StyleRangeData` in `cell_style.py`)
- Forward reference in interfaces: `def set_styles(self, data: List['StyleRangeData'])`
- Imports at file top, never inside functions
- Precise type hints: `List[StyleRangeData]` over `List[Dict[str, Any]]`

**Adding API Endpoint (3 places):**
1. `properties.yaml`: Add endpoint URL
2. `feishu_cfg.py`: Add field to Settings class
3. `request.py`: Implement request method

**Layer Responsibilities:**
- **Request**: HTTP, token, add sheet_id prefix
- **Operations**: Validation, type conversion, call `_response_json()`
- **Sheet**: User-friendly interface (if needed)

**Validation:**
- Validate all data before API call
- Check boundaries (rows/cols limits, total cells)
- Use helpers: `match_row_num_by_range()`, `excel_col_to_num()`
- Custom exceptions with clear error messages and suggested fixes
