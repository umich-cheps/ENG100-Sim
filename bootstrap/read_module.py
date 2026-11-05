import logging
import yaml
from pathlib import Path
from simu_core import SimuCore
from simu_core.file_util import file_util
from simu_core.exceptions import ValidationException, ConfigurationException

logger = logging.getLogger(__name__)


class ReadModule:
    """Read input parameter files provided by the user."""

    def __init__(self, sim_core: SimuCore, gen_params_path):
        self.sim_core = sim_core
        self.gen_params_path = gen_params_path

    def execute(self):
        """Read the input files and parameters for the simulation."""
        # Validate whether gen_params file exists
        if not Path(self.gen_params_path).is_file():
            raise ConfigurationException(f"The given gen_params path does not exist: {self.gen_params_path}")

        self.sim_core.gen_params_dict = file_util.get_file_map(self.gen_params_path)

        # Validate whether input_file_params and output_file_params keys exist in gen_params.txt
        if 'input_file_params' not in self.sim_core.gen_params_dict:
            raise ValidationException("The key 'input_file_params' does not exist in gen_params.txt")
        if 'output_file_params' not in self.sim_core.gen_params_dict:
            raise ValidationException("The key 'output_file_params' does not exist in gen_params.txt")
        self.sim_core.input_files_dict = self.read_text_file(
            self.sim_core.gen_params_dict, "input_file_params", get_file_locations=True)
        
        self.sim_core.output_files_dict =  self.read_text_file(
            self.sim_core.gen_params_dict, "output_file_params", get_file_locations=True)
        
        self.sim_core.cust_params_dict = self.read_text_file(
            self.sim_core.input_files_dict, "cust_params")
        
        self.sim_core.event_params_dict = self.read_distribution(
            self.sim_core.input_files_dict["event_params"])
        
        self.sim_core.input_file_contents_dict = self.read_nested_files(
            self.sim_core.input_files_dict)

        self.sim_core.read_input()



    def _read_yaml(self, key):
        with open(self.sim_core.file_util.get_file(key), 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
            
    def read_nested_files(self, file_locations_dict):
        """
        Read the contents of every file specified in file_locations_dict
        and return all contents

        Args:
            file_locations_dict: A map of all files to be read with
                filekeys as the keys and the values are the path to the 
                file
        Returns:
            file_content_dict: The contents of each file in a nested
                dict where the key is a filekey and the values are a
                dict of that file's contents.
        """
        file_content_dict = {}
        for key in file_locations_dict:
            file_content_dict[key] = file_util.get_file_map(file_locations_dict[key])
        return file_content_dict

    def read_text_file(self, dict, key, get_file_locations=False):
        """Read a file path from the dictionary and return its contents.
        
        Args:
            dict (dict): The dictionary containing file paths.
            key (str): The key for the file path in the dictionary.

        Returns:
            dict: The contents of the file as a dictionary.

        Raises:
            ValueError: If the key is not found in the dictionary.
        """
        if dict.get(key) is None:
            raise ValidationException(f"{key} is missing from {dict}.")
        
        if get_file_locations:
            return file_util.get_file_locations_map(dict[key])

        return file_util.get_file_map(dict[key])

    def read_distribution(self, file):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                result = {}
                event_dict = {}
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("//"):
                        continue
                    parts = line.split(None, 1)
                    if len(parts) == 2:
                        key, value = parts
                        if value.isdigit():
                            value = int(value)
                        if (key == "event_type" and len(event_dict) != 0):
                            result[self.sim_core.EventTypes[event_dict["event_type"]]] = event_dict
                            event_dict = {}
                        event_dict[key] = value
                    else:
                        logger.warning(f"Skipping malformed line: {line}")
                result[self.sim_core.EventTypes[event_dict["event_type"]]] = event_dict
                return result
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Error: The file '{file}' does not exist.") from e
