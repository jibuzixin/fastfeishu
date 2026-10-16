# 项目架构

fastfeishu 采用严格的**四层分层架构**，层与层之间只能自下而上依赖，杜绝循环引用。

```
用户代码
   ↓
fastfeishu/core/sheet.py        FeiShuSheet（高层用户接口）
   ↓
fastfeishu/core/operations.py   FeiShuSheetOperations（业务逻辑与校验）
   ↓
fastfeishu/core/request.py      FeiShuRequest（HTTP / token / 端点）
   ↓
飞书开放平台 API
```

底层支撑：

```
fastfeishu/helpers.py           纯工具函数（零依赖）
   ↑
fastfeishu/models/              数据模型（CellStyle / type / SheetProperties）
   ↑
fastfeishu/core/                核心实现
   ↑
fastfeishu/utils/               高级工具（FeiShuUtil / common / export_util）
```

**硬性规则**：`helpers.py` 不导入任何项目内模块；低层不导入高层。

## 模块职责

| 模块 | 职责 |
| --- | --- |
| `helpers.py` | 行列号互转、范围解析、空值判断、Base64 图片转换。**零依赖** |
| `core/interface.py` | `FeiShuInterface` 抽象基类，约束必须实现的契约 |
| `core/operations.py` | 参数校验、只读拦截、表头缓存、样式与分区写入实现 |
| `core/request.py` | HTTP 请求、tenant_access_token 缓存与并发安全刷新、错误码检查、YAML 端点拼接 |
| `core/sheet.py` | 列名映射、按行/按列读写、批量与流式读取等用户友好接口 |
| `models/type.py` | 单元格类型体系：`PlainText` / `Number` / `DateValue` / `TextLink` / `Email` / `Formula` / `RichText` / `MentionUser` / `MultipleValue` 等，以及 `StyleDirector` 预设样式与 `CellTypeConverter` 自动类型转换 |
| `models/cell_style.py` | `CellStyle`、`Font`、`StyleRangeData`（Builder 模式） |
| `models/sheet_properties.py` | `SheetProperties`、`Protect`（Builder 模式） |
| `models/feishu_var.py` | `FeishuVariable` 描述符：属性类型校验与只读保护 |
| `models/export_task.py` | 导出任务请求/结果数据模型 |
| `utils/feishu_util.py` | `FeiShuUtil`：跨 Sheet 批量搬运、`replace_placeholder` 类型保持替换 |
| `utils/partition_grid.py` | 稀疏网格智能分区（`horizontal` / `vertical` / `auto`） |
| `utils/common.py` | `batch_download_images` / `sync_batch_download_images` / `sample_from_array` |
| `utils/export_util.py` | 文档导出任务封装（`FeiShuExportUtil`、`export_document`） |
| `configs/settings.py` | 配置加载单例 `get_feishu_property()` |
| `configs/properties.yaml` | 全部 API 端点与占位符模板 |

## 设计模式

- **Builder**：`SheetProperties.Builder()`、`CellStyle.Builder()`、`Font.Builder()`
- **Descriptor**：`FeishuVariable` 负责只读校验与类型检查
- **ABC / Protocol**：`FeiShuInterface` 约束实现
- **Singleton**：`get_feishu_property()` 线程安全配置单例
- **Lazy Evaluation**：`_header` 表头缓存，仅在首次访问时请求
- **Strategy**：`partition_grid(grid, strategy)` 三种分区策略

## 关键实现细节

1. **只读模式**：`FeiShuSheet(url, readonly=True)` 通过 `FeishuVariable` 描述符阻断 `spreadsheet_token` / `sheet_id` 的写入类操作。
2. **表头缓存**：第 1 行固定视为表头，`get_header()` 首次读取后缓存。
3. **智能分区**：`skip_none=True` 时把稀疏数据拆成最少矩形区域，减少 API 调用次数。
4. **token 自动刷新**：`request.py` 在识别到 token 失效错误码时加锁刷新并重放请求（并发安全），也可调用 `raw_request.refresh_tenant_token()` 手动刷新。
5. **依赖瘦身**：核心依赖仅 `requests / PyYAML / yarl / pydantic_settings / python-dotenv`；`Pillow`（`[image]`）与 `aiohttp`（`[download]`）为可选依赖。

## 相关文档

- [快速上手](getting-started.md)
- [基础操作](basic-operations.md)
- [单元格类型](cell-types.md)
- [API 参考与异常处理](api-reference.md)
- [开发者指南](development.md) / [开发者贡献指南](CONTRIBUTING.md)
