import yaml
import os
from dotenv import load_dotenv

load_dotenv()

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "openai_config.yaml")

    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config

config = load_config()
