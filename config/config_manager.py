# config/config_manager.py

import json
import copy
from pathlib import Path
from config.default_config import DEFAULT_CONFIG

CONFIG_PATH = Path("config/config.json")


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        save_config(DEFAULT_CONFIG)
        return copy.deepcopy(DEFAULT_CONFIG)

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            user_config = json.load(f)
    except Exception:
        save_config(DEFAULT_CONFIG)
        return copy.deepcopy(DEFAULT_CONFIG)

    return merge_with_defaults(user_config)


def save_config(config: dict):
    CONFIG_PATH.parent.mkdir(exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def reset_to_defaults():
    save_config(DEFAULT_CONFIG)


def merge_with_defaults(user_config: dict) -> dict:
    result = copy.deepcopy(DEFAULT_CONFIG)

    def recursive_update(dst, src):
        for key, value in src.items():
            if isinstance(value, dict) and key in dst:
                recursive_update(dst[key], value)
            else:
                dst[key] = value

    recursive_update(result, user_config)
    return result
