# 飞书云文档导出功能使用指南

本文档介绍如何使用 fastfeishu 导出云文档功能。

## 功能概述

fastfeishu 支持将以下飞书云文档导出为本地文件：

| 云文档类型 | 支持的导出格式 |
|-----------|--------------|
| 新版飞书文档 (docx) | docx (Word), pdf |
| 旧版飞书文档 (doc) | docx (Word), pdf |
| 飞书电子表格 (sheet) | xlsx (Excel), csv |
| 飞书多维表格 (bitable) | xlsx (Excel), csv |

## 环境准备

在使用导出功能前，需要设置以下环境变量：

```bash
export FS_APP_ID="your_app_id"
export FS_APP_SECRET="your_app_secret"
```

或在代码中使用 `.env` 文件。

## 使用方式

导出功能提供了两种使用方式：

### 方式一：一步到位（推荐）

使用便捷函数 `export_document`，自动完成创建任务、轮询状态、下载文件的全部流程。

#### 示例 1：导出为 PDF 并保存到本地

```python
from fastfeishu.utils.export_util import export_document

# 导出飞书文档为 PDF
file_path = export_document(
    token="doxcnxxxxxxxxxxxxxx",  # 文档 token
    doc_type="docx",               # 文档类型
    file_extension="pdf",          # 导出为 PDF
    save_path="./output/my_doc.pdf"  # 保存路径
)

print(f"文件已保存到: {file_path}")
```

#### 示例 2：导出为字节流

```python
from fastfeishu.utils.export_util import export_document

# 导出为字节流（不保存到本地）
content = export_document(
    token="doxcnxxxxxxxxxxxxxx",
    doc_type="docx",
    file_extension="pdf"
)

# 自行处理字节流
with open("custom_path.pdf", "wb") as f:
    f.write(content)

# 或者通过网络传输
# return Response(content, mimetype='application/pdf')
```

#### 示例 3：导出电子表格为 Excel

```python
from fastfeishu.utils.export_util import export_document

# 导出电子表格为 Excel
file_path = export_document(
    token="shtcnxxxxxxxxxxxxxx",  # 电子表格 token
    doc_type="sheet",
    file_extension="xlsx",
    save_path="./output/my_sheet.xlsx"
)
```

#### 示例 4：导出电子表格的某个工作表为 CSV

```python
from fastfeishu.utils.export_util import export_document

# 导出特定工作表为 CSV（需要提供 sub_id）
file_path = export_document(
    token="shtcnxxxxxxxxxxxxxx",
    doc_type="sheet",
    file_extension="csv",
    sub_id="abc123",  # 工作表 ID
    save_path="./output/my_sheet.csv"
)
```

### 方式二：分步调用（灵活控制）

如果需要更精细的控制，可以分步调用各个方法。

```python
from fastfeishu.utils.export_util import FeiShuExportUtil
from fastfeishu.models import ExportDocType, ExportFileExtension

# 1. 创建导出工具实例（自动认证）
util = FeiShuExportUtil.create_export_util_with_auth()

# 2. 创建导出任务
ticket = util.create_export_task_simple(
    token="doxcnxxxxxxxxxxxxxx",
    doc_type=ExportDocType.DOCX,
    file_extension=ExportFileExtension.PDF
)
print(f"导出任务已创建，ticket: {ticket}")

# 3. 轮询任务结果（自动等待完成）
result = util.poll_export_task_result(
    ticket=ticket,
    token="doxcnxxxxxxxxxxxxxx",
    max_retry=60,        # 最大重试次数
    retry_interval=2.0   # 重试间隔（秒）
)

print(f"任务状态: {result.job_status}")
print(f"文件名: {result.file_name}")
print(f"文件大小: {result.file_size} 字节")

# 4. 下载文件
if result.is_success:
    file_content = util.download_export_file_simple(result.file_token)

    # 保存到本地
    with open("output.pdf", "wb") as f:
        f.write(file_content)
    print("文件下载成功")
else:
    print(f"任务失败: {result.job_error_msg}")
```

### 方式三：使用底层 API（一般用不到）

前两种方式都由 `utils/export_util.py` 封装了认证、重试与轮询。**除非你需要自己控制完整请求过程**，否则不要直接用这一层：它要求你自备一个可用的 `FeiShuRequest`，并且返回的是原始 `Response`，没有错误码转换和重试。

```python
from fastfeishu.core.request import FeiShuRequest
from fastfeishu.models.export_task import ExportTaskResult
import time

# 初始化 request（需要一个有效的飞书链接用于认证）
request = FeiShuRequest("https://your-feishu-link")

```python
from fastfeishu.core.request import FeiShuRequest
from fastfeishu.models.export_task import ExportTaskResult
import time

# 初始化 request（需要一个有效的飞书链接用于认证）
request = FeiShuRequest("https://your-feishu-link")

# 1. 创建导出任务
response = request.create_export_task(
    token="doxcnxxxxxxxxxxxxxx",
    doc_type="docx",
    file_extension="pdf"
)
ticket = response.json()["data"]["ticket"]

# 2. 手动轮询任务状态
while True:
    response = request.get_export_task_result(
        ticket=ticket,
        token="doxcnxxxxxxxxxxxxxx"
    )
    result_data = response.json()["data"]["result"]
    result = ExportTaskResult(result_data)

    if result.is_success:
        print("任务完成")
        break
    elif result.is_failed:
        print(f"任务失败: {result.job_error_msg}")
        break

    print("任务处理中...")
    time.sleep(2)

# 3. 下载文件
response = request.download_export_file(result.file_token)
with open("output.pdf", "wb") as f:
    f.write(response.content)
```

## 如何获取文档 Token

文档 token 可以从飞书云文档的 URL 中获取：

### 飞书文档 URL 示例

- **新版文档**: `https://example.feishu.cn/docx/doxcnxxxxxxxxxxxxxx`
  - token: `doxcnxxxxxxxxxxxxxx`
  - type: `docx`

- **电子表格**: `https://example.feishu.cn/sheets/shtcnxxxxxxxxxxxxxx`
  - token: `shtcnxxxxxxxxxxxxxx`
  - type: `sheet`

- **多维表格**: `https://example.feishu.cn/base/bascnxxxxxxxxxxxxxx`
  - token: `bascnxxxxxxxxxxxxxx`
  - type: `bitable`

### 获取工作表 ID (sub_id)

导出电子表格或多维表格为 CSV 时，需要提供 sub_id：

```python
from fastfeishu.core.sheet import FeiShuSheet

# 对于电子表格
sheet = FeiShuSheet("https://your-sheet-link")
metadata = sheet.request.get_sheet_metadata()
sheet_id = metadata["data"]["sheets"][0]["sheetId"]  # 工作表 ID

# 对于多维表格
# 需要调用多维表格 API 获取 table_id
```

## 支持的文档类型和格式组合

| 文档类型 | 可导出的格式 | 说明 |
|---------|------------|------|
| docx (新版文档) | docx, pdf | 文档内资源总计不超过 1GB (Word) 或 128MB (PDF) |
| doc (旧版文档) | docx, pdf | 已不推荐使用 |
| sheet (电子表格) | xlsx, csv | 导出 CSV 需提供 sub_id |
| bitable (多维表格) | xlsx, csv | 导出 CSV 需提供 sub_id |

## 异常处理

```python
from fastfeishu.utils.export_util import export_document
from fastfeishu.exceptions.exception import (
    FeiShuExportException,
    FeiShuExportTaskFailedException,
    FeiShuExportTimeoutException
)

try:
    file_path = export_document(
        token="doxcnxxxxxxxxxxxxxx",
        doc_type="docx",
        file_extension="pdf",
        save_path="./output.pdf"
    )
    print(f"导出成功: {file_path}")

except FeiShuExportTaskFailedException as e:
    # 导出任务失败
    print(f"导出失败，状态码: {e.job_status}")
    print(f"错误信息: {e.error_msg}")

except FeiShuExportTimeoutException:
    # 导出任务超时
    print("导出任务超时，请稍后重试")

except FeiShuExportException as e:
    # 其他导出异常
    print(f"导出异常: {str(e)}")
```

## 注意事项

1. **及时下载**：导出的文件在任务结束后 10 分钟会被删除，请及时下载。

2. **权限要求**：
   - 需要开启权限：`导出云文档(docs:document:export)` 或 `导出云文档(drive:export:readonly)`
   - 使用 `tenant_access_token` 时，需要为应用添加文档权限
   - 使用 `user_access_token` 时，需要为用户添加文档权限

3. **文件大小限制**：
   - 导出为 Word 文档：文档内资源总计不超过 1 GB
   - 导出为 PDF：文档内资源总计不超过 128 MB
   - 接口返回数据最大限制：10 MB

4. **水印**：
   - 使用应用身份导出：水印为应用 ID（如 `cli_a2c2xxxxxxxxd01b`）
   - 使用用户身份导出：水印为用户标识

5. **频率限制**：
   - 接口调用频率限制：100 次/分钟

## 完整示例

```python
from fastfeishu.utils.export_util import export_document
from fastfeishu.models import ExportDocType, ExportFileExtension

# 示例：导出多个文档
documents = [
    {
        "token": "doxcnxxxxxx1",
        "doc_type": ExportDocType.DOCX,
        "file_extension": ExportFileExtension.PDF,
        "save_path": "./exports/doc1.pdf"
    },
    {
        "token": "shtcnxxxxxx2",
        "doc_type": ExportDocType.SHEET,
        "file_extension": ExportFileExtension.XLSX,
        "save_path": "./exports/sheet1.xlsx"
    }
]

for doc in documents:
    try:
        file_path = export_document(**doc)
        print(f"✓ 导出成功: {file_path}")
    except Exception as e:
        print(f"✗ 导出失败: {e}")
```

## API 参考

### `export_document()` 函数参数

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| token | str | 是 | 云文档 token |
| doc_type | str/ExportDocType | 是 | 文档类型 (doc/sheet/bitable/docx) |
| file_extension | str/ExportFileExtension | 是 | 导出格式 (docx/pdf/xlsx/csv) |
| save_path | str | 否 | 保存路径，不传则返回字节流 |
| sub_id | str | 否 | 子表 ID。导出 sheet 的 CSV、导出 bitable 时分别传 sheet_id / table_id，其他场景留空 |
| max_retry | int | 否 | 最大重试次数，默认 60 |
| retry_interval | float | 否 | 重试间隔秒数，默认 2.0 |

### 返回值

- 如果指定了 `save_path`：返回保存的文件路径（str）
- 如果未指定 `save_path`：返回文件字节流（bytes）

## 已有 FeiShuSheet 实例时复用认证

`FeiShuExportUtil` 接受一个已有的 `FeiShuRequest`，可以直接复用 `FeiShuSheet.raw_request`，避免重复获取 token：

```python
from fastfeishu.core import FeiShuSheet
from fastfeishu.utils.export_util import FeiShuExportUtil

s = FeiShuSheet("https://your-feishu-link")
exporter = FeiShuExportUtil(s.raw_request)
content = exporter.download_export_file_simple(file_token)
```

> `FeiShuExportUtil()` 不传参数时会自行建立认证；若传入非法对象，构造阶段会抛 `FeiShuExportException`。

## 更多信息

- [飞书开放平台 - 导出云文档概述](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/drive-v1/export_task/export-user-guide)
- [创建导出任务 API](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/drive-v1/export_task/create)
- [查询导出任务结果 API](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/drive-v1/export_task/get)
- [下载导出文件 API](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/drive-v1/export_task/download)
