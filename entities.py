from typing import Callable, Optional
import json


class DynamicSettings:
    def __init__(self, name: str, enabled: bool = True, description: Optional[str] = None):
        self.name = name
        self.enabled = enabled
        self.description = description

    def to_dict(self):
        return {
            "name": self.name,
            "enabled": self.enabled,
            "description": self.description
        }

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)


class DynamicFunction:
    def __init__(self, func: Callable, settings: DynamicSettings):
        self.func = func
        self.settings = settings

    def to_dict(self):
        return {
            "func_name": self.func.__name__,
            "settings": self.settings.to_dict()
        }

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)