import uuid

class FeishuVariable:
    def __init__(self, type_hint=None, default=None, readonly_after_first_set=False):
        self.readonly_after_first_set = readonly_after_first_set
        self.type_hint = type_hint
        self.default = default
        self.name = None
        self._value_set_flag_name = None  # 用于记录是否已赋值的标志存储名

    def __set_name__(self, owner, name):
        self.name = name
        self.storage_name = f"_{name}_{uuid.uuid4().hex[:8]}"
        self._value_set_flag_name = f"_{name}_set"  # 标志位：是否已赋值

    def __get__(self, instance, owner):
        if instance is None:
            return self
        try:
            return getattr(instance, self.storage_name)
        except AttributeError:
            if self.default is not None:
                setattr(instance, self.storage_name, self.default)
                # 自动设置默认值也算“第一次赋值”，之后也会变为只读
                setattr(instance, self._value_set_flag_name, True)
                return self.default
            raise AttributeError(f"必填属性 '{self.name}' 未初始化")

    def __set__(self, instance, value):
        if value is None and self.default is None:
            raise ValueError(f"'{self.name}' 不允许为 None")
        if self.type_hint and not isinstance(value, self.type_hint):
            raise TypeError(f"'{self.name}' 必须是 {self.type_hint}")
        already_set = getattr(instance, self._value_set_flag_name, False)
        # 检查是否已赋值过（如果启用了只读模式）
        if self.readonly_after_first_set:
            if already_set:
                raise AttributeError(f"属性 '{self.name}' 已初始化，只能读取，不能修改")
        setattr(instance, self.storage_name, value)
        setattr(instance, self._value_set_flag_name, True)  # 标记已赋值