from pathlib import Path
import logging
import yaml

logger = logging.getLogger(__name__) 

class FileUtil():

    def check_file_extension(self, file, expected_extension):
        """
        Checks if the file has the expected extension.

        Args:
            file (str): The path to the file.
            expected_extension (str): The expected file extension (e.g., '.txt').

        Returns:
            bool: True if the file has the expected extension, False otherwise.
        """
        return Path(file).suffix == expected_extension

    def get_file_map(self, file):
        """
        Reads a text file containing key-value pairs (space-delimited)
        or a YAML file and returns a mapping of its contents.

        Args:
            file (str): The path to the text or YAML file to read.

        Returns:
            dict: A dictionary mapping keys to values.
        """
        file_ext = Path(file).suffix
        
        if file_ext == '.yaml' or file_ext == '.yml':
            # Handle YAML files
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except FileNotFoundError as e:
                raise FileNotFoundError(
                    f"Error: The file '{file}' does not exist.") from e
        elif file_ext == '.txt':
            # Handle text files (original behavior)
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    result = {}
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("//"):
                            continue
                        parts = line.split(None, 1)
                        if len(parts) == 2:
                            key, value = parts
                            if value.isdigit():
                                value = int(value)
                            result[key] = value
                        else:
                            logger.warning(f"Skipping malformed line: {line}")
                    return result
            except FileNotFoundError as e:
                raise FileNotFoundError(
                    f"Error: The file '{file}' does not exist.") from e
        else:
            raise ValueError(f"File '{file}' has unsupported extension '{file_ext}'. Expected '.txt', '.yaml', or '.yml'.")

    def get_file_locations_map(self, file):
        """
        Reads a text file containing directory paths followed by 
        key-value pairs of file keys and filenames,
        """
        if not self.check_file_extension(file, '.txt'):
            raise ValueError(f"File '{file}' does not have the expected .txt extension.")

        try:
            with open(file, 'r', encoding='utf-8') as f:
                result = {}
                folder_path = ''
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("//"):
                        continue
                    parts = line.split(None, 1)
                    
                    if len(parts) == 1:
                        folder_path = parts[0]
                        if not folder_path.endswith('/'):
                            raise ValueError(
                                f"Folder path '{folder_path}' does not end with a '/'. "
                                "Folder paths must end with a '/' character.")
                        
                    elif len(parts) == 2:
                        key = parts[0]
                        if parts[1].count('.') != 1:
                            raise ValueError(
                                f"Invalid file extension for '{parts[1]}' for key '{key}'. "
                                "File names must contain exactly one '.' character "
                                "to denote a file extension.")
                        value = folder_path + parts[1]
                        result[key] = value
                        
                    else:
                        logger.warning(f"Skipping malformed line: {line}")
                return result
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Error: The file '{file}' does not exist.") from e
        

# Singleton instance of FileUtil        
file_util = FileUtil()