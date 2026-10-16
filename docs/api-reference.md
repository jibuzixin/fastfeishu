# API 参考与异常处理

## FeiShuSheet 主要方法

**读取方法**:
- `read(sheet_range)` - 读取范围
- `read_raw(sheet_range)` - 读取原始数据（含公式）
- `read_human(sheet_range)` - 人类可读方式读取
- `read_images(sheet_range)` - 读取图片
- `read_column(column_name)` - 读取指定列（返回一维数组）
- `read_image_column(column_name, start_row=2, end_row=None)` - 读取图片列（返回二进制数据列表）
- `read_row(row_number, full_row=False, read_method=None)` - 读取指定行（返回字典）
- `read_rows(row_numbers, full_row=False, read_method=None)` - 批量读取指定多行的数据（返回字典）
- `read_batch(ranges)` - 批量读取多个范围
- `iterrows(start_row=2, end_row=None, batch_size=500, return_type=dict, columns=None, read_method=None)` - 流式迭代
- `get_title()` - 获取标题
- `get_header()` - 获取表头
- `get_sheet_info()` - 获取当前 Sheet 信息
- `get_sheets_info()` - 获取所有 Sheet 信息
- `get_workbook_title()` - 获取工作簿标题

**写入方法**:
- `write(sheet_range, data_list, skip_none=False, partition_strategy='auto')` - 写入范围
- `write_batch(value_ranges, skip_none=False, partition_strategy='auto')` - 批量写入多个范围
- `write_row(data, write_row=2, skip_none=True, partition_strategy='auto')` - 写入行
- `write_column(column_name, data_list, start_row=2, skip_none=False, partition_strategy='auto')` - 写入列
- `write_row_by_hang_header(hang_header_range, data, write_row=2, skip_none=True, partition_strategy='auto')` - 悬挂表头写入
- `append_to_column(column_name, data_list, skip_none=False, partition_strategy='auto')` - 追加写入列数据
- `write_image(cell, image, image_name="cell.png")` - 写入图片
- `append(sheet_range, data_list)` - 追加数据
- `insert(sheet_range, data_list)` - 插入数据（在指定位置上方插入新行）

**删除/插入方法**:
- `delete_series(start_index, end_index)` - 删除行列
- `delete_series_by_index(start_index, end_index)` - 按索引删除
- `delete_columns_by_name(start_col_name, end_col_name)` - 按列名删除
- `insert_column_to_right(column_letter, insert_number=1, inherit_style=True)` - 右侧插入列
- `insert_column_to_left(column_letter, insert_number=1, inherit_style=True)` - 左侧插入列
- `insert_series(start_index, end_index, major_dimension, inherit_style)` - 插入行列
- `append_series(add_count, major_dimension)` - 在末尾追加行列

**高级方法**:
- `get_index_by_col_name(col_name)` - 根据列名获取索引
- `get_letter_by_col_name(col_name)` - 根据列名获取字母
- `check_columns_exist(col_names)` - 检测列是否存在（返回字典）
- `has_columns(col_names)` - 检测所有列是否都存在（返回布尔值）

**图片方法**:
- `download_image_to_path(file_token, save_path)` - 下载到路径
- `download_image_bytes(file_token)` - 下载为字节
- `download_image_stream(file_token)` - 下载为流
- `download_image_base64(file_token, compress=None)` - 下载为Base64

**Sheet管理**:
- `create_sheet(title, index=0)` - 创建新Sheet
- `copy(title)` - 复制当前Sheet
- `update_sheet_properties(properties)` - 更新Sheet属性
- `set_style(sheet_range, style)` - 设置单个范围的样式
- `set_styles(data)` - 批量设置多个范围的样式

**鉴权**（通过 `s.raw_request` 访问）:
- `refresh_tenant_token()` - 手动重新获取 tenant_access_token（日常无需调用，token 失效会自动刷新重试）

**属性**:
- `header` - 表头列表
- `link` - 当前链接
- `sheet_token` - Sheet Token
- `sheet_id` - Sheet ID
- `raw_request` - 原始请求对象（FeiShuRequest）

---

## 异常处理

```python
from fastfeishu.exceptions import FeiShuException, FeiShuRequestException, FeiShuColumnNotExist

try:
    s = FeiShuSheet('飞书链接')
    # 操作代码
except FeiShuColumnNotExist as e:
    print(f"列不存在: {e}")
except FeiShuRequestException as e:
    print(f"请求异常: {e}")  # e.code 可拿到业务错误码（HTTP 错误但响应体非 JSON 时为 None）
except FeiShuException as e:
    print(f"飞书异常: {e}")
```

### tenant_access_token 自动刷新

`tenant_access_token` 有效期约 2 小时，过期后调用接口会返回 token 失效错误码。
fastfeishu 在 request 层统一处理：当响应命中以下飞书通用错误码时，**自动重新获取
token 并重试一次**（只重试一次，避免无限循环），对调用方完全透明：

| 错误码 | 含义 |
|--------|------|
| `99991663` | tenant_access_token 过期/无效（主码） |
| `99991665` | invalid tenant code |
| `4001` | Invalid token, please refresh |
| `20013` | tenant access token invalid |
| `20005` | invalid access_token |

如果你希望主动控制（例如长时间运行的任务前预刷新），可调用手动刷新方法：

```python
from fastfeishu.core import FeiShuSheet

s = FeiShuSheet('飞书链接')
s.raw_request.refresh_tenant_token()   # 手动重新获取 tenant_access_token
```

> 自动重试通过统一 HTTP 入口 `_do_request` 实现，所有读写/下载方法均受益；
> 二进制流式下载（图片、导出文件）在 token 失效时同样会刷新重试，且不会消耗响应流。
>
> **线程安全**：多线程共享同一个 `FeiShuSheet` 实例时，若并发命中 token 失效，
> 内部用锁 + 代际计数器去重，只刷新一次，其余线程直接复用新 token，避免重复刷新。

### 自定义触发刷新的错误码

触发自动刷新的错误码集合定义在 `fastfeishu.core.request.TENANT_TOKEN_EXPIRED_CODES`（默认为上表 5 个码）。
**无需改源码**，运行时重新赋值即可对后续所有请求立即生效（`_do_request` 每次都查模块全局对象）：

```python
import fastfeishu.core.request as ff_req

# 增加一个码（frozenset | 返回新集合）
ff_req.TENANT_TOKEN_EXPIRED_CODES = ff_req.TENANT_TOKEN_EXPIRED_CODES | {91402}

# 移除一个码
ff_req.TENANT_TOKEN_EXPIRED_CODES = ff_req.TENANT_TOKEN_EXPIRED_CODES - {4001}

# 完全自定义
ff_req.TENANT_TOKEN_EXPIRED_CODES = frozenset({99991663})
```

> 这段代码只需在创建 `FeiShuSheet` 之前执行一次即可，整个进程内的请求都会用新集合。
> `frozenset` 是不可变类型，必须整体重新赋值，不能 `.add()`。

---
