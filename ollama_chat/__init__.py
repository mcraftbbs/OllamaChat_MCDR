from mcdreforged.api.all import *
from .api import send_to_ollama, send_to_openai
from .data_manager import DataManager
from .config_manager import ConfigManager

def tr(key, *args):
    """翻译函数，获取本地化文本"""
    return ServerInterface.get_instance().tr(f"ollamachat.{key}", *args)

class Plugin:
    def __init__(self, server: ServerInterface):
        self.server = server
        self.config_manager = ConfigManager(server)
        self.config = self.config_manager.load_config()

    def register_commands(self):
        """注册插件命令"""
        builder = SimpleCommandBuilder()

        commands = [
            ("!!oc guide", self.show_guide, 0),  # 所有人可访问
            ("!!oc records", self.view_records, 0),
            ("!!oc reset", self.clear_records, 1),
            ("!!oc restore", self.restore_prompt, 2),
            ("!!oc chat <message>", self.send_chat, 0),
        ]

        for cmd, func, level in commands:
            builder.command(cmd, func)
            builder.literal(cmd.split()[1]).requires(Requirements().has_permission(level))

        builder.arg("message", GreedyText)
        builder.register(self.server)

    def on_load(self, old_module):
        """插件加载时执行"""
        self.register_commands()

    def player_required(self, source: CommandSource) -> bool:
        """检查是否为玩家"""
        if not source.is_player:
            source.reply(tr("player_only"))
            return False
        return True

    def show_guide(self, source: CommandSource):
        """显示帮助信息"""
        source.reply(tr("guide_message"))

    @new_thread
    def send_chat(self, source: CommandSource, context: CommandContext):
        """与 AI 对话"""
        if not self.player_required(source):
            return
        message = context["message"]
        data = DataManager(source, source.player, self.config)
        messages = data.append_message("user", message)
        try:
            response = (
                send_to_ollama(messages, self.config)
                if "ollama" in self.config["ollama_base_url"]
                else send_to_openai(messages, self.config)
            )
            source.reply(f"{data.prefix} {response}")
            data.append_message("assistant", response)
        except Exception as e:
            source.reply(f"{tr('error.api_failed')} {e}")

    def view_records(self, source: CommandSource):
        """查看聊天记录"""
        if not self.player_required(source):
            return
        DataManager(source, source.player, self.config).show_records()

    def clear_records(self, source: CommandSource):
        """清空聊天记录"""
        if not self.player_required(source):
            return
        DataManager(source, source.player, self.config).clear_records()

    def restore_prompt(self, source: CommandSource):
        """恢复默认 AI 预设"""
        if not self.player_required(source):
            return
        DataManager(source, source.player, self.config).restore_prompt()

def on_load(server: ServerInterface, old_module):
    plugin = Plugin(server)
    plugin.on_load(old_module)
