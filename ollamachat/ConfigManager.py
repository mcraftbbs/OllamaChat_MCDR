from mcdreforged.api.all import *
from pathlib import Path
from typing import Dict, Any
import os
import json

def tr(key, *args):
    return ServerInterface.get_instance().tr(f"ollamachat.{key}", *args)

class ConfigManager:
    def __init__(self, server: ServerInterface):
        self.server = server
        self.config_path = Path(self.server.get_data_folder()) / 'config.json'
        self.config: Dict[str, Any] = {}
        self.default_config = {
            "api_key": "",  # 用于 OpenAI 或其他需要密钥的 API
            "ollama_base_url": "http://localhost:11434",  # 默认 Ollama 本地地址
            "openai_base_url": "https://api.openai.com/v1",
            "model": "llama3",  # 默认使用 Ollama 的 llama3 模型
            "system_prompt": "你是一个Minecraft助手，负责回答玩家的相关问题.",
            "prefix": "§a[OllamaChat]§r",
            "permission": {
                "guide": 1,
                "records": 1,
                "reset": 1,
                "setup": 1,
                "label": 1,
                "init setup": 1,
                "chat": 1
            }
        }
        self._ensure_config()

    def _ensure_config(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        if not self.config_path.exists():
            self.save_config(self.default_config)
            self.server.logger.warning(tr("create_config"), self.config_path)

    def load_config(self) -> Dict[str, Any]:
        if self.check_config_when_running():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                return self.config
        return self.default_config

    def save_config(self, config: Dict[str, Any]):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def check_config_when_running(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            self.config = json_data
            required_keys = {
                "api_key": "API Key",
                "ollama_base_url": "Ollama Base URL",
                "openai_base_url": "OpenAI Base URL",
                "model": "Model",
                "system_prompt": "System Prompt",
                "prefix": "Prefix"
            }
            for key, name in required_keys.items():
                if not json_data.get(key):
                    self.server.logger.error(f"{tr('error.check_empty')} {name}, {tr('error.please_check_config')}")
                    return False
            return True
        except Exception as e:
            self.server.logger.error(f"{tr('error.config_error')} {e}")
            return False

