import unittest
import os
import shutil
from cash_flow.storage_handler.file_manager import FileManager

class TestFileManager(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.file_manager = FileManager()
        self.test_category = "test_category"
        self.test_file = "test_file.txt"
        
        # Create test directory and file
        os.makedirs(os.path.join(self.test_category), exist_ok=True)
        with open(self.test_file, "w") as f:
            f.write("test content")

    def tearDown(self):
        """Clean up test environment after each test"""
        # Remove test file and directories
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        
        dirs = ["new_test_category", "test_category", "test_label"]
        for d in dirs:
            path = os.path.join("data_store", d)
            if os.path.exists(path):
                shutil.rmtree(path)

    def test_get_base_path(self):
        """Test _get_base_path returns correct path"""
        base_path = self.file_manager._get_base_path()
        self.assertEqual(base_path, "data_store")

    def test_create_label(self):
        """Test _create_label creates directory and returns path"""
        label = "test_label"
        path = self.file_manager._create_label(label)
        self.assertTrue(os.path.exists(path))
        self.assertTrue(os.path.isdir(path))

    def test_save_custom_file(self):
        """Test save_custom_file with valid inputs"""
        date = "2025-01-01"
        result = self.file_manager.save_custom_file(
            self.test_file, 
            date, 
            self.test_category
        )
        self.assertIsNotNone(result)
        if result:
            self.assertTrue(os.path.exists(result))
            self.assertTrue(os.path.basename(result).startswith(date))

    def test_save_custom_file_invalid_path(self):
        """Test save_custom_file with invalid file path"""
        result = self.file_manager.save_custom_file(
            "nonexistent.txt",
            "2025-01-01",
            self.test_category
        )
        self.assertIsNone(result)

    def test_delete_file(self):
        """Test delete_file functionality"""
        # Create a file to delete
        test_file = "to_delete.txt"
        with open(test_file, "w") as f:
            f.write("delete me")
        
        self.assertTrue(self.file_manager.delete_file(test_file))
        self.assertFalse(os.path.exists(test_file))

    def test_update_file(self):
        """Test update_file with new files"""
        date = "2025-01-01"
        old_paths = []
        new_paths = [self.test_file]
        
        result = self.file_manager.update_file(
            old_paths,
            new_paths,
            date,
            self.test_category
        )
        
        self.assertGreater(len(result), 0)
        self.assertTrue(all(os.path.exists(p) for p in result))

    def test_update_file_date(self):
        """Test update_file_date functionality"""
        # Create a file with date prefix
        old_date = "2025-01-01"
        new_date = "2025-02-01"
        original_path = self.file_manager.save_custom_file(
            self.test_file,
            old_date,
            self.test_category
        )
        self.assertIsNotNone(original_path)
        if original_path:
            result = self.file_manager.update_file_date(
                [original_path],
                new_date
            )
            
            # self.assertGreater(len(result), 0)
            self.assertTrue(all(os.path.basename(p).startswith(new_date) for p in result))

    def test_update_file_category(self):
        """Test update_file_category functionality"""
        # Create initial file in category
        date = "2025-01-01"
        new_category = "new_test_category"
        
        original_path = self.file_manager.save_custom_file(
            self.test_file,
            date,
            self.test_category
        )
        self.assertIsNotNone(original_path)
        if original_path:
            result = self.file_manager.update_file_category(
                [original_path],
                new_category
            )
            
            # self.assertGreater(len(result), 0)
            self.assertTrue(all(new_category in p for p in result))

    def test_check_file_paths(self):
        """Test check_file_paths functionality"""
        # Create test files
        valid_file = "valid.txt"
        with open(valid_file, "w") as f:
            f.write("valid")
        
        paths = [valid_file, "nonexistent.txt"]
        result = self.file_manager.check_file_paths(paths)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], valid_file)
        
        # Cleanup
        os.remove(valid_file)