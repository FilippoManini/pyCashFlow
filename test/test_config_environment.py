import os
import unittest

from cash_flow.storage_handler.config_environment import CustomConfig


class TestCustomSetting(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_load_default_config_when_missing(self):
        """Test loading default config when the config file is missing."""
        test_config_file = "test_config.json"
        
        # Ensure the test config file does not exist
        if os.path.exists(test_config_file):
            os.remove(test_config_file)
    
        config = CustomConfig.load()
        
        self.assertIsInstance(config, CustomConfig)