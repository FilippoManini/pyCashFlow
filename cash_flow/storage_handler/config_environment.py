from dataclasses import asdict, dataclass, field
from pathlib import Path
import json

CONFIG_FILE = "config.json"


@dataclass
class CustomConfig:
    """Configuration class for handling application settings."""

    category: list[str] = field(default_factory=list)

    @staticmethod
    def load(file_path: str = CONFIG_FILE) -> "CustomConfig":
        """Loads configuration from a JSON file or creates a default one if missing.

        Args:
            file_path: Path to the JSON configuration file.

        Returns:
            An instance of CustomConfig.
        """
        if not Path(file_path).exists():
            print(f"Config file '{file_path}' not found. Creating default config.")
            default_list = [
                "home",
                "food_groceries",
                "healthcare",
                "gym_fitness",
                "phone",
                "transportation",
                "clothing",
                "subscriptions",
                "dining_out",
                "entertainment",
                "gifts",
                "travel_vacation",
                "culture",
                "personal_care",
                "other_extra",
                "salary",
                "other_income",
            ]
            default_config = CustomConfig(category=default_list)
            default_config.save(file_path)
            return default_config

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return CustomConfig(**data)

    def save(self, file_path: str = CONFIG_FILE):
        """Saves configuration to a JSON file.

        Args:
            file_path: Path to the JSON configuration file.
        """
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(asdict(self), file, indent=4)
            print(f"Config saved to '{file_path}'")
