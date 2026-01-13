import os
import re
import yaml
import threading
from fastfeishu.models.feishu_cfg import *
from pathlib import Path
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)
from typing import Dict, Any, Type, Tuple

DEFAULT_YAML = Path(__file__).parent / "properties.yaml"
# 用户可覆盖：环境变量 > 用户家目录 > 内置
USER_CONFIG = Path(os.getenv("FEISHU_CONFIG", "")).expanduser().resolve()
if not USER_CONFIG.is_file():
    USER_CONFIG = Path.home() / ".feishu" / "config.yaml"

CONFIG_FILE = USER_CONFIG if USER_CONFIG.is_file() else DEFAULT_YAML

class MissingEnvVarError(RuntimeError):
    """环境变量未配置且没有默认值"""

# ---------- 2. 自定义 YAML 源 ----------
class YamlEnvSettingsSource(PydanticBaseSettingsSource):
    """支持 ${VAR:-default} 的 YAML 文件源"""
    def __init__(self, settings_cls: Type[BaseSettings], yaml_path: str):
        self.yaml_path = Path(yaml_path)
        super().__init__(settings_cls)

    def get_field_value(self, field, field_name: str) -> Tuple[Any, str, bool]:
        # 返回 (值, 字段名, 是否发现)
        data = self._load()
        return data.get(field_name), field_name, field_name in data

    def __call__(self) -> Dict[str, Any]:
        # 提供给 pydantic-settings 的整颗子树
        return self._load()

    # ---------- 公共辅助 ----------
    def _load(self) -> Dict[str, Any]:
        if not self.yaml_path.exists():
            return {}
        text = self.yaml_path.read_text(encoding="utf-8")
        # 替换 ${VAR:-default}
        text = re.sub(r"\$\{([^}]+)\}", self._repl, text)
        return yaml.safe_load(text) or {}

    def _repl(self, match: re.Match[str]) -> str:
        expr = match.group(1)
        var, sep, default = expr.partition(":-")
        value = os.getenv(var)
        if value is not None:
            return value
        if sep:                       # 有默认值
            return default
        raise RuntimeError(f"环境变量 '{var}' 未配置且未提供默认值")

class Settings(BaseSettings):
    """根 Settings，只负责把 feishu 节点挂进来"""
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",  # 支持 FEISHU__LINKS__SHEETS__TARGET=xxx 环境变量覆盖 yaml 配置
    )

    feishu: FeishuSettings

    # ---------- 4. 把 YAML 源塞进加载链 ----------
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,  # 1. 构造参数
            env_settings,  # 2. 系统环境变量
            dotenv_settings,  # 3. .env
            YamlEnvSettingsSource(settings_cls, CONFIG_FILE),  # 4. YAML+${}
            file_secret_settings,  # 5. secrets
        )

# ---------- 5. 全局单例 ----------
_lock = threading.Lock()
feishu_property: Settings | None = None      # 只是类型注解，**没有赋值**

def get_feishu_property() -> Settings:
    global feishu_property
    if feishu_property is None:
        with _lock:                       # 防止多线程同时 new
            if feishu_property is None:   # 双重检查
                feishu_property = Settings()
    return feishu_property

if __name__ == '__main__':
    print(get_feishu_property().feishu.links.sheets.metainfo.url)