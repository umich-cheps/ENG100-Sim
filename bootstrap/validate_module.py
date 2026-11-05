from simu_core import SimuCore
from simu_core.exceptions import ValidationException
from simu_core.error_manager import ErrorManager

class ValidateModule():
    """Validate parameters provided by the user."""

    def __init__(self, sim_core: SimuCore, error_manager: ErrorManager):
        self.sim_core = sim_core
        self.error_manager = error_manager

    def execute(self):
        # assumes Enum is created and passed in to the Module
        
        # Validate gen_params variables
        # Validate whether simulation_stopping_criteria is set
        simulation_stopping_criteria = self.sim_core.gen_params_dict.get('simulation_stopping_criteria')
        if not simulation_stopping_criteria:
            self.error_manager.add_validation_error(
                ValidationException('simulation_stopping_criteria does not exist in gen_params.txt')
            )
        else:
            # Validate the type of the criteria (num_replications, execution_time) exists as a key and is has a number value
            stopping_threshold = self.sim_core.gen_params_dict.get(simulation_stopping_criteria)
            if not stopping_threshold:
                self.error_manager.add_validation_error(ValidationException(f'{simulation_stopping_criteria} does not exist in gen_params.txt'))
            else:
                try:
                    float(stopping_threshold)
                except ValueError:
                    self.error_manager.add_validation_error(ValidationException(f'The value mapped to {simulation_stopping_criteria} is not a valid number'))

        # Validate whether epoch_duration is set
        epoch_duration = self.sim_core.gen_params_dict.get('epoch_duration')
        if not epoch_duration:
                self.error_manager.add_validation_error(ValidationException('epoch_duration does not exist in gen_params.txt'))
        else:
            # Validate that epoch_duration is a number
            try:
                float(epoch_duration)
            except ValueError:
                self.error_manager.add_validation_error(ValidationException(f'The value mapped to epoch_duration is not a valid number'))
            
        # Validate whether replication stopping threshold is set
        replication_stopping_threshold = self.sim_core.get_params_dict.get('replication_stopping_threshold')
        if not replication_stopping_threshold:
            self.error_manager.add_validation_error(ValidationException('replication_stopping_threshold does not exist in gen_params.txt'))
        else:
            # Validate whether replication stopping threshold is a float
            try:
                float(replication_stopping_threshold)
            except ValueError:
                self.error_manager.add_validation_error(ValidationException(f'The value mapped to replication_stopping_threshold is not a valid number'))
            
            
        # Validate whether all EventTypes are in the self.event_params_dict
        for e in self.EventTypes:
            temp = self.event_params_dict.get(e)
            if not temp:
                self.error_manager.add_validation_error(ValidationException(f'{e} is not in event_params.txt'))
                
        # Validate distributions allowed by the TD: this file does not exist yet so it is not yet implemented
            
        # Check error manager for errors and display them
        if self.error_manager.has_validation_errors():
            self.error_manager.display_errors()
            raise SystemExit("Validation failed. Please fix the errors above.")
        # Custom validations by the TD
        self.TD_distribution_validation()

    def TD_distribution_validation(self):
        pass