# 飞书 API 快速操作

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Test Coverage](https://img.shields.io/badge/coverage-57%25-yellow)](docs/TESTING.md)

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

# 安装项目
cd fastfeishu
pip install -e .
```

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
├── chatgpt                         # 大模型接口
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
│   │   └── type.py                 # 单元格类型
│   └── utils/                      # 高级工具
│       ├── common.py               # 批量下载等高级功能
│       ├── feishu_util.py          # FeiShuUtil 工具类
│       └── partition_grid.py       # 网格分区算法
├── requirements.txt                # 依赖列表
├── setup.py                        # 项目元数据
└── README.md                       # 说明文档
```

**架构分层**（从底到高）：
- `helpers.py` - 底层纯函数（无任何依赖）
- `models/` - 数据模型层
- `core/` - 核心业务逻辑层
- `utils/` - 高级工具层（可依赖 core）

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
```

#### 遍历整张表（流式读取）

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接', readonly=True)

    # 默认从第2行开始，每次读取500行
    for row in s.iterrows():
        print(row['CaseID'], row['query'], row['预期APIINFO'])

    # 自定义起始行、结束行、批次大小
    for row in s.iterrows(start_row=5, end_row=100, batch_size=1000):
        print(row)

    # 上述默认读取的单元格内容为适合人类阅读的
    # 更改 read_method 方法引用为 read_raw 可以读取原始单元格的值（比如带文本的链接、公式表达式）
    for row in s.iterrows(read_method=s.read_raw):
        print(row)
```

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
```

### 2.4 高级操作

#### 替换占位符（支持类型保持）

```python
from fastfeishu.core import FeiShuSheet

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

    s.replace_placeholder(
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

## 三、批量处理

### 3.1 FeiShuUtil 工具类

```python
from fastfeishu.core import FeiShuSheet
from fastfeishu.utils import FeiShuUtil
from typing import List, Dict, Any
import pandas as pd

if __name__ == '__main__':
    source_sheet = FeiShuSheet('源Sheet链接')
    target_sheet = FeiShuSheet('目标Sheet链接')

    # 直接复制数据
    FeiShuUtil.process_rows_to_new_sheet(source_sheet, target_sheet)

    # 自定义行处理函数
    def even_insert_handler(row: pd.Series) -> List[Dict[str, Any]]:
        if row.name % 2 == 0:  # 偶数行
            empty = {k: None for k in row.index}
            return [empty, empty, row.to_dict()]  # 插2空行 + 原行
        return []  # 奇数行丢弃

    FeiShuUtil.process_rows_to_new_sheet(
        source_sheet,
        target_sheet,
        row_handler=even_insert_handler,
        batch_write=2000  # 批量写入行数
    )
```

### 3.2 自定义数据源

```python
from fastfeishu.core import FeiShuSheet
from fastfeishu.utils import FeiShuUtil
from typing import Generator
import pandas as pd

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

## 四、单元格类型

支持写入特殊单元格类型：

```python
from fastfeishu.core import FeiShuSheet
from fastfeishu.models.type import TextLink, Email, Formula

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 文本链接
    s.write('a1', [[TextLink('https://example.com', '点击访问')]])

    # 邮箱
    s.write('b1', [[Email('test@example.com')]])

    # 公式
    s.write('c1', [[Formula('=A1+B1')]])
```

## 五、API 参考方法

### FeiShuSheet 主要方法

**读取方法**:
- `read(sheet_range)` - 读取范围
- `read_raw(sheet_range)` - 读取原始数据（含公式）
- `read_human(sheet_range)` - 人类可读方式读取
- `read_images(sheet_range)` - 读取图片
- `read_column(column_name)` - 读取指定列（返回一维数组）
- `iterrows(start_row=2, end_row=None, batch_size=500)` - 流式迭代
- `get_title()` - 获取标题
- `get_header()` - 获取表头

**写入方法**:
- `write(sheet_range, data_list)` - 写入范围
- `write_row(data, write_row=2, skip_none=True, partition_strategy='auto')` - 写入行
- `write_column(column_name, data_list, start_row=2)` - 写入列
- `write_row_by_hang_header(hang_header_range, data, write_row=2, skip_none=True, partition_strategy='auto')` - 悬挂表头写入
- `write_image(cell, image, image_name="cell.png")` - 写入图片
- `append_to_column(column_name, data_list)` - 追加写入列数据

**删除/插入方法**:
- `delete_series(start_index, end_index)` - 删除行列
- `delete_series_by_index(start_index, end_index)` - 按索引删除
- `delete_column_by_name(start_col_name, end_col_name)` - 按列名删除
- `insert_column_to_right(column_letter, insert_number=1)` - 右侧插入列
- `insert_column_to_left(column_letter, insert_number=1)` - 左侧插入列

**高级方法**:
- `replace_placeholder(sheet_range, **kwargs)` - 替换占位符（智能类型保持）
- `get_index_by_col_name(col_name)` - 根据列名获取索引
- `get_letter_by_col_name(col_name)` - 根据列名获取字母
- `write_batch(value_ranges)` - 批量写入多个范围

**图片方法**:
- `download_image_to_path(file_token, save_path)` - 下载到路径
- `download_image_bytes(file_token)` - 下载为字节
- `download_image_stream(file_token)` - 下载为流
- `download_image_base64(file_token, compress=None)` - 下载为Base64

**Sheet管理**:
- `create_sheet(title, index=0)` - 创建新Sheet
- `copy(title)` - 复制当前Sheet
- `update_sheet_properties(properties)` - 更新Sheet属性
- `set_style(sheet_range, style)` - 设置样式

## 六、异常处理

```python
from fastfeishu.exceptions import FeiShuException, FeiShuRequestException, FeiShuColumnNotExist

try:
    s = FeiShuSheet('飞书链接')
    # 操作代码
except FeiShuColumnNotExist as e:
    print(f"列不存在: {e}")
except FeiShuRequestException as e:
    print(f"请求异常: {e}")
except FeiShuException as e:
    print(f"飞书异常: {e}")
```

## 七、测试

### 7.1 安装测试依赖

```bash
# 安装所有依赖（包括测试依赖）
pip install -r requirements.txt

# 或者只安装开发测试依赖
pip install -r requirements-dev.txt
```

### 7.2 运行测试

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

### 7.3 查看测试覆盖率

```bash
# 生成HTML覆盖率报告
pytest --cov=fastfeishu --cov-report=html

# 在浏览器中打开 htmlcov/index.html 查看详细报告
```

### 7.4 编写自己的测试

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

### 7.5 测试最佳实践

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

### 7.6 测试标记说明

- `@pytest.mark.unit` - 单元测试，不依赖外部服务
- `@pytest.mark.integration` - 集成测试，需要真实API
- `@pytest.mark.slow` - 慢速测试
- `@pytest.mark.smoke` - 冒烟测试

### 7.7 更多信息

详细的测试指南请参考 [tests/README.md](tests/README.md)

## 八、开发者指南

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

## 九、许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 十、贡献

欢迎贡献！请先阅读 **[开发者贡献指南](docs/CONTRIBUTING.md)** 了解如何参与项目开发。
