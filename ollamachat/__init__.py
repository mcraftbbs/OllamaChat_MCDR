from mcdreforged.api.all import *
from openai import OpenAI
import requests
from ollamachat.DataManager import DataManager
from ollamachat.ConfigManager import ConfigManager

def tr(key, *args):
    return ServerInterface.get_instance().tr(f"ollamachat.{key}", *args)

config_manager = None

def register_commands(server: ServerInterface, config: dict):
    builder = SimpleCommandBuilder()
    require = Requirements()
    level_dict = config.get("permission", {})
    builder.command('!!oc guide', show_guide)
    builder.command('!!oc records', view_records)
    builder.command('!!oc reset', clear_records)
    builder.command('!!oc setup', view_setup)
    builder.command('!!oc label', view_label)
    builder.command('!!oc setup <setup>', update_setup)
    builder.command('!!oc label <label>', update_label)
    builder.command('!!oc init setup', init_setup)
    builder.command('!!oc chat <message>', send_chat)

    builder.arg('label', GreedyText)
    builder.arg('message', GreedyText)
    builder.arg('setup', GreedyText)

    for literal in level_dict:
        builder.literal(literal).requires(
            require.has_permission(level_dict[literal]),
            failure_message_getter=lambda err, p=level_dict[literal]: "lack_permission"
        )

    builder.register(server)

def on_load(server: ServerInterface, old_module):
    global config_manager
    config_manager = ConfigManager(server)
    config = config_manager.load_config()
    register_commands(server, config)

def show_guide(source: CommandSource):
    source.reply(tr("guide_message"))

def send_to_ollama(messages: list, config: dict) -> str:
    response = requests.post(
        f"{config['ollama_base_url']}/api/chat",
        json={
            "model": config["model"],
            "messages": messages,
            "stream": False
        }
    )
    return response.json()["message"]["content"]

def send_to_openai(messages: list, config: dict) -> str:
    client = OpenAI(api_key=config["api_key"], base_url=config["openai_base_url"])
    response = client.chat.completions.create(model=config["model"], messages=messages, stream=False)
    return response.choices[0].message.content

@new_thread
def send_chat(source: CommandSource, context: CommandContext):
    if not source.is_player:
        source.reply(tr("only_by_player"))
        return
    message = context['message']
    config = config_manager.load_config()
    player_data = DataManager(source, source.player, config)
    prefix = player_data.prefix
    messages = player_data.add_message("user", message)
    try:
        response = send_to_ollama(messages, config) if "ollama" in config["ollama_base_url"] else send_to_openai(messages, config)
        source.reply(f"{prefix} {response}")
        player_data.add_message("assistant", response)
    except Exception as e:
        source.reply(f"{tr('error.api_failed')} {e}")

def update_setup(source: CommandSource, context: CommandContext):
    if not source.is_player:
        source.reply(tr("only_by_player"))
        return
    DataManager(source, source.player, config_manager.load_config()).setup(context['setup'])

def view_setup(source: CommandSource):
    if not source.is_player:
        source.reply(tr("only_by_player"))
        return
    DataManager(source, source.player, config_manager.load_config()).get_setup()

def update_label(source: CommandSource, context: CommandContext):
    if not source.is_player:
        source.reply(tr("only_by_player"))
        return
    label = context['label']
    if not label:
        source.reply(tr("error.input_label_empty"))
        return
    if len(label) > 8:
        source.reply(tr("error.input_label_too_long"))
        return
    DataManager(source, source.player, config_manager.load_config()).label(label)

def view_label(source: CommandSource):
    if not source.is_player:
        source.reply(tr("only_by_player"))
        return
    DataManager(source, source.player, config_manager.load_config()).get_label()

def view_records(source: CommandSource):
    if not source.is_player:
        source.reply(tr("only_by_player"))
        return
    DataManager(source, source.player, config_manager.load_config()).records()

def clear_records(source: CommandSource):
    if not source.is_player:
        source.reply(tr("only_by_player"))
        return
    DataManager(source, source.player, config_manager.load_config()).reset()

def init_setup(source: CommandSource):
    if not source.is_player:
        source.reply(tr("only_by_player"))
        return
    DataManager(source, source.player, config_manager.load_config()).init_system()

