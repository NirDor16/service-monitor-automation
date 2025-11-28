from pathlib import Path
import yaml


def load_config() -> dict:
    """
    Load the config.yaml file located in the monitor package.
    Returns a dictionary containing all configuration values.
    If the file is missing, empty, or invalid, an empty dict is returned.
    """
    config_path = Path(__file__).resolve().parent / "config.yaml"

    if not config_path.exists():
        return {}

    with config_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    # Ensure the result is always a dictionary
    if not isinstance(data, dict):
        return {}

    return data
