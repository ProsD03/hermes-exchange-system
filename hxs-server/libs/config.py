import toml
from pydantic import BaseModel, Field
import os


class AuthConfig(BaseModel):
    auth_required: bool = Field(default=False)


class ServerConfig(BaseModel):
    bind_ip: str = Field(default='127.0.0.1')
    bind_port: int = Field(default=1303)


class Config(BaseModel):
    auth: AuthConfig = Field(default_factory=AuthConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)

    def load_config(self, path: str):
        if not os.path.exists(path):
            print("No Path")
            return False
        try:
            toml_file = toml.load(path)
            for key in toml_file.keys():
                if key not in self.__dict__.keys():
                    return False
                else:
                    for subkey in toml_file[key]:
                        if subkey not in self.__dict__[key].__dict__.keys():
                            return False
                        else:
                            self.__dict__[key].__dict__[subkey] = toml_file[key][subkey]
            return True
        except (toml.TomlDecodeError, IOError, TypeError):
            print("Not TOML")
            return False


config = Config()
