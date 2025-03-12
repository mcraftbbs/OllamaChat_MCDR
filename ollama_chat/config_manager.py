from mcdreforged.api.all import *
from pathlib import Path
import json

def tr(key, *args):
    return ServerInterface.get_instance().tr(f"ollamachat.{key}", *args)

class ConfigManager:
    DEFAULT_CONFIG = {
        "api_key": "",
        "ollama_base_url": "http://localhost:11434",
        "openai_base_url": "https://api.openai.com/v1",
        "model": "llama3",
        "system_prompt": "You are a helpful Minecraft assistant.",
        "prefix": "§a[AI]§r"
    }

    def __init__(self, server: ServerInterface):
        self.server = server
        self.config_path = Path(server.get_data_folder()) / "config.json"
        self.config = self.load_config()

    def load_config(self) -> dict:
        """加载配置文件"""
        if not self.config_path.exists():
            self.save_config(self.DEFAULT_CONFIG)
            self.server.logger.info(tr("config_created"))
            return self.DEFAULT_CONFIG

        try:
            with self.config_path.open("r", encoding="utf-8") as f:
                config = json.load(f)
                if self._validate_config(config):
                    return config
                raise ValueError("Invalid config format")
        except Exception as e:
            self.server.logger.error(f"{tr('error.config_error')} {e}")
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG

    def save_config(self, config: dict):
        """保存配置文件"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with self.config_path.open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def _validate_config(self, config: dict) -> bool:
        """验证配置文件"""
        required = {"api_key", "ollama_base_url", "openai_base_url", "model", "system_prompt", "prefix"}
        if not all(key in config for key in required):
            self.server.logger.error(tr("error.missing_keys"))
            return False
        return True
