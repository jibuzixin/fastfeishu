# 飞书 API 快速操作

## 一、快速上手

### 1. 安装

**使用 Python 3.11 版本**（3.12 可能存在依赖冲突）

```bash
# 创建虚拟环境
conda create -n feishu python=3.11 -y

# 激活环境
conda activate feishu

# 以源码安装
cd fastfeishu
pip install -e . --index-url https://artifactory.ep.chehejia.com/artifactory/api/pypi/licloud-pypi/simple
```

### 2. 环境变量配置

在项目根目录创建 `.env` 文件：

```bash
# 飞书应用凭证
FS_APP_ID=''           # 飞书应用ID
FS_APP_SECRET=''       # 飞书应用密钥

# OiS3 凭证（可选）
OiS_REGION=''
OiS_IDAAS_CLIENT_ID=''
OiS_IDAAS_CLIENT_SECRET=''
OiS_IDAAS_SERVICE_ID=''
```

### 3. 目录结构

```
项目根目录
├── chatgpt             # 大模型接口
├── fastfeishu          # 飞书在线文档操作接口
│   ├── __init__.py
│   ├── configs/        # 配置管理
│   ├── core/           # 核心实现
│   │   ├── interface.py   # 抽象接口
│   │   ├── operations.py  # 操作层
│   │   ├── request.py     # API请求层
│   │   └── sheet.py       # 高层接口
│   ├── exceptions/     # 异常类
│   ├── models/         # 数据模型
│   │   ├── feishu_util.py        # 工具类
│   │   ├── sheet_properties.py   # Sheet属性配置
│   │   └── type.py               # 单元格类型
│   └── utils/          # 工具函数
├── scripts             # 日常脚本
├── requirements.txt    # 依赖列表
├── setup.py            # 项目元数据
└── README.md           # 说明文档
```

## 二、基础操作

### 2.1 读取数据

#### 单元格读取、范围读取

```python
from fastfeishu.feishu import FeiShuSheet

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

#### 遍历整张表（流式读取）

```python
from fastfeishu.feishu import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接', readonly=True)

    # 默认从第2行开始，每次读取500行
    for row in s.iterrows():
        print(row['CaseID'], row['query'], row['预期APIINFO'])

    # 自定义起始行、结束行、批次大小
    for row in s.iterrows(start_row=5, end_row=100, batch_size=1000):
        print(row)
```

#### 读取图片

```python
from fastfeishu.feishu import FeiShuSheet

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
from fastfeishu.feishu import FeiShuSheet

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
from fastfeishu.feishu import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 写入单列数据
    s.write_column("自动化", [1, 2, 3, 4, 5, 6, 7, 8])

    # 从指定行开始写入
    s.write_column("自动化", [1, 2, 3, 4, 5, 6, 7, 8], start_row=4)
```

#### 按列名写入行（支持字典或二维数组）

```python
from fastfeishu.feishu import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 使用字典写入
    s.write_row([
        {'CaseID': 1, '意图类型': '这是什么', '端到端回复': '回复内容'},
        {'CaseID': 2, '意图类型': 'type', '端到端回复': '回复内容2'},
        [3, None, None, "这是什么东西"],  # 支持数组
    ], write_row=4)  # 从第4行开始写入
```

#### 悬挂表头写入

```python
from fastfeishu.feishu import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 使用自定义表头范围
    s.write_row_by_hang_header(
        hang_header_range='A1:D1',  # 表头范围
        data=[  # 数据
            {'CaseID': 1, '意图类型': 'type', '端到端回复': '回复内容'},
            {'CaseID': 2, '意图类型': 'type', '端到端回复': '回复内容2'},
        ],
        write_row=2  # 数据从第2行开始
    )
```

#### 写入图片

```python
from fastfeishu.feishu import FeiShuSheet

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
from fastfeishu.feishu import FeiShuSheet

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
from fastfeishu.feishu import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 在C列右边插入1个空列
    s.insert_column_to_right('C', insert_number=1)

    # 在B列左边插入2个空列
    s.insert_column_to_left('B', insert_number=2)
```

### 2.4 高级操作

#### 替换占位符

```python
from fastfeishu.feishu import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 替换目标范围内，单元格中的占位符为实际值
    # 如：将 a2:c2 范围的单元格中包含 {name}, {age}, {city} 替换为实际的值
    # 注意当前只支持字符串
    s.replace_placeholder(
        sheet_range='a2:c2',
        name='张三',
        age=25,
        city='北京'
    )
```

#### Sheet属性配置

```python
from fastfeishu.feishu import FeiShuSheet
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
        .protect(protect)
        .build()

    s.update_sheet_properties(properties)
```

## 三、批量处理

### 3.1 FeiShuUtil 工具类

```python
from fastfeishu.feishu import FeiShuSheet, FeiShuUtil
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
from fastfeishu.feishu import FeiShuSheet, FeiShuUtil
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
from fastfeishu.feishu import FeiShuSheet
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
- `iterrows(start_row=2, end_row=None, batch_size=500)` - 流式迭代
- `get_title()` - 获取标题
- `get_header()` - 获取表头

**写入方法**:
- `write(sheet_range, data_list)` - 写入范围
- `write_row(data, write_row=2)` - 写入行
- `write_column(column_name, data_list, start_row=2)` - 写入列
- `write_row_by_hang_header(hang_header_range, data, write_row=2)` - 悬挂表头写入
- `write_image(cell, image, image_name="cell.png")` - 写入图片

**删除/插入方法**:
- `delete_series(start_index, end_index)` - 删除行列
- `delete_series_by_index(start_index, end_index)` - 按索引删除
- `delete_column_by_name(start_col_name, end_col_name)` - 按列名删除
- `insert_column_to_right(column_letter, insert_number=1)` - 右侧插入列
- `insert_column_to_left(column_letter, insert_number=1)` - 左侧插入列

**高级方法**:
- `replace_placeholder(sheet_range, **kwargs)` - 替换占位符
- `get_index_by_col_name(col_name)` - 根据列名获取索引
- `get_letter_by_col_name(col_name)` - 根据列名获取字母

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

