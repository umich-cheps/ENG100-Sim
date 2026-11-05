import logging
import yaml
from simu_core import SimuCore
from simu_core import RandomVariable
from simu_core.file_util import file_util
from simu_core.exceptions import ValidationException 

logger = logging.getLogger(__name__)


class ParseModule:
    def __init__(self, sim_core: SimuCore):
        self.sim_core = sim_core

    def execute(self):
        self.parse_stopping_criteria()
        self.parse_distributions()
        self.sim_core.custom_parsing()

        self.sim_core.validate_input()

    def parse_stopping_criteria(self):
        """Parse and set replication and simululation stopping criteria"""
        self.sim_core.replication_stopping_criteria = self.sim_core.gen_params_dict[
            'replication_stopping_criteria']
        if self.sim_core.replication_stopping_criteria == "num_epochs":
            self.sim_core.replication_stopping_threshold = self.sim_core.gen_params_dict[
                'num_epochs']
            
        self.sim_core.simulation_stopping_criteria = self.sim_core.gen_params_dict[
            'simulation_stopping_criteria']
        if (self.sim_core.simulation_stopping_criteria == "num_replications" 
                or self.sim_core.simulation_stopping_criteria == "execution_time"):
            self.sim_core.simulation_stopping_threshold =  self.sim_core.gen_params_dict[
                self.sim_core.simulation_stopping_criteria]
        
        self.sim_core.epoch_duration = self.sim_core.gen_params_dict['epoch_duration']


    def parse_distributions(self):
        for key in self.sim_core.event_params_dict:
            self.sim_core.event_random_variables[key] = RandomVariable(
                        self.sim_core.event_params_dict[key]["distribution"], 
                        self.sim_core.event_params_dict[key])
            
            stopping_criteria_dict = {}
            stopping_criteria_dict['stopping_criteria'] = self.sim_core.event_params_dict[key]["stopping_criteria"]
            if (stopping_criteria_dict['stopping_criteria'] == 'num_trials'):
                stopping_criteria_dict['threshold'] = self.sim_core.event_params_dict[key]['threshold']
                
            self.sim_core.event_type_stopping_criteria[key] = stopping_criteria_dict
    
    def validate_parse(self):
        # assumes Enum is created and passed in to the Module
        
        # Validate gen_params variables
        # Validate whether simulation_stopping_criteria is set
        simulation_stopping_criteria = self.sim_core.gen_params_dict.get('simulation_stopping_criteria')
        if not simulation_stopping_criteria:
            raise ValidationException('simulation_stopping_criteria does not exist in gen_params.txt')

        # Validate the type of the criteria (num_replications, execution_time) exists as a key and is has a number value
        stopping_threshold = self.sim_core.gen_params_dict.get(simulation_stopping_criteria)
        if not stopping_threshold:
            raise ValidationException(f'{simulation_stopping_criteria} does not exist in gen_params.txt')
        try:
            float(stopping_threshold)
        except ValueError:
            raise ValidationException(f'The value mapped to {simulation_stopping_criteria} is not a valid number')

        # Validate whether epoch_duration is set
        epoch_duration = self.sim_core.gen_params_dict.get('epoch_duration')
        if not epoch_duration:
            raise ValidationException('epoch_duration does not exist in gen_params.txt')
        
        # Validate that epoch_duration is a number
        try:
            float(epoch_duration)
        except ValueError:
            raise ValidationException(f'The value mapped to epoch_duration is not a valid number')
        
        # Validate whether replication stopping threshold is set
        replication_stopping_threshold = self.sim_core.get_params_dict.get('replication_stopping_threshold')
        if not replication_stopping_threshold:
            raise ValidationException('replication_stopping_threshold does not exist in gen_params.txt')

        # Validate whether replication stopping threshold is a float
        try:
            float(replication_stopping_threshold)
        except ValueError:
            raise ValidationException(f'The value mapped to replication_stopping_threshold is not a valid number')
        
        
        # Validate whether all EventTypes are in the self.event_params_dict
        for e in self.EventTypes:
            temp = self.event_params_dict.get(e)
            if not temp:
                raise ValidationException(f'{e} is not in event_params.txt')
            
        # Validate distributions allowed by the TD: this file does not exist yet so it is not yet implemented
        
        # Custom validations by the TD
        self.TD_distribution_validation()

    def TD_distribution_validation(self):
        pass