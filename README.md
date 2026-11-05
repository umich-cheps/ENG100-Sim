# Simulation Core Library

This repository provides a Python-based simulation framework for organizing and running various simulation projects. As an example, this project implements a vaccine clinic simulation using a modular, extensible framework. The framework is designed to be flexible, allowing you to easily plug in new simulation models by extending the provided core functionality.

## Project Structure

```plaintext
simulation_project/
│
├── simu_core/                    # Core library (general-purpose classes and functions)
│   ├── __init__.py               # Exposes SimuCore
|   ├── base_table.py             # Helper class for handling base table
|   ├── error_manager.py          # Helper class for managing errors
|   ├── exceptions.py             # Custom exception definitions
|   ├── file_util.py              # Helper class for reading files
|   ├── metrics_table.py          # Helper class for handling metrics table
|   ├── random_variable.py        # Helper class for generating random variables
│   ├── simu_core.py              # Abstract base class for simulations
|   ├── statistics_table.py       # Helper class for handling statistics table
|   ├── task_queue.py             # DEPRECATED (last updated W26) 
|   ├── task_table.py             # DEPRECATED (last updated W26) 
|   ├── utils.py                  # Additional utility functions
|   └── database/                 # Contains model and repository definitions for all databases
|       ├── models/               # Contains model definitions
|       |   ├── __init__.py       # Exposes models
|       |   ├── custom.py         # Custom models for individual simulations
|       |   └── simulation.py     # Models for tasks, metrics, and statistics
|       └── repositories/         # Contains repository class definitions
|           ├── __init__.py                 # Exposes repositories
|           ├── base_repository.py          # Repository class for base table
|           ├── event_repository.py         # DEPRECATED (last updated F25) 
|           ├── metrics_repository.py       # Repository class for metrics table
|           ├── statistics_repository.py    # Repository class for statistics table
|           └── task_repository.py          # DEPRECATED (last updated S26) 
│
├── bootstrap/                    # Simulation framework modules
│   ├── __init__.py               # Exposes framework modules
│   ├── read_module.py            # ReadModule implementation (handles input reading)
│   ├── init_module.py            # InitModule implementation (initializes simulation)
│   ├── run_simulation_module.py  # RunSimulationModule implementation (runs simulation)
│   ├── gen_sim_metrics_module.py # GenSimMetricsModule implementation (generates statistics)
|   ├── parse_module.py           # ParseModule implementation (parses input/output files)
│   ├── report_module.py          # ReportModule implementation (generates reports)
│   └── validate_module.py        # ValidateModule implementation (validates input/output after parsing)
|
├── simulations/                  # Specific simulations (e.g., coin toss)
│   ├── __init__.py               # Exposes CoinTossSimCore
│   ├── coin_toss_simulation.py   # DEPRECATED (last updated W25) Coin toss simulation implementation
│   ├── patient_access_simulation_1.py      # Vaccine clinic simulation implementation
│   ├── patient_access_simulation_2.py      # DEPRECATED (last updated S25) 
│   ├── patient_access_simulation_3.py      # DEPRECATED (last updated S25) 
│   └── patient_access_simulation_4.py      # DEPRECATED (last updated S25) 
|
├── sql/                          # Contains SQL definitions for databases
|   ├── metrics.sql               # Metrics table SQL definition
|   ├── statistics.sql            # Statistics table SQL definition
|   └── tasks.sql                 # DEPRECATED (last updated S26)
|
├── tests/                        # Contains unit testing files
|   ├── test_file_util_input      # Input files needed for file_util tests
|   |   └── ...            
|   ├── test_random_variable_input      # Input files needed for random variable tests
|   |   └── ...                   
|   ├── deprecated_test_task_table.py   # DEPRECATED (last updated S26) 
|   ├── test_base_table.py        # Unit test for base tables
|   ├── test_file_util.py         # Unit test for file util (final utility functions)
|   ├── test_metrics_table.py     # Unit test for metrics tables
|   ├── test_random_variable.py   # Unit test for random variables
|   └── test_statistics_table.py  # Unit test for statistics tables
│
├── data/                         # Contains input/output files for simulations
│   ├── input/                    # Input file directory
│   |    └── ...                
│   └── output/                   # Output file directory
|        └── ...                 
|
├── main_patient_access_simulation_1.py     # Vaccine clinic example simulation main file
├── main_patient_access_simulation_2.py     # DEPRECATED (last updated S25) 
├── main_patient_access_simulation_3.py     # DEPRECATED (last updated S25) 
├── main_patient_access_simulation_4.py     # DEPRECATED (last updated S25) 
└── main_simulation.py                      # DEPRECATED (last updated W25)
```

## Installation

To set up the project and run the simulation, you'll need Python 3.6+ and the following Python packages:

- `pandas` (for data handling)
- `matplotlib` (for generating reports)
- `pandasql`
- `yaml`
- `pydantic`
- `duckdb`
- `sqlalchemy`

### Step 1: Clone the Repository

```bash
git clone https://github.com/your_username/simulation_project.git
cd CHEPSSimuCore
```

### Step 2: Set up the Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate        # On Linux/macOS
venv\Scripts\activate           # On Windows
```

### Step 3: Install Dependencies

```bash
pip install pandas matplotlib pandasql pyyaml pydantic duckdb sqlalchemy
```

## Usage

### Input File Structure

```plaintext
gen_params.txt                    # REQUIRED; General parameters needed for all simulations (see example below)
│
├── input_file_params.txt         # REQUIRED; File paths for input files to be read by SimuCore
│   ├── event_params.txt          # REQUIRED; Parameters for each event type (see example below)
│   ├── cust_params.txt           # OPTIONAL; Custom parameters for the given simulation
│   ├── empirical_dist.txt        # OPTIONAL; Empirical distribution file (Required if using empirical distribution)
│   └── Additional input files    # OPTIONAL; Additional input files needed for a given simulation
│
└── output_file_params.txt        # REQUIRED; File paths for output files to be written to
    └── Additional output files   # OPTIONAL; Additional output files needed for a given simulation
```

### Input File Examples

#### gen_params.txt

```plaintext
replication_stopping_criteria num_epochs
num_epochs 15
simulation_stopping_criteria num_replications
num_replications 10
epoch_duration 480
input_file_params data/input/patient_access_1/input_file_params.txt
output_file_params data/input/patient_access_1/output_file_params.txt
```

#### input_file_params.txt/output_file_params.txt
```plaintext
/path/to/folder/containing/files/
file_1_description file_name.txt
file_2_description file_name.png
```
***Note:** output_file_params.txt can include images, text files, or other file types but input_file_params.txt must contain text-based files (i.e. .txt, .csv, .yaml, etc.)*

#### event_params.txt
```plaintext
event_type event_type_A
distribution normal
mean 30
std_dev 10
stopping_criteria interarrival
event_type event_type_B
distribution gaussian
mean 16
std_dev 3
stopping_criteria trial
threshold 1
```

### Running the Simulation

To run a simulation, execute the `name_of_main_simulation_file.py` script:

```bash
python3 name_of_main_simulation_file.py
```

This will:

1. Read the input file.
2. Initialize the simulation infrastructure.
3. Simulate the specified number of replications and epochs per replication.
4. Generate and print basic statistics (mean, median, 95% confidence interval).

### Output Example

```plaintext
Reading input
Initializing simulation infrastructure...
Running simulation...
Generating simulation metrics...
Metrics Name: num_vaccinated    mean: 4.8   median 2    95% confidence interval (-4.6, 14.2)
Metrics Name: num_waitlisted    mean: 106.8 median: 50  95% confidence interval (-102.5, 316.2)
```


## Adding New Simulations

The framework is designed to allow the easy addition of new simulations. To add a new simulation, follow these steps:

1. **Extend `SimuCore`**: Create a new class in the `simulations` folder that extends the `SimuCore` abstract class.
2. **Implement Required Methods**: Override the `read_input`, `validate_input`, `task_comparator`, and `generate_reports` methods.
3. **Implement Required Dictionaries**: Define dictionaries `process_function_names`, `task_type_information_dict`, and `update_metric_function_names`. Be sure to define methods listed in these dictionaries as well.
4. **Add Custom Logic**: Add your specific simulation logic to the new class.

Once added, you can use the existing `bootstrap` modules to structure your new simulation.

## Folder Breakdown

### `simu_core/`

Contains the core library, including the `SimuCore` abstract base class. All simulations extend this core class to ensure consistency and reusability.

### `simu_core/database/`

Contains the models and repositories used in the simulations.

### `bootstrap/`

Contains reusable modules for reading input, initializing the simulation, running the simulation, generating metrics, and reporting. These modules are designed to work with any simulation that extends `SimuCore`.

### `simulations/`

Houses specific simulation models. The current implementation includes a coin toss simulation.

### `data/input/`

Holds the input files for the simulations. In this project, it contains a file specifying the number of coin tosses.

### Parallelism Acceleration

The current implementation for the parallelized acceleration is on branch dev_v3_parallel. Progress was last made on it W26 by @mattschu22 (reach out to ummatt@umich.edu with any questions). The purpose of this version is to accelerate the runtime by running each replication in parallel. Curerntly there are two ways to do this:

#### Thread-Level Parallelism

This version of the implementation uses `concurrent.futures.ThreadPoolExecutor`. Each replication is run seperately in its own thread. The remaining issue with this version is the CHEPS server does not support the thread-level locking mechanisms that concurrent access to DuckDB requires. To finish this implementation, library developers should use the thread-safe multi-queue. Each replication thread should write to the queue with full SQL queries rather than a database and a single consumer with a single DB connection should execute the queries in the database. For queries that return results, replication threads should wait for the database thread to place the result in their queue

#### Process-Level Parallelism

This version of the implementation uses `concurrent.futures.ProcessPoolExecutor`. Each replication is run separately in its own process. The remaining issue with this version is that DuckDB does not support concurrent connections from different processes. A similar solution to the thread version on a process-level can be applied here but a simpler solution may be using `postgres` instead. Postgres directly supports this type of usage and can be used to replace DuckDB entirely. The only drawback is the `postgres` will be slower for analytic workloads.

## License

CHEPS Property (DO NOT CLONE TO YOUR PERSONAL COMPUTER)
