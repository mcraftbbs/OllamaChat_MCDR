from mcdreforged.api.all import *
from pathlib import Path
import uuid_api
import json

def tr(key, *args):
    return ServerInterface.get_instance().tr(f"ollamachat.{key}", *args)

class DataManager:
    def __init__(self, source: CommandSource, player: str, config: dict):
        self.source = source
        self.config = config
        self.data_dir = Path("./config/ollamachat/data")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 获取或生成 UUID
        uuid_file = self.data_dir.parent / "uuid.json"
        uuid_file.touch()
        with uuid_file.open("r+", encoding="utf-8") as f:
            uuids = json.load(f) if f.readable() and f.tell() > 0 else {}
            f.seek(0)
            self.uuid = uuids.get(player) or uuid_api.get_uuid(player)
            if player not in uuids:
                uuids[player] = self.uuid
                json.dump(uuids, f, indent=2)

        # 文件路径
        self.chat_file = self.data_dir / f"{self.uuid}_chat.json"
        self.prompt_file = self.data_dir / f"{self.uuid}_prompt.json"
        self.prefix = config.get("prefix", "§a[AI]§r")

        # 初始化文件
        self._init_file(self.chat_file, [])
        self._init_file(self.prompt_file, [{"role": "system", "content": config.get("system_prompt", "")}])

    def _init_file(self, path: Path, default: list):
        """初始化数据文件"""
        path.touch()
        if path.stat().st_size == 0:
            with path.open("w", encoding="utf-8") as f:
                json.dump(default, f, indent=2)

    def append_message(self, role: str, content: str) -> list:
        """添加消息到历史记录"""
        with self.prompt_file.open("r", encoding="utf-8") as f:
            prompt = json.load(f)
        with self.chat_file.open("r+", encoding="utf-8") as f:
            messages = json.load(f)
            messages.append({"role": role, "content": content})
            f.seek(0)
            json.dump(messages, f, indent=2)
        return prompt + messages

    def show_records(self):
        """显示聊天记录"""
        with self.chat_file.open("r", encoding="utf-8") as f:
            messages = json.load(f)
        if not messages:
            self.source.reply(tr("records.empty"))
            return
        output = "\n§7=== Chat History ===§r\n"
        for i, msg in enumerate(messages, 1):
            output += f"§6#{i} {msg['role']}:§r {msg['content']}\n"
        output += "§7=== End ===§r"
        self.source.reply(output)

    def clear_records(self):
        """清空聊天记录"""
        with self.chat_file.open("w", encoding="utf-8") as f:
            json.dump([], f, indent=2)
        self.source.reply(tr("records.reset"))

    def restore_prompt(self):
        """恢复默认系统提示"""
        default_prompt = [{"role": "system", "content": self.config.get("system_prompt", "")}]
        with self.prompt_file.open("w", encoding="utf-8") as f:
            json.dump(default_prompt, f, indent=2)
        self.source.reply(tr("setup.init"))
