from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Literal


@dataclass
class Protect:
    lock: Optional[bool] = None
    lock_info: Optional[str] = None
    user_ids: List[str] = field(default_factory=list)

    @classmethod
    def builder(cls):
        return Protect.Builder()

    class Builder:
        def __init__(self):
            self.protect = Protect()

        def lock(self, lock: bool=True):
            if lock:
                self.protect.lock = "LOCK"
            else:
                self.protect.lock = "UNLOCK"
            return self

        def lock_info(self, lock_info: str):
            self.protect.lock_info = lock_info
            return self

        def user_ids(self, user_ids: List[str]):
            self.protect.user_ids = user_ids
            return self

        def build(self):
            return self.protect

@dataclass
class SheetProperties:
    """"""
    sheet_id: Optional[str] = None
    title: Optional[str] = None
    index: Optional[int] = None
    hidden: Optional[bool] = None
    frozen_col_count: Optional[int] = None
    frozen_row_count: Optional[int] = None
    protect: Optional[Protect] = None

    @classmethod
    def builder(cls):
        return SheetProperties.Builder()

    class Builder:
        def __init__(self):
            self.sheet = SheetProperties()

        def sheet_id(self, sheet_id: str):
            self.sheet.sheet_id = sheet_id
            return self

        def title(self, title: str):
            self.sheet.title = title
            return self

        def index(self, index: int):
            self.sheet.index = index
            return self

        def hidden(self, hidden: bool):
            self.sheet.hidden = hidden
            return self

        def frozen_col_count(self, frozen_col_count: int):
            self.sheet.frozen_col_count = frozen_col_count
            return self

        def frozen_row_count(self, frozen_row_count: int):
            self.sheet.frozen_row_count = frozen_row_count
            return self

        def protect(self, protect: Protect):
            self.sheet.protect = protect
            return self

        def build(self):
            return self.sheet

    def to_dict(self):
        """过滤掉未设置的值，只转化有值的属性为 Dict"""
        sheet_dict = asdict(self)
        return {k: v for k, v in sheet_dict.items() if v is not None}