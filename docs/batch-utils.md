# 批量处理工具

## 1. FeiShuUtil 工具类

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

## 2. 自定义数据源

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

## 3. 批量下载图片（通用工具）

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

## 4. 随机抽样工具

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
