# 基础操作（读取 / 写入 / 删除 / 样式）

## 1. 读取数据

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

## 2. 写入数据

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

    # skip_none：不把 None 写进表格，保留该单元格的原有内容
    # 注意：行/列对齐不变——None 的位置不写、不挪位、不紧凑
    s.write('A2:C2', [[1, None, 3]], skip_none=True)
    # -> 1 写入 A2，3 写入 C2（不是 B2），B2 的原值保留不变
```

> **`skip_none` 语义（所有写方法统一）**：`skip_none=True` 表示**不把 None 值写进飞书表格**，
> 保留 None 位置单元格的既有内容，且**不改变行列对齐**——第 (r,c) 个值仍落在原位置，
> None 的格子直接跳过、不剔除、不紧凑。实现上用 `partition_grid` 把含 None 的网格切成
> 若干"全非 None 矩形"按原位置批量写入。`skip_none=False`（默认）则用 None 覆盖对应单元格。
> 支持 `skip_none` 的方法：`write` / `write_batch` / `write_column` / `append_to_column`
> / `write_row` / `write_row_by_hang_header`。`partition_strategy` 仅在 `skip_none=True` 时生效
> （`'auto'`/`'horizontal'`/`'vertical'`）。

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

    # skip_none=True：每个范围各自分区，None 位置不写、不紧凑
    s.write_batch([
        {"range": "A2:C2", "values": [[1, None, 3]]},
    ], skip_none=True)
    # -> 1 写入 A2，3 写入 C2，B2 保留原值
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

    # skip_none=True：None 行不写、保留原内容、行对齐不变（不紧凑）
    s.write_column("自动化", [1, None, 3], start_row=2, skip_none=True)
    # -> 1 写入第 2 行，3 写入第 4 行（第 3 行原值保留）
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

    # skip_none=True：None 位置不写、行对齐不变（不剔除、不紧凑）
    s.append_to_column("自动化", [1, None, 3], skip_none=True)
    # -> 1 和 3 追加到列尾的原位置，None 的那行不写、不挪位
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

## 3. 删除数据

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

## 4. 行列追加

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

## 5. 高级操作

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
