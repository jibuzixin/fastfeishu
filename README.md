# 飞书 API 快速操作
# 一、快速上手
## 1. 安装
**使用 python 3.11. 的版本**，太高会有依赖冲突（*如果解决好冲突可以更新*）

1. 首先新建一个虚拟环境
```bash
conda create -n feishu python=3.11 -y
```
2. 激活环境
```bash
conda activate feishu
```
3. 以源码安装包，以便在任何地方使用和修改
```bash
# 进入项目目录
cd fastfeishu
# 执行，后面的私有仓库为了安装 ois3 的依赖
pip install -e . --index-url https://artifactory.ep.chehejia.com/artifactory/api/pypi/licloud-pypi/simple
```
4. 敏感信息需要填写进环境变量，在项目根目录中创建 .env 文件写入下面信息
```bash
# 找尉卓洋要
FS_APP_ID=''  # 飞书相关
FS_APP_SECRET=''

OiS_REGION=''  # OiS3相关
OiS_IDAAS_CLIENT_ID=''
OiS_IDAAS_CLIENT_SECRET=''
OiS_IDAAS_SERVICE_ID=''
```

后续不需要卸载
```bash
pip uninstall fastfeishu
```

## 2. 目录结构说明

```bash
项目根目录
├── chatgpt             # 调用大模型的方法接口
├── fastfeishu          # 飞书在线文档操作接口
│   ├── __init__.py
│   ├── configs             # 飞书接口的配置
│   ├── exceptions          # 飞书异常类
│   ├── core                # 飞书核心代码
│   ├── models              # 飞书用到的实体类，包含飞书类变量、配置类
│   └── utils               # 飞书操作将可能使用到的工具
├── README.md           # 说明文档
├── requirements.txt    # 依赖 使用 pip install -r requirements.txt 安装
├── scripts             # 日常会经常使用到的脚本，构建数据集、上传图片、音频等
└── setup.py            # 项目元数据
```

## 3. 简单操作
### 读取
单元格读取、范围读取
```python
from fastfeishu.feishu import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接', readonly=True)  # 为 True 只读模式
    h = s.read('M2:m2')  # 单元格
    print(h)
    h = s.read('a2:Ai33')  # 范围
    print(h)
```
遍历整张表
```python
from fastfeishu.feishu import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接', readonly=True)  # 为 True 只读模式
    for row in s.iterrows():
        print(row['CaseID'], row['query'], row['预期APIINFO'])
```
读取单元格 A2 图片
```python
from fastfeishu.feishu import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')
    data = s.read_images('a2:a2')  # 获取图片信息
    file_token = data['fileToken']  # 获取token
    s.download_image_to_path(file_token, 'tmp_image_1.png')  # 下载图片
    base64 = s.download_image_base64(file_token)  # 获取图片 base64 编码
    img_bytes = s.download_image_bytes(file_token)  # 获取二进制流
```

### 2.2 写入
写入一个范围的数据，用二维数组表示写入的行和列
```python
from fastfeishu.feishu import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')
    h = s.write('M2:m2', [['字符串 或者 数字，或者可序列化对象']])  # 单元格
    print(h)
    h = s.write('a2:Ai33', [[...], [...], [...] ... ...])  # 范围
    print(h)
```
根据列名或者数组更方便的从第四行开始写入
```python
from fastfeishu.feishu import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')
    s.write_row(
        [
            {'CaseID': 1, '图像（系统不需要,水印去除)': "asdas", "意图类型": "这是什么"},
            {'CaseID': 2, '意图类型': "type", "端到端回复": "... ..."},
            [3, None, None, "这是什么东西"],
        ], 
        write_row=4)
```
根据列名写入一列数据，如果列不存在则在末尾新增
```python
from fastfeishu.feishu import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')
    s.write_column("自动化", [1,2,3,4,5,6,7,8,])  # 在“自动化”列写入了1，2，3，4，5 ... ...
    s.write_column("自动化", [1,2,3,4,5,6,7,8,], start_row=4)  # 从第四行开始写
```
写入单元格 A2 图片
```python
from fastfeishu.feishu import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')
    s.write_image('a2', '传入本地图片地址 或 二进制流', '示例图.png')
```

### 2.3 删除
删除 6~8 行,包含第 6 行和第 8 行
```python
from fastfeishu.feishu import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')
    s.delete_series(6, 8)
```
删除“端到端回复”列
```python
from fastfeishu.feishu import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')
    s.delete_series("端到端回复")
```
删除“CaseID”到“端到端回复”之间（包含此两列）的所有列
```python
from fastfeishu.feishu import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')
    s.delete_series("CaseID", "端到端回复")
```

### 2.4 便携操作
```python
from fastfeishu.feishu import FeiShuSheet, FeiShuUtil
from typing import List, Dict, Any
import pandas as pd

if __name__ == '__main__':
    source_sheet = FeiShuSheet('')
    target_sheet = FeiShuSheet('')
    # 没有传入函数，则将 source 复制到 target 中
    FeiShuUtil.process_rows_to_new_sheet(source_sheet, target_sheet)

    # 偶数行前面插 2 空行，奇数行删除
    def even_insert_handler(row: pd.Series) -> List[Dict[str, Any]]:
        if row.name % 2 == 0:   # pd.DataFrame.iterrows 的 name 就是原始索引
            empty = {k: None for k in row.index}
            return [empty, empty, row.to_dict()]
        return []               # 奇数行直接丢弃
    # target 表数据将会是 source 中的数据进行偶数行前面插 2 空行，奇数行删除操作后的样子
    FeiShuUtil.process_rows_to_new_sheet(source_sheet, target_sheet, row_handler=even_insert_handler)
```
上述是对于飞书类而言，如果想有自己构造的数据写入，或者读取的本地文件写入的话，需要根据协议实现对应的生成器即可。（例子如下）
```python
# 数组中每一个字典都是一行数据，每一个键都代表列名，写到对应的列中
# 如果原本没有的列名，在这里新增，那么新 sheet 中就会有对应的新列
# 目前缺点，需要自己手动对应列的位置，因为目前写入是按照 list[dict.values()] 顺序写入，没有列名映射
l = [
    {"a": 1, "b": 2},
    {"a": 3, "b": 4},
    {"a": 5, "b": 6},
    {"a": 7, "b": 8},
    {"a": 9, "b": 9},
]
class CustomIter:
    @staticmethod
    def iterrows(
            start_row: int,
            end_row: Optional[int] = None,
    ) -> Generator[dict[str, int], None, None]:
        if end_row is None:
            end_row = len(l)
        for i in range(start_row, end_row):
            l[i]['t'] = 'hhh'
            yield l[i]

for i in Custom().iterrows(0):
    print(i)

FeiShuUtil.process_rows_to_new_sheet(CustomIter, target_sheet, row_handler=even_insert_handler)
```

# 二、日常使用工具
可在 scripts 文件夹中找到