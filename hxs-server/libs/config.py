import toml
from pydantic import BaseModel, Field


class Config(BaseModel):
    auth_required: bool = Field(default=False)
    bind_ip: str = Field(default='127.0.0.1')
    bind_port: int = Field(default=1303)

    def load_config(self, path: str):
        return False


config = Config()
