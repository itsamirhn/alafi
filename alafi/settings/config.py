import os
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Self, cast

from dcloader import Loader, Source
from dcloader.source import EnvSource, YAMLSource


@dataclass
class Database:
    name: str = "postgres"
    user: str = "postgres"
    password: str = "password"
    host: str = "localhost"
    port: int = 5432


@dataclass
class Authentication:
    key: str = "some_key"
    ttl: timedelta = timedelta(days=30)


@dataclass
class Config:
    secret_key: str
    debug: bool = False
    allowed_hosts: list[str] = field(default_factory=lambda: ["localhost", "127.0.0.1"])
    database: Database = field(default_factory=Database)

    authentication: Authentication = field(default_factory=Authentication)

    @classmethod
    def load(cls: type[Self]) -> Self:
        sources: list[Source] = [EnvSource("ALAFI")]

        config_file_path = os.environ.get("ALAFI_CONFIG_FILE_PATH")
        if config_file_path:
            sources.append(YAMLSource(config_file_path))

        loader = Loader(sources)
        return cast(Self, loader.load(cls))
