# OllamaChat

[The officially developed OllamaChat plugin MCDR version]

📜 LICENSE: **GNU GPLv3** [![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A Minecraft server plugin for MCDReforged that enables players to chat with AI using either Ollama or OpenAI.

## 📦 Dependencies
- Main Dependency: [MCDReforged](https://github.com/MCDReforged/MCDReforged) v2.x
- *Required Dependency*: [uuid_api](https://github.com/AnzhiZhang/MCDReforgedPlugins/tree/master/src/uuid_api) (GPLv3)

## Features
- Chat with AI directly in Minecraft.
- Supports both Ollama (local) and OpenAI (API) backends.
- Customizable AI label and setup prompts.
- View and reset chat history.

## Installation
1. Ensure [MCDReforged](https://github.com/MCDReforged/MCDReforged) is installed on your server.
2. Install required Python dependencies:
   ```bash
   pip install openai requests
   ```
3. Place the plugin files in the `plugins` folder of your MCDReforged server.
4. Restart the server to generate the default configuration.

## Configuration
Edit `config/ollamachat/config.json` to configure the plugin:
- `"api_key"`: Your OpenAI API key (leave empty for Ollama).
- `"ollama_base_url"`: URL for Ollama (default: `http://localhost:11434`).
- `"openai_base_url"`: URL for OpenAI (default: `https://api.openai.com/v1`).
- `"model"`: AI model (e.g., `llama3` for Ollama).
- `"system_prompt"`: Default AI behavior prompt.
- `"prefix"`: Chat prefix displayed in-game.

Example `config.json`:
```json
{
  "api_key": "",
  "ollama_base_url": "http://localhost:11434",
  "openai_base_url": "https://api.openai.com/v1",
  "model": "llama3",
  "system_prompt": "You are a Minecraft assistant helping players with game-related questions.",
  "prefix": "§a[OllamaChat]§r",
  "permission": {
    "guide": 1,
    "records": 1,
    "reset": 1,
    "setup": 1,
    "label": 1,
    "init system": 1,
    "chat": 1
  }
}
```

## Commands
All commands are prefixed with `!!oc` and can only be used by players.

| Command                | Description                     | Example                |
|-----------------------|--------------------------------|-----------------------|
| `!!oc guide`          | Show this command guide        | `!!oc guide`          |
| `!!oc label`          | View current AI label          | `!!oc label`          |
| `!!oc label <label>`  | Set a new AI label (max 8 chars) | `!!oc label Bot`    |
| `!!oc records`        | View chat history              | `!!oc records`        |
| `!!oc reset`          | Clear chat history             | `!!oc reset`          |
| `!!oc setup`          | View current AI setup prompt   | `!!oc setup`          |
| `!!oc setup <setup>`  | Set a new AI setup prompt      | `!!oc setup Helper`   |
| `!!oc init system`    | Reset AI setup to default      | `!!oc init system`    |
| `!!oc chat <message>` | Chat with the AI               | `!!oc chat Hi`        |

## Permissions
Permissions are configurable in `config.json` under `"permission"`. Default level is `1` for all commands.

## Support
- Report issues or suggest features on GitHub/[community server](https://chat.sarskin.cn/invite/iHgI6LTX)..
