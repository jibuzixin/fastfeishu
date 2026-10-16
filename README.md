<div align="center">

<img src="assets/logo.svg" alt="fastfeishu logo" width="96" height="96">

# fastfeishu

**飞书（Lark）Sheets API v3 的 Python 高级封装 —— 读、写、管电子表格，像操作 DataFrame 一样自然。**

[![Python](https://img.shields.io/badge/python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-00C853)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-在线阅读-2F6FEB)](https://jibuzixin.github.io/fastfeishu/)
[![Tests](https://img.shields.io/badge/tests-pytest-3776AB?logo=pytest&logoColor=white)](https://github.com/jibuzixin/fastfeishu/actions)

[快速开始](#-30-秒快速开始) · [文档](#-文档) · [架构](docs/ARCHITECTURE.md) · [贡献](docs/CONTRIBUTING.md) · [许可证](LICENSE)

</div>

---

## ✨ 特性

| 能力 | 说明 |
| --- | --- |
| 📖 列名映射 | 直接用列名读写，自动完成列号换算，列不存在自动创建 |
| ⚡ 批量与流式 | 批量范围读写、流式迭代整表、`iterrows(columns=...)` 按需取列 |
| 🧩 智能分区 | 稀疏数据自动拆分为最少矩形区域，显著减少 API 调用 |
| 🎨 单元格类型 | 富文本、链接、邮箱、公式、`@人`、`@文档`、下拉、日期、样式 |
| 🖼️ 图片处理 | 按路径 / 字节 / 流 / Base64 写入，四种方式下载 |
| 🧰 批处理工具 | 跨 Sheet 搬运、类型保持的占位符替换、异步批量下载、随机抽样 |
| 🔐 稳定鉴权 | `tenant_access_token` 缓存 + 并发安全自动刷新重试 |
| 🪶 依赖轻量 | 核心依赖约 4MB，Pillow / aiohttp 按需安装 |

## 🚀 30 秒快速开始

```bash
pip install fastfeishu
```

```python
from fastfeishu.core import FeiShuSheet

s = FeiShuSheet('https://xxx.feishu.cn/sheets/xxxx', readonly=True)

# 读取
print(s.read('A1:C10'))
for row in s.iterrows(start_row=2, columns=['CaseID', 'query']):
    print(row['CaseID'], row['query'])

# 写入（需 readonly=False）
s.write_row([{'CaseID': 1, 'query': '你好'}], write_row=2, skip_none=True)
```

配置凭证（项目根目录 `.env`）：

```bash
FS_APP_ID='cli_xxxxxxxx'
FS_APP_SECRET='xxxxxxxx'
```

> 完整安装选项、目录结构与进阶示例见 **[快速上手](docs/getting-started.md)**。

## 📖 文档

在线阅读：**<https://jibuzixin.github.io/fastfeishu/>**

### 使用

| 文档 | 内容 |
| --- | --- |
| [快速上手](docs/getting-started.md) | 安装、可选依赖、环境变量、目录结构 |
| [基础操作](docs/basic-operations.md) | 读取、写入、删除、行列追加、样式设置 |
| [单元格类型](docs/cell-types.md) | 富文本、链接、邮箱、公式、`@人`、日期、下拉 |
| [批量处理工具](docs/batch-utils.md) | `FeiShuUtil`、批量下载图片、随机抽样 |
| [Sheet 管理](docs/sheet-management.md) | 创建 / 复制 Sheet、属性与状态查询 |
| [API 参考与异常处理](docs/api-reference.md) | 全量方法速查、错误码与自定义刷新 |
| [文档导出](docs/EXPORT_GUIDE.md) | 异步导出任务与文件下载 |

### 开发

| 文档 | 内容 |
| --- | --- |
| [项目架构](docs/ARCHITECTURE.md) | 四层分层、设计模式、关键实现细节 |
| [开发者贡献指南](docs/CONTRIBUTING.md) | 一键装环境、工作流、提交规范、CI/Pages 流水线 |
| [测试指南](docs/TESTING.md) | 单元测试编写、Fixtures、覆盖率明细 |
| [集成测试指南](docs/INTEGRATION_TESTS.md) | 测试表格配置、跳过与清理策略 |

## 🛠️ 开发

```bash
conda create -n feishu python=3.11 -y && conda activate feishu
./setup_dev.sh      # 安装依赖 + 配置 Git hooks
pytest -m unit      # 单元测试（无需凭证）
```

## 📄 许可证

[MIT](LICENSE) © jibuzixin
