# 快速上手

## 安装

### 开发者安装（推荐）

如果你想参与开发或修改代码，使用一键安装脚本：

```bash
# 创建并激活虚拟环境
conda create -n feishu python=3.11 -y
conda activate feishu

# 进入项目目录并运行安装脚本
cd fastfeishu
./setup_dev.sh
```

**这会自动配置 Git hooks，确保代码质量！** 详细说明请参考 **[开发者贡献指南](CONTRIBUTING.md)**。

### 用户安装（仅使用）

如果你只是使用这个库，不需要修改代码：

```bash
# 创建并激活虚拟环境
conda create -n feishu python=3.11 -y
conda activate feishu

# 安装项目（核心依赖很轻量，约 4MB）
cd fastfeishu
pip install .
```

**可选功能**（按需安装，避免装入不需要的重依赖）：

```bash
pip install ".[image]"      # 需要图片压缩（Pillow）：download_image_base64(compress=...)
pip install ".[download]"   # 需要批量异步下载图片（aiohttp）：batch_download_images
pip install ".[image,download]"  # 一次装齐
```

> 核心安装只含 `requests / PyYAML / yarl / pydantic_settings / python-dotenv`，
> 不含 pandas/Pillow/aiohttp。调用未安装的可选功能时会给出友好的安装提示。

## 环境变量配置

在项目根目录创建 `.env` 文件：

```bash
# 飞书应用凭证
FS_APP_ID=''           # 飞书应用ID
FS_APP_SECRET=''       # 飞书应用密钥
```

## 目录结构

```
项目根目录
├── fastfeishu                      # 飞书在线文档操作接口
│   ├── __init__.py
│   ├── helpers.py                  # 纯工具函数（零依赖）
│   ├── configs/                    # 配置管理
│   ├── core/                       # 核心实现
│   │   ├── interface.py            # 抽象接口
│   │   ├── operations.py           # 操作层
│   │   ├── request.py              # API请求层
│   │   └── sheet.py                # 高层接口
│   ├── exceptions/                 # 异常类
│   ├── models/                     # 数据模型
│   │   ├── sheet_properties.py     # Sheet属性配置
│   │   ├── cell_style.py           # 单元格样式
│   │   ├── export_task.py          # 导出任务
│   │   └── type.py                 # 单元格类型
│   └── utils/                      # 高级工具
│       ├── common.py               # 批量下载等高级功能
│       ├── feishu_util.py          # FeiShuUtil 工具类
│       └── partition_grid.py       # 网格分区算法
├── requirements.txt                # 核心依赖列表（与 pyproject.toml 同步）
├── pyproject.toml                  # 项目元数据与依赖声明
└── README.md                       # 说明文档
```

**架构分层**（从底到高）：
- `helpers.py` - 底层纯函数（无任何依赖）
- `models/` - 数据模型层
- `core/` - 核心业务逻辑层
- `utils/` - 高级工具层（可依赖 core）

---
