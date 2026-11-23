"""Holds the classes for the agent configurations"""

from dataclasses import dataclass


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class Config:
    base_url: str
    model: str
    api_key: str = ""
    data_base_url: str = ""
    max_steps: int = 8
