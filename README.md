# 飞书 API 快速操作

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Test Coverage](https://img.shields.io/badge/coverage-61%25-yellowgreen)](docs/TESTING.md)

**fastfeishu** 是一个用于与飞书（Lark）Sheets API v3 交互的 Python 包，提供高级接口用于读取、写入和管理电子表格，支持批处理、图片处理和流式读取。

## 📚 文档导航

- **[开发者贡献指南](docs/CONTRIBUTING.md)** - 新人必读！一键配置开发环境，了解开发工作流和代码规范
- **[项目架构指南](docs/CLAUDE.md)** - 详细的架构设计、设计模式和开发模式
- **[测试指南](docs/TESTING.md)** - 单元测试编写指南和最佳实践
- **[集成测试指南](docs/INTEGRATION_TESTS.md)** - 集成测试编写指南和示例
- **[GitHub Actions](../../actions)** - 查看 CI/CD 状态

## 🚀 新人快速开始

如果你是第一次参与本项目开发，强烈建议使用一键安装脚本：

```bash
# 1. 克隆项目并创建虚拟环境
git clone <repo_url>
cd fastfeishu
conda create -n feishu python=3.11 -y
conda activate feishu

# 2. 运行一键安装脚本（自动完成所有配置）
./setup_dev.sh
```

脚本会自动完成：
- ✅ 检查 Python 环境
- ✅ 安装项目依赖和测试工具
- ✅ 配置 Git hooks（自动检查格式和运行测试）
- ✅ 单元测试不通过时自动阻止推送

完成后你只需关注：**写代码 → git commit → git push**

**详细说明请参考：[开发者贡献指南](docs/CONTRIBUTING.md)**

---

## 一、快速上手

### 1. 安装

#### 开发者安装（推荐）

如果你想参与开发或修改代码，使用一键安装脚本：

```bash
# 创建并激活虚拟环境
conda create -n feishu python=3.11 -y
conda activate feishu

# 进入项目目录并运行安装脚本
cd fastfeishu
./setup_dev.sh
```

**这会自动配置 Git hooks，确保代码质量！** 详细说明请参考 **[开发者贡献指南](docs/CONTRIBUTING.md)**。

#### 用户安装（仅使用）

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

### 2. 环境变量配置

在项目根目录创建 `.env` 文件：

```bash
# 飞书应用凭证
FS_APP_ID=''           # 飞书应用ID
FS_APP_SECRET=''       # 飞书应用密钥
```

### 3. 目录结构

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

## 二、基础操作

### 2.1 读取数据

#### 单元格读取、范围读取

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    # 只读模式
    s = FeiShuSheet('飞书链接', readonly=True)

    # 读取单个单元格
    h = s.read('M2:m2')
    print(h)

    # 读取范围
    h = s.read('a2:Ai33')
    print(h)
```

#### 获取Sheet标题

```python
s = FeiShuSheet('飞书链接', readonly=True)
print(s.get_title())  # 输出: Sheet名称
```

#### 读取原始数据（包含公式）

```python
s = FeiShuSheet('飞书链接', readonly=True)
# 读取原始数据，包括公式计算结果
raw_data = s.read_raw('a2:Ai33')
print(raw_data)
```

#### 人类可读方式读取

```python
s = FeiShuSheet('飞书链接', readonly=True)
# 按照人类阅读习惯读取
human_data = s.read_human('a2:Ai33')
print(human_data)
```

#### 读取指定列

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接', readonly=True)

    # 根据列名读取整列数据（从第2行开始）
    column_data = s.read_column('CaseID')
    print(column_data)  # [1, 2, 3, 4, ...]

    # 指定读取范围
    column_data = s.read_column('CaseID', start_row=3, end_row=100)
```

#### 读取指定行

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接', readonly=True)

    # 读取第2行（默认只读和表头等长的列）
    # 假设表头为 ["姓名", "年龄"]
    row_data = s.read_row(2)
    print(row_data)  # {"姓名": "张三", "年龄": 25}

    # 读取整行（包含表头范围外的列）
    # 超出表头的列使用列字母索引作为键
    row_data_full = s.read_row(2, full_row=True)
    print(row_data_full)  # {"姓名": "张三", "年龄": 25, "C": "备注", "D": "其他"}

    # 读取表头行（第1行）
    # 使用列字母索引作为键
    header_row = s.read_row(1)
    print(header_row)  # {"A": "姓名", "B": "年龄"}

    # 使用 read_raw 读取公式
    row_with_formula = s.read_row(3, read_method=s.read_raw)
    print(row_with_formula)  # {"姓名": "李四", "年龄": "=B2+1"}

    # 当表头某列为None或空字符串时，自动使用列字母索引
    # 假设表头为 ["姓名", None, "", "城市"]
    row_with_none_header = s.read_row(2)
    print(row_with_none_header)  # {"姓名": "张三", "B": 25, "C": "测试", "城市": "北京"}
```

#### 批量读取多行

使用 `read_rows` 方法可以一次性读取多个不连续的行，相比多次调用 `read_row` 性能更高（使用飞书批量读取 API）。

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接', readonly=True)

    # 批量读取第2、3、5行（默认只读和表头等长的列）
    # 假设表头为 ["姓名", "年龄", "城市"]
    rows_data = s.read_rows([2, 3, 5])
    print(rows_data)
    # [
    #     {"姓名": "张三", "年龄": 25, "城市": "北京"},
    #     {"姓名": "李四", "年龄": 30, "城市": "上海"},
    #     {"姓名": "王五", "年龄": 28, "城市": "广州"}
    # ]

    # 读取整行（包含表头范围外的列）
    rows_data_full = s.read_rows([2, 3], full_row=True)
    print(rows_data_full)
    # [
    #     {"姓名": "张三", "年龄": 25, "C": "备注1", "D": "其他1"},
    #     {"姓名": "李四", "年龄": 30, "C": "备注2", "D": "其他2"}
    # ]

    # 同时读取表头行和数据行
    rows_with_header = s.read_rows([1, 2, 3])
    # 第1行使用列字母索引，其他行使用表头名称

    # 使用 read_raw 读取公式
    rows_with_formula = s.read_rows([2, 3], read_method=s.read_raw)

    # 注意：该接口返回数据的最大限制为 10 MB
```

#### 批量读取多范围

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接', readonly=True)

    # 同时读取多个范围，性能更高
    result = s.read_batch(["A1:C3", "D5:E10"])
    # result["valueRanges"] 包含每个范围的读取结果
```

#### 遍历整张表（流式读取）

使用 `iterrows` 方法可以流式读取飞书表格，内存安全，适合处理大型数据集。

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接', readonly=True)

    # 基础用法：默认从第2行开始，每次读取500行，返回字典格式
    for index, row in s.iterrows():
        print(index, row['CaseID'], row['query'], row['预期APIINFO'])

    # 完整参数演示
    for index, row in s.iterrows(
        start_row=5,           # 起始行号（含），默认 2
        end_row=100,           # 结束行号（含），默认 None（读到最后）
        batch_size=1000,       # 每次读取行数，默认 500
        return_type=dict,      # 返回类型：dict 或 list，默认 dict
        columns=None,          # 指定读取的列，默认 None（所有列）
        read_method=s.read_human  # 读取方法引用，默认 read_human
    ):
        print(index, row)

    # 示例1：只读取指定列（节省带宽和内存）
    # 当表格列很多但只需要少数几列时，强烈推荐使用此功能
    for index, row in s.iterrows(columns=['CaseID', 'query']):
        print(index, row['CaseID'], row['query'])
        # 只传输这两列的数据，大幅减少网络流量和内存占用

    # 示例2：使用列字母索引
    for index, row in s.iterrows(columns=['A', 'B', 'D']):
        print(index, row)  # row 是 {'A': val1, 'B': val2, 'D': val3}

    # 示例3：从第1行开始（包含表头），使用列字母索引
    for index, row in s.iterrows(start_row=1, return_type=dict):
        # 当 start_row=1 且 return_type=dict 时，表头使用列字母索引 A, B, C...
        print(index, row['A'], row['B'])  # 第1行会返回 {"A": "姓名", "B": "年龄"}

    # 示例4：返回列表格式（不使用表头映射）
    for index, row in s.iterrows(return_type=list):
        print(index, row[0], row[1])  # 直接使用索引访问

    # 示例5：读取原始数据（公式、带文本链接等）
    for index, row in s.iterrows(read_method=s.read_raw):
        # read_raw 可以获取公式表达式、链接的原始数据
        print(index, row['公式列'])  # 会显示 "=A1+B1" 而不是计算结果

    # 示例6：处理大数据集（指定结束行，优化批次大小）
    for index, row in s.iterrows(
        start_row=2,
        end_row=10000,       # 只处理前1万行
        batch_size=2000,     # 增大批次可以减少API调用次数
        columns=['关键列1', '关键列2']  # 只读需要的列
    ):
        # 处理数据...
        pass
```

**参数说明**：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `start_row` | `int` | `2` | 数据起始行（含），默认跳过表头从第2行开始 |
| `end_row` | `Optional[int]` | `None` | 结束行（含），`None` 表示读到最后一行 |
| `batch_size` | `int` | `500` | 每次读取的行数，根据表格大小可适当调整（范围：100-2000） |
| `return_type` | `Type[Union[List, Dict]]` | `dict` | 返回类型：`dict` 使用列名访问，`list` 使用索引访问 |
| `columns` | `Optional[List[str]]` | `None` | 指定要读取的列（列名或列字母），`None` 表示读取所有列 |
| `read_method` | `Callable` | `None` | 读取方法引用（`read_human`/`read_raw`/`read`），`None` 默认为 `read_human` |

**返回值**：
- 生成器，每次迭代返回 `(行号, 行数据)` 元组
- `行号`：当前行在表格中的实际行号（从1开始）
- `行数据`：根据 `return_type` 返回 `dict` 或 `list`

**使用建议**：
- 处理小数据集（< 1000行）：`batch_size=500`（默认）
- 处理大数据集（> 10000行）：`batch_size=1000-2000`
- **列很多时使用 `columns` 参数**：只读取需要的列，可以大幅减少带宽和内存占用
  - 例如：表格有 50 列，只需要 3 列，使用 `columns` 可减少 94% 的数据传输
- 飞书 API 单次返回限制为 10MB，过大的 `batch_size` 可能触发限制
- 使用 `read_raw` 可以读取公式原始表达式，但解析速度较慢

**性能优化**：
- `columns` 参数会自动优化读取策略：
  - 连续列（如 `['A', 'B', 'C']`）：使用单次读取
  - 离散列（如 `['A', 'D', 'G']`）：使用批量 API 读取多个范围

#### 读取图片

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 获取图片信息
    data = s.read_images('a2:a2')
    file_token = data['fileToken']

    # 下载图片到本地
    s.download_image_to_path(file_token, 'tmp_image_1.png')

    # 下载图片为Base64编码
    base64 = s.download_image_base64(file_token, compress=True)  # compress=True 可压缩

    # 下载图片为二进制流
    img_bytes = s.download_image_bytes(file_token)

    # 下载图片为流
    img_stream = s.download_image_stream(file_token)
```

#### 读取图片列

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 根据列名读取整列图片（默认从第2行开始）
    # 返回二进制数据列表，如果单元格不包含图片则为 None
    image_list = s.read_image_column('图片列')

    # 指定读取范围（从第3行开始，到第10行结束）
    image_list = s.read_image_column('图片列', start_row=3, end_row=10)

    # 保存图片到本地
    for index, image_bytes in enumerate(image_list):
        if image_bytes is not None:
            with open(f'./image_{index}.png', 'wb') as f:
                f.write(image_bytes)
            print(f"图片 {index} 写入成功")
```

### 2.2 写入数据

#### 写入范围

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 写入单个单元格
    s.write('M2:m2', [['字符串、数字或可序列化对象']])

    # 写入范围
    s.write('a2:Ai33', [
        ['数据1', '数据2'],
        ['数据3', '数据4'],
        # ... 更多行
    ])
```

#### 批量写入多个范围

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 同时写入多个范围，性能更高
    s.write_batch([
        {"range": "A2:B3", "values": [[1, 2], [3, 4]]},
        {"range": "D2:E3", "values": [[5, 6], [7, 8]]},
    ])
```

#### 追加数据

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 在已有数据末尾追加数据
    s.append('A10:C15', [[1, 2, 3], [4, 5, 6]])
```

#### 插入数据

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 在指定位置上方插入新行并写入数据
    s.insert('A10:C10', [[1, 2, 3]])
```

#### 按列名写入（自动新增列）

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 写入单列数据
    s.write_column("自动化", [1, 2, 3, 4, 5, 6, 7, 8])

    # 从指定行开始写入
    s.write_column("自动化", [1, 2, 3, 4, 5, 6, 7, 8], start_row=4)
```

#### 按列名追加写入列数据（不会自动新建列）

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 追加写入单列数据
    # 假设原列数据是: [1, 4, 5, 6, None, yes, '', None, '', None, None]
    s.append_to_column("自动化", [1, 2, 3])
    # 写入后变为: [1, 4, 5, 6, None, yes, '', None, '', 1, 2, 3]
```

#### 按列名写入行（支持字典或二维数组）

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 使用字典写入（支持字典和列表混合）
    s.write_row([
        {'CaseID': 1, '意图类型': '这是什么', '端到端回复': '回复内容'},
        {'CaseID': 2, '意图类型': 'type', '端到端回复': '回复内容2'},
        [3, None, None, "这是什么东西"],  # 支持数组
    ], write_row=4)  # 从第4行开始写入

    # skip_none 参数：控制 None 值处理（默认 True）
    s.write_row([
        {'CaseID': 1, '意图类型': None, '端到端回复': '回复内容'},
        {'CaseID': 2, '意图类型': 'type', '端到端回复': None},
    ], write_row=4, skip_none=True)  # None 不会覆盖原有数据

    # skip_none=False：使用 None 覆盖单元格
    s.write_row([
        {'CaseID': 1, '意图类型': None, '端到端回复': '回复内容'},
    ], write_row=4, skip_none=False)  # None 会覆盖单元格为空

    # partition_strategy 参数：数据分区策略（性能优化，仅在 skip_none=True 时有效）
    # - 'auto'（默认）：自动选择最优策略
    # - 'horizontal'：横向分割
    # - 'vertical'：纵向分割
    s.write_row(data, write_row=4, skip_none=True, partition_strategy='horizontal')
```

#### 悬挂表头写入

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 使用自定义表头范围（可指定任意行作为表头）
    s.write_row_by_hang_header(
        hang_header_range='A1:D1',  # 表头范围
        data=[  # 数据（支持字典和列表混合）
            {'CaseID': 1, '意图类型': 'type', '端到端回复': '回复内容'},
            {'CaseID': 2, '意图类型': 'type', '端到端回复': '回复内容2'},
        ],
        write_row=2  # 数据从第2行开始（相对于表头行）
    )

    # skip_none 参数：控制 None 值处理（默认 True）
    s.write_row_by_hang_header(
        hang_header_range='A1:D1',
        data=[
            {'CaseID': 1, '意图类型': None, '端到端回复': '回复内容'},
        ],
        write_row=2,
        skip_none=True  # None 不会覆盖原有数据
    )

    # partition_strategy 参数：数据分区策略（仅在 skip_none=True 时有效）
    s.write_row_by_hang_header(
        hang_header_range='C22:JK22',  # 可以是任意行范围
        data=data,
        write_row=2,
        skip_none=True,
        partition_strategy='auto'  # 'auto'（默认）, 'horizontal', 'vertical'
    )
```

#### 写入图片

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 传入本地图片路径
    s.write_image('a2', '本地图片路径.png', '示例图.png')

    # 传入二进制流
    import io
    with open('本地图片路径.png', 'rb') as f:
        img_bytes = f.read()
    s.write_image('a2', img_bytes, '示例图.png')
```

### 2.3 删除数据

#### 删除行列

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 删除6-8列（包含6和8列）
    s.delete_series(6, 8, major_dimension="COLUMNS")

    # 删除6-8行（包含6和8行）
    s.delete_series(6, 8, major_dimension="ROW")

    # 删除"端到端回复"列
    s.delete_columns_by_name("端到端回复")

    # 删除"CaseID"到"端到端回复"之间的所有列
    s.delete_columns_by_name("CaseID", "端到端回复")

    # 使用数字索引删除1~3行，包含第3行（从1开始）
    s.delete_series_by_index(1, 3)

    # 使用字母索引删除 A~F 列，包含 F 列
    s.delete_series_by_index('A', 'F')
```

#### 插入列

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 在C列右边插入1个空列
    s.insert_column_to_right('C', insert_number=1)

    # 在B列左边插入2个空列
    s.insert_column_to_left('B', insert_number=2)

    # 在指定位置插入空列（继承样式）
    s.insert_column_to_right('D', insert_number=1, inherit_style=True)
```

### 2.4 行列追加

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 在工作表末尾追加5行
    total_rows = s.append_series(5, "ROWS")
    print(f"当前总行数: {total_rows}")

    # 在工作表末尾追加3列，返回新列的字母索引
    new_col_letter = s.append_series(3, "COLUMNS")
    print(f"新列字母索引: {new_col_letter}")
```

### 2.5 高级操作

#### 替换占位符（支持类型保持）

```python
from fastfeishu.core import FeiShuSheet
from fastfeishu.utils.feishu_util import FeiShuUtil

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 智能类型替换：
    # 1. 纯占位符（如 {price}）会保持原始类型
    # 2. 混合文本（如 "价格：{price}元"）会转为字符串

    # 示例：假设单元格内容为
    # A1: {name}              -> 纯占位符
    # A2: {age}               -> 纯占位符
    # A3: {price}             -> 纯占位符
    # A4: Hello {name}!       -> 混合文本
    # A5: 价格：{price}元     -> 混合文本

    FeiShuUtil.replace_placeholder(
        sheet=s,
        sheet_range='A1:A5',
        name='张三',
        age=25,           # 数字类型
        price=99.99       # 浮点数类型
    )

    # 替换后结果：
    # A1: 张三                 (字符串)
    # A2: 25                   (数字类型保持)
    # A3: 99.99                (浮点数类型保持)
    # A4: Hello 张三!          (字符串)
    # A5: 价格：99.99元        (字符串)
```

#### Sheet属性配置

```python
from fastfeishu.core import FeiShuSheet
from fastfeishu.models.sheet_properties import SheetProperties, Protect

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 配置单元格保护
    protect = Protect.builder() \
        .lock(True) \
        .lock_info('锁定信息') \
        .build()

    # 配置Sheet属性
    properties = SheetProperties.builder() \
        .title('新标题') \
        .index(0) \
        .hidden(False) \
        .frozen_col_count(3) \
        .frozen_row_count(2) \
        .protect(protect) \
        .build()

    s.update_sheet_properties(properties)
```

#### 设置单元格样式

```python
from fastfeishu.core import FeiShuSheet
from fastfeishu.models import CellStyle, Font

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 使用 Builder 模式创建样式（推荐）
    style = CellStyle.builder() \
        .font(Font.builder()
              .bold(True)
              .italic(False)
              .font_size("14pt/1.5")
              .build()) \
        .text_decoration(1) \
        .formatter("#,##0.00") \
        .h_align(1) \
        .v_align(1) \
        .fore_color("#000000") \
        .back_color("#ffff00") \
        .border_type("FULL_BORDER") \
        .border_color("#ff0000") \
        .build()

    # 应用样式到范围
    s.set_style("A1:C3", style)

    # 或使用字典直接设置
    s.set_style("A1:C3", {
        "font": {"bold": True, "fontSize": "14pt/1.5"},
        "hAlign": 1,
        "foreColor": "#000000",
        "backColor": "#ffff00",
        "borderType": "FULL_BORDER"
    })

    # 清除样式
    s.set_style("A1:C3", CellStyle.builder().clean(True).build())
```

#### 批量设置单元格样式

使用 `set_styles` 可以一次性为多个范围设置不同的样式，比多次调用 `set_style` 更高效。

```python
from fastfeishu.core import FeiShuSheet
from fastfeishu.models import CellStyle, Font
from fastfeishu.models.cell_style import StyleRangeData
from typing import List

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 方式1：使用字典（推荐，更灵活）
    s.set_styles([
        {
            "ranges": ["A1:E1"],
            "style": CellStyle.builder()
                .font(Font.builder().bold().font_size("14pt/1.5").build())
                .fore_color("#000000")
                .back_color("#e6f2ff")
                .h_align(1)
                .border_type("FULL_BORDER")
                .build()
        },
        {
            "ranges": ["C2:C10", "E2:E10"],
            "style": {
                "foreColor": "#ffffff",
                "backColor": "#ff6b6b",
                "hAlign": 1
            }
        }
    ])

    # 方式2：使用 StyleRangeData 类型（更严格的类型检查）
    # 适合需要 IDE 类型提示和静态类型检查的场景
    header_style = CellStyle.builder() \
        .font(Font.builder().bold().font_size("14pt/1.5").build()) \
        .fore_color("#000000") \
        .back_color("#e6f2ff") \
        .h_align(1) \
        .v_align(1) \
        .border_type("FULL_BORDER") \
        .border_color("#0066cc") \
        .build()

    highlight_style = CellStyle.builder() \
        .fore_color("#ffffff") \
        .back_color("#ff6b6b") \
        .h_align(1) \
        .build()

    # 显式声明类型为 List[StyleRangeData]
    style_data: List[StyleRangeData] = [
        StyleRangeData(
            ranges=["A1:E1"],
            style=header_style
        ),
        StyleRangeData(
            ranges=["C2:C10", "E2:E10"],
            style=highlight_style
        ),
        StyleRangeData(
            ranges=["A2:B10"],
            style={
                "hAlign": 0,
                "borderType": "FULL_BORDER"
            }
        )
    ]
    s.set_styles(style_data)

    # 单个样式应用到多个范围
    common_style = CellStyle.builder() \
        .back_color("#f0f0f0") \
        .border_type("FULL_BORDER") \
        .build()

    s.set_styles([
        StyleRangeData(
            ranges=["A1:C3", "E5:G7", "I9:K11"],
            style=common_style
        )
    ])
```

**使用限制**：
- 单次设置的范围不可超过 **5000 行 × 100 列**
- 在设置边框样式时，单次更新的单元格数量不可超过 **30,000 个**
- 当单元格在多个范围中时，单元格将应用请求体的最后一个样式

**样式属性说明**：

**字体样式 (font)**:
- `bold`: 是否加粗（True/False）
- `italic`: 是否斜体（True/False）
- `fontSize`: 字体大小，格式如 "10pt/1.5"（字号范围 [9,36]pt，行距固定 1.5px）
- `clean`: 是否清除字体格式（True/False）

**文本装饰 (textDecoration)**:
- `0`: 默认样式（无下划线和删除线）
- `1`: 下划线
- `2`: 删除线
- `3`: 下划线和删除线

**数字格式 (formatter)**:
- `"@"`: 纯文本
- `"0"`: 数字（1024）
- `"#,##0"`: 数字千分位（1,024）
- `"#,##0.00"`: 数字千分位+小数点（1,024.56）
- `"0%"`: 百分比（10%）
- `"0.00%"`: 百分比小数点（10.24%）
- `"0.00E+00"`: 科学计数（1.02E+03）
- `"¥#,##0"`: 人民币（¥1,024）
- `"¥#,##0.00"`: 人民币小数点（¥1,024.56）
- `"$#,##0"`: 美元（$1,024）
- `"$#,##0.00"`: 美元小数点（$1,024.56）
- `"yyyy/MM/dd"`: 日期（2017/08/10）
- `"yyyy-MM-dd"`: 日期（2017-08-10）
- `"HH:mm:ss"`: 时间（23:24:25）
- `"yyyy/MM/dd HH:mm:ss"`: 日期时间（2017/08/10 23:24:25）

**对齐方式**:
- 水平对齐 (hAlign): `0`-左对齐, `1`-中对齐, `2`-右对齐
- 垂直对齐 (vAlign): `0`-上对齐, `1`-中对齐, `2`-下对齐

**颜色**:
- `foreColor`: 字体颜色，十六进制格式（如 "#000000"）
- `backColor`: 背景色，十六进制格式（如 "#ffff00"）

**边框**:
- `borderType`: 边框类型
  - `"FULL_BORDER"`: 全边框（四周都有边框）
  - `"OUTER_BORDER"`: 外边框（只有外侧有边框）
  - `"INNER_BORDER"`: 内边框（只有内部有边框）
  - `"NO_BORDER"`: 无边框
  - `"LEFT_BORDER"`: 左边框
  - `"RIGHT_BORDER"`: 右边框
  - `"TOP_BORDER"`: 上边框
  - `"BOTTOM_BORDER"`: 下边框
- `borderColor`: 边框颜色，十六进制格式（如 "#ff0000"）

**其他**:
- `clean`: 是否清除所有格式（True/False，默认 False）

---

## 三、单元格类型

支持写入特殊单元格类型，让单元格内容更丰富：

### 3.1 基础类型

```python
from fastfeishu.core import FeiShuSheet
from fastfeishu.models.type import TextLink, Email, Formula, PlainText, Number, DateValue
from datetime import date, datetime

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 文本链接
    s.write('a1', [[TextLink('https://example.com', '点击访问')]])

    # 邮箱
    s.write('b1', [[Email('test@example.com')]])

    # 公式
    s.write('c1', [[Formula('=A1+B1')]])

    # 纯文本（显式）
    s.write('d1', [[PlainText('普通文本')]])

    # 数字（显式）
    s.write('e1', [[Number(123.45)]])

    # 日期（使用飞书日期格式）
    # DateValue(44562) 对应 2022-01-01
    s.write('f1', [[DateValue.from_date(date(2024, 3, 15))]])
    s.write('g1', [[DateValue.today()]])       # 今天
    s.write('h1', [[DateValue.now()]])          # 当前日期时间
    s.write('i1', [[DateValue.from_string("2024-03-15")]])
```

### 3.2 富文本类型

```python
from fastfeishu.core import FeiShuSheet
from fastfeishu.models.type import RichText, SegmentStyle, StyleDirector

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 基础用法：构建富文本
    rich = (RichText.builder()
            .add_plain("状态：")
            .add_bold("成功")
            .add_plain("，共")
            .add_colored("100", "#00cc00")
            .add_plain("条")
            .build())
    s.write('a1', [[rich]])

    # 使用预设样式（Director）
    title = (RichText.builder()
             .add_plain("", StyleDirector.title())  # 标题样式
             .build())

    warning = (RichText.builder()
               .add_plain("警告", StyleDirector.warning())
               .build())

    # 拼接多个 RichText
    rich1 = RichText.builder().add_plain("Part1").build()
    rich2 = RichText.builder().add_bold("Part2").build()
    combined = (RichText.builder()
                .append_rich(rich1)
                .add_plain(" - ")
                .append_rich(rich2)
                .build())
```

### 3.3 @人和@文档

```python
from fastfeishu.core import FeiShuSheet
from fastfeishu.models.type import MentionUser, MentionDoc

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # @人（通过邮箱）
    s.write('a1', [[MentionUser(
        user_info='user@example.com',
        text_type='email',
        notify=True
    )]])

    # @文档
    s.write('b1', [[MentionDoc(
        file_token='doc_token',
        obj_type='doc'
    )]])
```

### 3.4 下拉列表

```python
from fastfeishu.core import FeiShuSheet
from fastfeishu.models.type import MultipleValue

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 创建下拉列表
    s.write('a1', [[MultipleValue(['选项A', '选项B', '选项C'])]])

    # 包含布尔值的下拉列表
    s.write('b1', [[MultipleValue([True, False, '待定'])]])
```

### 3.5 带样式的链接和邮箱

```python
from fastfeishu.core import FeiShuSheet
from fastfeishu.models.type import StyledLink, StyledEmail, SegmentStyle, TextSegment

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 带分段样式的链接
    s.write('a1', [[StyledLink(
        link='https://example.com',
        text='点击访问',
        segments=[
            TextSegment("访问", SegmentStyle(bold=True, foreColor="#ff0000").to_json()),
            TextSegment("页面", SegmentStyle(italic=True).to_json())
        ]
    )]])

    # 带样式的邮箱
    s.write('b1', [[StyledEmail(
        email='test@example.com',
        segments=[
            TextSegment("联系", SegmentStyle(bold=True).to_json()),
            TextSegment("我们", SegmentStyle(italic=True).to_json())
        ]
    )]])
```

### 3.6 自动类型转换

```python
from fastfeishu.core import FeiShuSheet
from fastfeishu.models.type import CellTypeConverter

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 自动识别类型并转换
    cell = CellTypeConverter.auto_convert("https://example.com")  # 返回 NotTextLink
    cell2 = CellTypeConverter.auto_convert("test@example.com")      # 返回 Email
    cell3 = CellTypeConverter.auto_convert("=A1+B1")               # 返回 Formula
    cell4 = CellTypeConverter.auto_convert(123)                   # 返回 123（数字）
    cell5 = CellTypeConverter.auto_convert(True)                    # 返回 PlainText("True")

    # 批量转换列表
    data = ["https://example.com", "test@example.com", "=A1+B1", 123]
    cells = CellTypeConverter.from_list(data)

    # 批量转换二维表格
    table = [
        ["https://example.com", "test@example.com"],
        ["=A1+B1", 123]
    ]
    cells_table = CellTypeConverter.from_list_to_json(table)
    s.write('A1:D2', cells_table)
```

---

## 四、批量处理

### 4.1 FeiShuUtil 工具类

```python
from fastfeishu.core import FeiShuSheet
from fastfeishu.utils import FeiShuUtil
from typing import List, Dict, Any

if __name__ == '__main__':
    source_sheet = FeiShuSheet('源Sheet链接')
    target_sheet = FeiShuSheet('目标Sheet链接')

    # 直接复制数据
    FeiShuUtil.process_rows_to_new_sheet(source_sheet, target_sheet)

    # 自定义行处理函数
    # row_handler 接收一行数据（dict），返回要写入的行列表（每个元素是一个 dict）
    def even_insert_handler(row: Dict[str, Any]) -> List[Dict[str, Any]]:
        # row 是字典，如 {"CaseID": 1, "query": "...", "预期APIINFO": "..."}
        if row.get("CaseID") % 2 == 0:  # 偶数 CaseID
            empty = {k: None for k in row}  # 与原行同结构的空行
            return [empty, empty, row]      # 插2空行 + 原行
        return []  # 其他行丢弃

    FeiShuUtil.process_rows_to_new_sheet(
        source_sheet,
        target_sheet,
        row_handler=even_insert_handler,
        batch_write=2000  # 批量写入行数
    )

    # 替换占位符（智能类型保持）
    # 纯占位符（如 {price}）会保持原始类型
    # 混合文本（如 "价格：{price}元"）会转为字符串
    FeiShuUtil.replace_placeholder(
        sheet=source_sheet,
        sheet_range='A1:A5',
        name='张三',
        age=25,
        price=99.99
    )
```

### 4.2 自定义数据源

```python
from fastfeishu.core import FeiShuSheet
from fastfeishu.utils import FeiShuUtil
from typing import Generator

if __name__ == '__main__':
    source_sheet = FeiShuSheet('源Sheet链接')
    target_sheet = FeiShuSheet('目标Sheet链接')

    l = [
        {"a": 1, "b": 2},
        {"a": 3, "b": 4},
        {"a": 5, "b": 6},
    ]

    class CustomIter:
        @staticmethod
        def iterrows(start_row: int, end_row: int = None) -> Generator[dict, None, None]:
            if end_row is None:
                end_row = len(l)
            for i in range(start_row, end_row):
                l[i]['t'] = 'hhh'
                yield l[i]

    # 使用自定义数据源
    FeiShuUtil.process_rows_to_new_sheet(
        CustomIter,
        target_sheet,
        row_handler=even_insert_handler
    )
```

### 4.3 批量下载图片（通用工具）

```python
from fastfeishu.utils.common import batch_download_images, sync_batch_download_images

# 异步批量下载（推荐）
success_list, failed_list = await batch_download_images(
    urls=["https://example.com/1.jpg", "https://example.com/2.png"],
    qps=10,                              # 每秒最多10个请求
    save_dir="./downloaded_images",      # 保存到本地
    return_type="both",                  # 返回状态 + 二进制
    failed_log_path="logs/failed.json",
    headers={"Referer": "https://example.com"}
)

# 同步批量下载（在同步代码中使用）
success_list, failed_list = sync_batch_download_images(
    urls=["https://example.com/1.jpg", "https://example.com/2.png"],
    qps=10,
    save_dir="./downloaded_images",
    return_type="binary"
)
```

### 4.4 随机抽样工具

```python
from fastfeishu.utils.common import sample_from_array

labels = ['[安全]', '[涉政]', '[安全]', '[涉政]', '[其他]']

# 随机抽取3个（不按标签分组）
result = sample_from_array(labels, label_config=None, max_samples=3)

# 按指定字典抽取
result = sample_from_array(labels, label_config={'[安全]': 2, '[涉政]': 1})

# 针对所有独特标签，每种抽取最多2个
result = sample_from_array(labels, label_config={}, max_samples=2)
```

---

## 五、Sheet 管理

### 5.1 创建和复制 Sheet

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 创建新 Sheet（在指定位置）
    new_sheet = s.create_sheet(title='新Sheet', index=0)
    print(f"新Sheet链接: {new_sheet.link}")

    # 复制当前 Sheet
    copied_sheet = s.copy(title='副本')
    print(f"复制后的Sheet链接: {copied_sheet.link}")
```

### 5.2 获取 Sheet 信息

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接', readonly=True)

    # 获取当前 Sheet 信息
    info = s.get_sheet_info()
    print(f"行数: {info['rowCount']}, 列数: {info['columnCount']}")

    # 获取所有 Sheet 信息
    sheets = s.get_sheets_info()
    for sheet in sheets:
        print(f"Sheet标题: {sheet.title}, ID: {sheet.sheetId}")

    # 获取工作簿标题
    workbook_title = s.get_workbook_title()
    print(f"工作簿标题: {workbook_title}")

    # 获取表头
    header = s.get_header()
    print(f"表头: {header}")
```

### 5.3 属性和状态

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接', readonly=True)

    # 检查是否只读
    print(s.is_readonly())  # True

    # 获取基础属性
    print(s.sheet_token)   # Sheet Token
    print(s.sheet_id)      # Sheet ID
    print(s.link)          # 当前链接

    # 获取原始请求对象（高级用法）
    raw_req = s.raw_request
```

---

## 六、API 参考方法

### FeiShuSheet 主要方法

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
- `write(sheet_range, data_list)` - 写入范围
- `write_batch(value_ranges)` - 批量写入多个范围
- `write_row(data, write_row=2, skip_none=True, partition_strategy='auto')` - 写入行
- `write_column(column_name, data_list, start_row=2)` - 写入列
- `write_row_by_hang_header(hang_header_range, data, write_row=2, skip_none=True, partition_strategy='auto')` - 悬挂表头写入
- `write_image(cell, image, image_name="cell.png")` - 写入图片
- `append(sheet_range, data_list)` - 追加数据
- `append_to_column(column_name, data_list)` - 追加写入列数据
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

## 七、异常处理

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

### 7.1 tenant_access_token 自动刷新

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

### 7.2 自定义触发刷新的错误码

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

## 八、测试

### 8.1 安装测试依赖

```bash
# 安装核心依赖 + 开发测试工具（pytest 等）
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 建议同时安装可选功能依赖，以便跑通图片压缩 / 批量下载相关代码路径
pip install ".[image,download]"
```

### 8.2 运行测试

#### 运行所有测试

```bash
# 基本运行
pytest

# 显示详细信息
pytest -v

# 显示覆盖率报告
pytest --cov=fastfeishu --cov-report=html
```

#### 运行特定类型的测试

```bash
# 只运行单元测试（快速，不需要API凭证）
pytest -m unit

# 只运行集成测试（需要配置 .env 中的 API 凭证）
pytest -m integration

# 排除慢速测试
pytest -m "not slow"
```

#### 运行特定测试文件或函数

```bash
# 运行单个测试文件
pytest tests/unit/test_request.py

# 运行特定测试类
pytest tests/unit/test_request.py::TestFeiShuRequest

# 运行特定测试函数
pytest tests/unit/test_request.py::TestFeiShuRequest::test_parse_feishu_url

# 根据名称模糊匹配
pytest -k "test_parse"
```

### 8.3 查看测试覆盖率

```bash
# 生成HTML覆盖率报告
pytest --cov=fastfeishu --cov-report=html

# 在浏览器中打开 htmlcov/index.html 查看详细报告
```

### 8.4 编写自己的测试

#### 单元测试示例

创建测试文件 `tests/unit/test_your_feature.py`：

```python
import pytest
from unittest.mock import Mock, patch
from fastfeishu.your_module import YourClass


@pytest.mark.unit
class TestYourFeature:
    """你的功能测试"""

    def test_basic_function(self):
        """测试基本功能"""
        obj = YourClass()
        result = obj.some_method()
        assert result == expected_value

    @patch('fastfeishu.your_module.external_api')
    def test_with_mock(self, mock_api):
        """使用mock测试"""
        mock_api.return_value = "mocked_data"
        obj = YourClass()
        result = obj.method_using_api()
        assert result == "expected"
```

#### 使用测试Fixtures

测试fixtures在 `tests/conftest.py` 中定义，可直接使用：

```python
def test_with_fixtures(feishu_url, sample_header, mock_read_response):
    """使用共享fixtures"""
    # fixtures会自动注入
    assert len(sample_header) > 0
    assert mock_read_response["code"] == 0
```

#### 参数化测试

```python
@pytest.mark.parametrize("input,expected", [
    (1, "A"),
    (26, "Z"),
    (27, "AA"),
])
def test_num_to_excel_col(input, expected):
    from fastfeishu.utils import num_to_excel_col
    assert num_to_excel_col(input) == expected
```

### 8.5 测试最佳实践

1. **测试命名规范**
   - 测试文件：`test_*.py`
   - 测试类：`Test*`
   - 测试函数：`test_*`

2. **测试结构（AAA模式）**
   ```python
   def test_example():
       # Arrange - 准备数据
       data = prepare_data()

       # Act - 执行操作
       result = function_under_test(data)

       # Assert - 验证结果
       assert result == expected
   ```

3. **Mock外部依赖**
   - 单元测试应该mock所有外部API调用
   - 使用 `@patch` 装饰器或 `pytest-mock`

4. **测试覆盖率目标**
   - 核心模块：>80%
   - 工具函数：>90%
   - 模型类：>70%

### 8.6 测试标记说明

- `@pytest.mark.unit` - 单元测试，不依赖外部服务
- `@pytest.mark.integration` - 集成测试，需要真实API
- `@pytest.mark.slow` - 慢速测试
- `@pytest.mark.smoke` - 冒烟测试

### 8.7 更多信息

详细的测试指南请参考 [tests/README.md](tests/README.md)

---

## 九、开发者指南

如果你想参与项目开发，请查看以下文档：

### 📖 必读文档

- **[开发者贡献指南](docs/CONTRIBUTING.md)** - 开发工作流、测试流程、代码规范
- **[项目架构指南](docs/CLAUDE.md)** - 架构设计、设计模式、模块说明

### 🛠️ 快速参考

#### Git 提交规范

所有提交信息必须遵循约定式提交格式：

```bash
git commit -m "[feat] 新功能描述"
git commit -m "[fix] Bug修复描述"
git commit -m "[docs] 文档更新"
```

**提交类型**: `[feat]` `[fix]` `[perf]` `[refactor]` `[docs]` `[test]` `[chore]` `[style]`

详细说明请参考 **[开发者贡献指南](docs/CONTRIBUTING.md)**。

#### 自动化测试

本项目配置了 pre-push hook，执行 `git push` 时会自动运行单元测试：

- ✅ 测试通过 → 推送成功
- ❌ 测试失败 → 推送被阻止

```bash
# 手动运行测试
pytest tests/unit -v -m unit

# 查看测试覆盖率
pytest tests/unit -v -m unit --cov=fastfeishu --cov-report=term-missing
```

#### CI/CD

本项目使用 GitHub Actions 进行持续集成：

- **触发时机**: Pull Request 到 main/dev 分支
- **测试环境**: Python 3.11 和 3.12
- **状态查看**: [GitHub Actions](../../actions)

### 🏗️ 架构原则

本项目遵循严格的分层架构（从底到高）：

```
helpers.py (纯工具函数，零依赖)
   ↓
models/ (数据模型层)
   ↓
core/ (核心业务逻辑层)
   ↓
utils/ (高级工具层)
```

**重要规则**：
- `helpers.py` 永远不应导入项目内其他模块
- 低层模块不应导入高层模块
- 避免循环依赖

详细说明请参考 **[项目架构指南](docs/CLAUDE.md)**。

---

## 十、许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 十一、贡献

欢迎贡献！请先阅读 **[开发者贡献指南](docs/CONTRIBUTING.md)** 了解如何参与项目开发。
