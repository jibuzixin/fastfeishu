from typing import (
    Protocol,
    Generator,
    Union,
    Optional,
    List, Any, Dict)
import pandas as pd
import abc

class FeiShuInterface(abc.ABC):
    @abc.abstractmethod
    def get_header(self) -> List[str]: ...

    @abc.abstractmethod
    def read(self, sheet_range: str) -> List[List[Any]]: ...

    @abc.abstractmethod
    def read_images(self, sheet_range: str) -> List[List[Any]]: ...

    @abc.abstractmethod
    def create_sheet(self, title: str, index: int) -> str: ...

    @abc.abstractmethod
    def insert(self, sheet_range: str, data_list: List[List]): ...  # ?

    @abc.abstractmethod
    def write(self, sheet_range: str, data_list: List[List[Any]]): ...  # ?

    @abc.abstractmethod
    def append(self, sheet_range: str, data_list: List[list], insert_data_option="OVERWRITE"): ...  # ?

    @abc.abstractmethod
    def delete_series_by_index(self, start_index: str | int, end_index: str | int): ...

class IterableSheetProtocol(Protocol):
    def iterrows(
        self,
        start_row: int = 2,
        end_row: Optional[int] = None,
    ) -> Generator[Union[dict[str, Any], pd.Series], None, None]: ...