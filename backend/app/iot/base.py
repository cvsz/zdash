from abc import ABC, abstractmethod


class IoTAdapterBase(ABC):
    @abstractmethod
    def power_cycle(self, confirmation: bool = False) -> dict:
        raise NotImplementedError
