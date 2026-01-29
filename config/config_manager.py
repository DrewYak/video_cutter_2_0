import json
from pathlib import Path


class ConfigManager:
    def __init__(self):
        self.config_dir = Path(__file__).parent
        self.default_config_path = self.config_dir / "default_config.json"
        self.user_config_path = self.config_dir / "config.json"

        self._config = self._load()

    def _load(self) -> dict:
        if self.user_config_path.exists():
            try:
                with open(self.user_config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return self._load_default()

    def _load_default(self) -> dict:
        with open(self.default_config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self):
        with open(self.user_config_path, "w", encoding="utf-8") as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)

    def reset_to_default(self):
        self._config = self._load_default()
        self.save()

    def get(self, *keys, default=None):
        data = self._config
        for key in keys:
            if not isinstance(data, dict) or key not in data:
                return default
            data = data[key]
        return data

    def set(self, value, *keys):
        data = self._config
        for key in keys[:-1]:
            data = data.setdefault(key, {})
        data[keys[-1]] = value
        self.save()
