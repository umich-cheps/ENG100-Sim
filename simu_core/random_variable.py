from abc import ABC, abstractmethod
from numpy import random
from .file_util import FileUtil


class RandomVariable(ABC):
    def __init__(self, distribution, params):
        """
        Initialize a random variable with the specified distribution 
        and parameters.

        Args:
            distribution (str): The name of the distribution.
            params (dict): Parameters for the distribution.
                For emperical distribution, this should be a dictionary
                with keys as outcomes and values as probabilities.

        Raises:
            ValueError: If the distribution or its parameters are 
                invalid.
        """
        distribution = distribution.lower()  # Remove case sensitivity
        self.params = {}

        if distribution == 'poisson':
            self.distribution = 'poisson'
            if float(params['lambda']) < 0:
                raise ValueError('Invalid distribution parameters: lambda must be non-negative')
            self.params = {'lambda': float(params['lambda'])}

        elif distribution == 'uniform':
            self.distribution = 'uniform'
            self.params = {
                'lower_bound': float(params['lower_bound']),
                'upper_bound': float(params['upper_bound'])}
            
        elif distribution == 'normal':
            self.distribution = 'normal'
            if float(params['std_dev']) < 0:
                raise ValueError(
                    "Invalid distribution parameters: standard deviaton must be non-negative") 
            self.params = {'mean': float(params['mean']), 'std_dev': float(params['std_dev'])}
        
        elif distribution == 'binomial':
            self.distribution = 'binomial'
            if int(params['n']) < 0: 
                raise ValueError('Invalid distribution parameters: n must be non-negative')
            if float(params['p']) < 0 or float(params['p']) > 1: 
                raise ValueError('Invalid distribution parameters: p must be within [0,1]')
            self.params = {
                'n': params['n'], 
                'p': float(params['p'])}
        
        elif distribution == 'exponential':
            self.distribution = 'exponential'
            if float(params['lambda']) <= 0: 
                raise ValueError('Invalid distribution parameters: lambda must be positive')
            self.params = {'lambda': float(params['lambda'])}
        
        elif distribution == 'geometric':
            self.distribution = 'geometric'
            if float(params['p']) <= 0 or float(params['p']) > 1: 
                raise ValueError('Invalid distribution parameters: p must be within [0,1]')
            self.params = {'p': float(params['p'])}
        
        elif distribution == 'bernoulli':
            self.distribution = 'bernoulli'
            if float(params['p']) < 0 or float(params['p']) > 1: 
                raise ValueError('Invalid distribution parameters: p must be within [0,1]')
            self.params = {'p': float(params['p'])}
        
        elif distribution == 'empirical':
            self.distribution = 'empirical'
            self.read_empirical_distribution(params['path'])
            if (self.input_type == 'aggregate'):
                total_prob = 0
                for value in self.distribution_map.values():
                    if value < 0: 
                        raise ValueError('Invalid probabilities: probabilities must be non-negative')
                    elif value > 1:
                        raise ValueError('Invalid probabilities: probabilities must be less than 1')
                    else:
                        total_prob += value
                if total_prob != 1: 
                    raise ValueError('Invalid probabilities: the sum of all probabilities must equal 1')
                self.params = self.distribution_map
        
        else:
            raise ValueError('Invalid distribution')

    def sample(self, n):
        """Generate a sample of size n from the random variable."""
        if self.distribution == 'poisson':
            return random.poisson(lam=self.params['lambda'], size=n)
        
        elif self.distribution == 'uniform':
            return random.uniform(
                low=self.params['lower_bound'],
                high=self.params['upper_bound'], 
                size=n)
        
        elif self.distribution == 'normal':
            return random.normal(
                loc=self.params['mean'], 
                scale=self.params['std_dev'],
                size=n)
        
        elif self.distribution == 'binomial':
            return random.binomial(
                n=self.params['n'],
                p=self.params['p'],
                size=n)
        
        elif self.distribution == 'exponential':
            return random.exponential(scale=1/self.params['lambda'], size=n)
        
        elif self.distribution == 'geometric':
            return random.geometric(p=self.params['p'], size=n)
        
        elif self.distribution == 'bernoulli':
            return random.binomial(n=1, p=self.params['p'], size=n)
        
        elif self.distribution == 'empirical':
            return random.choice(
                a=list(self.params.keys()), 
                p=list(self.params.values()),
                size=n,)
        
        else:
            raise ValueError('Invalid distribution')
        
    def read_empirical_distribution(self, path):
        self.distribution_map = {}
        try:
            with open(path, 'r', encoding='utf-8') as file:
                input_type_line = file.readline()
                input_type_line = input_type_line.strip()
                input_type_line = input_type_line.split()
                self.input_type = input_type_line[1].lower()
                if input_type_line[0] != 'input_type':
                    raise ValueError('input_type must be on the first line of the ' \
                        'empirical distribution file')
                if self.input_type != 'aggregate' and self.input_type != 'raw':
                    raise ValueError('Empirical distribution input_type must be aggregate or raw')
                line = file.readline()
                while (line):
                    line = line.strip()
                    line = line.split()
                    outcome = line[0]
                    probability = float(line[1])
                    if outcome == 'input_type':
                        raise ValueError('input_type must only appear once and on the first line ' \
                            'in the empirical distribution file')
                    self.distribution_map[outcome] = float(probability)
                    line = file.readline()
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Error: The file '{path}' does not exist.") from e
        