from openai import OpenAI
import requests

def send_to_ollama(messages: list, config: dict) -> str:
    """调用 Ollama API"""
    response = requests.post(
        f"{config['ollama_base_url']}/api/chat",
        json={"model": config["model"], "messages": messages, "stream": False},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]

def send_to_openai(messages: list, config: dict) -> str:
    """调用 OpenAI API"""
    client = OpenAI(api_key=config["api_key"], base_url=config["openai_base_url"])
    response = client.chat.completions.create(
        model=config["model"], messages=messages, stream=False
    )
    return response.choices[0].message.content
