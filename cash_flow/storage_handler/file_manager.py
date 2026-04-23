import logging
import shutil
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


class FileManager:
    def __init__(self, path: str = "data_store"):
        self.path = path

    def _get_base_path(self) -> str:
        """Return the path to the folder where the script or executable is located."""
        if getattr(sys, "frozen", False):
            application_path = Path(sys.executable).parent
        else:
            # If running as a script, sys.argv[0] is the main script path.
            # application_path = os.path.dirname(os.path.abspath(sys.argv[0]))
            application_path = Path(self.path)
        return str(application_path)

    def _create_label(self, label: str) -> str:
        """
        Creates the folder if it does not exist,
        supports intermediate directories (e.g., dir/dir_in),
        and returns the folder path.
        """
        base_path = Path(self._get_base_path())
        target_folder = base_path / label
        target_folder.mkdir(parents=True, exist_ok=True)
        return str(target_folder)

    def save_custom_file(self, file_path: str, date: str, dir_label: str) -> str | None:
        """Saves a copy of a file to a specific directory with a date prefix.

        Args:
            file_path (str): The absolute or relative path to the source file.
            date (str): The date string (e.g., 'YYYY-MM-DD') to prepend to the filename.
            dir_label (str): The name of the subdirectory within the data store
                             where the file will be saved.

        Returns:
            The full path to the newly saved file if successful, otherwise None.
        """

        path = Path(file_path)
        if not path.is_file():
            logger.error(f"File '{file_path}' does not exist.")
            return None

        dir_path = Path(self._create_label(dir_label))

        # Check if the date is valid
        if not date:
            logger.error("Date is empty or invalid.")
            return None

        # Rename the file with the date in y/m/d format
        new_file_name = f"{date}-{path.name}"
        new_file_path = dir_path / new_file_name

        # Copy the file to the folder, overwrite if it already exists
        try:
            shutil.copy2(file_path, new_file_path)  # copy2 preserves metadata
            logger.info(
                f"File '{path.name}' saved as '{new_file_name}' in '{dir_path}'."
            )
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            return None

        return str(new_file_path)

    def delete_file(self, file_path: str) -> bool:
        """
        Deletes the specified file if it exists.
        Returns True if the file was deleted, False otherwise.
        """
        path = Path(file_path)
        if path.is_file():
            try:
                path.unlink()
                logger.info(f"File '{file_path}' deleted successfully.")
                return True
            except Exception as e:
                logger.error(f"Error deleting file: {e}")
                return False
        else:
            logger.warning(f"File '{file_path}' does not exist.")
            return False

    def update_file(
        self,
        old_file_paths: list[str],
        new_file_paths: list[str],
        date: str,
        dir_label: str,
    ) -> list[str]:
        """
        Updates the file paths.

        If the previous files are no longer valid, they must be deleted manually.
        """
        for file_path in new_file_paths:
            temp_file_path = self.save_custom_file(file_path, date, dir_label)
            if temp_file_path is not None:
                old_file_paths.append(temp_file_path)
        return old_file_paths

    def update_file_date(self, file_paths: list[str], date: str) -> list[str]:
        """
        Updates the date prefix in the filenames of the given files.

        Args:
            file_paths: List of paths to files to update
            date: New date string to use as prefix (format: YYYY-MM-DD)

        Returns:
            List of new file paths after renaming, empty list if any error occurs
        """
        new_file_paths: list[str] = []

        for file_path in file_paths:
            path = Path(file_path)

            if not path.is_file():
                logger.error(f"File '{file_path}' does not exist.")
                return []

            # Get filename without the date prefix (skip first 10 characters: YYYY-MM-DD-)
            original_name = path.name[10:]
            new_name = f"{date}{original_name}"
            # Create new path object with the new name
            new_path = path.parent / new_name

            try:
                path.rename(new_path)
                new_file_paths.append(str(new_path))
            except Exception as e:
                logger.error(f"Error renaming file {path}: {e}")
                return []

        return new_file_paths

    def update_file_category(self, file_paths: list[str], dir_label: str) -> list[str]:
        """
        Moves files to a different category folder while maintaining the same filename.

        Args:
            file_paths: List of paths to files to move
            dir_label: New category folder name

        Returns:
            List of new file paths after moving, empty list if any error occurs
        """
        new_file_paths: list[str] = []

        for file_path in file_paths:
            path = Path(file_path)

            if not path.is_file():
                logger.error(f"File '{file_path}' does not exist.")
                return []

            self._create_label(dir_label)

            path_new = Path(path.parent.parent / dir_label / path.name)
            try:
                path.rename(path_new)
            except Exception as e:
                logger.error(f"Error moving file {path}: {e}")
                return []
            new_file_paths.append(str(path_new))

        return new_file_paths

    def check_file_paths(self, file_paths: list[str]) -> list[str]:
        """
        Verifies if files in file_paths exist and returns a list of valid paths.
        Returns an empty list if no valid files are found.
        """
        if not file_paths:
            return []

        valid_paths: list[str] = []
        for file_path in file_paths:
            path = Path(file_path)
            if path.exists():
                valid_paths.append(str(path))
            else:
                logger.warning(f"Warning: File not found: {file_path}")

        return valid_paths
