from dataclasses import dataclass, field, asdict
import json
from pathlib import Path

CONFIG_FILE = "config.json"

@dataclass
class CustomConfig:
    category: list[str] = field(default_factory=list)

    @staticmethod
    def load(file_path: str = CONFIG_FILE) -> "CustomConfig":
        """
        Load configuration from JSON file or create default config it if missing.
        """
        if not Path(file_path).exists():
            print(f"Config file '{file_path}' not found. Creating default config.")
            default_list = [
                # necessities
                "home",
                "food_groceries",
                "healthcare",
                "gym_fitness",
                "phone",
                "transportation",
                "clothing",

                # extras
                "subscriptions",
                "dining_out",
                "entertainment",
                "gifts",
                "travel_vacation",
                "culture",
                "personal_care",
                "other_extra",

                # income
                "salary",
                "other_income"
            ]
            default_config = CustomConfig(category=default_list)
            default_config.save(file_path)
            return default_config
        
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return CustomConfig(**data)
    
    def save(self, file_path: str = CONFIG_FILE):
        """Save configuration to JSON file."""
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(asdict(self), file, indent=4)
            print(f"Config saved to '{file_path}'")

