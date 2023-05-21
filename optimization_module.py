"""
v.1.0.0 - Basic release
Optimization module for optComp software
"""

import nevergrad as ng
from file_manager import FileProcessor
import os

# File processor class initialization
work_directory = os.path.dirname(os.path.abspath(__file__))
opt_object = FileProcessor()
opt_object.read_file("Shell_3_sections_flipped.inp")
opt_object.search_orientation()

# Objective function definition
def objective_function(*angles: float):
    """Comprises file_manager functions to output the minimization criteria"""
    
    opt_object.write_input_file("Displacement", "design_nodes", *angles)
    opt_object.run_calculix(work_directory, "ccx", "MOD_file")
    opt_object.retrieve_results("Displacement")
    objective = opt_object.process_results("Displacement", "Average")

    return objective

# Optimizer definition
num_variables = 3  # Number of variables
instrum = ng.p.Instrumentation(*[ng.p.Scalar(lower=0, upper=90) for _ in range(num_variables)])
optimizer = ng.optimizers.OnePlusOne(parametrization=instrum)

# Specify the maximum number of function evaluations
max_evaluations = 50

# Perform the optimization loop
for _ in range(max_evaluations):
    x = optimizer.ask()  # Get a candidate solution
    print(x)
    value = objective_function(*x.args, **x.kwargs)  # Evaluate the objective function
    optimizer.tell(x, value)  # Provide the evaluation result to the optimizer

best_solution = optimizer.provide_recommendation().args  # Get the best solution found

print(best_solution)  # Best solution found