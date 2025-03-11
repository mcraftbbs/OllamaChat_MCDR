from mcdreforged.api.all import *
from pathlib import Path
import uuid_api
import os
import json

def tr(key, *args):
    return ServerInterface.get_instance().tr(f"ollamachat.{key}", *args)

class DataManager:
    def __init__(self, source: CommandSource, name: str, config: dict = None):
        uuid_path = './config/ollamachat/uuid.json'
        data_path = './config/ollamachat/data/'
        if not os.path.exists(uuid_path):
            with open(uuid_path, 'w') as file:
                json.dump({}, file)
        with open(uuid_path, 'r') as file:
            uuid_data = json.load(file)
        if name in uuid_data:
            uuid = uuid_data[name]
        else:
            uuid = uuid_api.get_uuid(name)
            uuid_data[name] = uuid
            with open(uuid_path, 'w') as file:
                json.dump(uuid_data, file, indent=2)

        self.config = config if config is not None else {}
        self.source = source
        self.history_path = f"{data_path}{uuid}.json"
        self.system_prompt_path = f"{data_path}{uuid}_system_prompt.json"
        self.prefix_path = f"{data_path}{uuid}_prefix.txt"

        self.initial_system_prompt = [{"role": "system", "content": self.config.get("system_prompt")}]
        os.makedirs(os.path.dirname(self.prefix_path), exist_ok=True)
        if not os.path.exists(self.prefix_path):
            with open(self.prefix_path, 'w') as file:
                file.write(self.config.get("prefix"))

        with open(self.prefix_path, 'r') as file:
            self.prefix = file.read().strip() or self.config.get("prefix")
            with open(self.prefix_path, 'w') as file:
                file.write(self.prefix)

        for path, default in [(self.history_path, []), (self.system_prompt_path, self.initial_system_prompt)]:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            if not os.path.exists(path):
                with open(path, 'w') as file:
                    json.dump(default, file)

    def records(self):
        with open(self.history_path, 'r') as file:
            messages = json.load(file)
        history = "\n--- Records ---\n"
        for i, msg in enumerate(messages):
            history += f"#{i}: {msg['role']}: {msg['content']}\n"
        history += "--- End ---\n"
        self.source.reply(history)

    def reset(self):
        with open(self.history_path, 'w') as file:
            json.dump([], file)
        self.source.reply(tr("records.reset"))

    def add_message(self, role: str, content: str):
        with open(self.system_prompt_path, 'r') as file:
            system_prompt = json.load(file)
        with open(self.history_path, 'r') as file:
            messages = json.load(file)
        messages.append({"role": role, "content": content})
        with open(self.history_path, 'w') as file:
            json.dump(messages, file)
        return system_prompt + messages

    def setup(self, system_prompt: str):
        with open(self.system_prompt_path, 'w') as file:
            json.dump([{"role": "system", "content": system_prompt}], file)
        self.source.reply(tr("setup.done"))

    def label(self, prefix: str):
        self.prefix = f'§a[{prefix}]§r'
        with open(self.prefix_path, 'w') as file:
            file.write(self.prefix)
        self.source.reply(tr("label.set"))

    def init_system(self):
        with open(self.system_prompt_path, 'w') as file:
            json.dump(self.initial_system_prompt, file)
        self.source.reply(tr("setup.init"))

    def get_label(self):
        self.source.reply(f"{tr('label.current')} {self.prefix}")

    def get_setup(self):
        with open(self.system_prompt_path, 'r') as file:
            system_prompt = json.load(file)
        content = system_prompt[0].get("content", "") if system_prompt and isinstance(system_prompt, list) else ""
        self.source.reply(f"{tr('setup.current')} {content}" if content else tr("error.no_setup"))


