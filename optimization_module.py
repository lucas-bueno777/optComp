"""
v.1.0.0 - Basic release
Optimization module for optComp software
"""

import os
import time
import nevergrad as ng
from file_manager import FileProcessor

# File processor class initialization


class OptimizationModule:
    """Opt. module for optComp - only orientations"""

    def __init__(self,
                 input_file: str,
                 opt_type: str,
                 opt_set: str,
                 opt_criteria: str,
                 max_iterations: int,
                 *args: float
                 ) -> None:
        """
        Class setup variables and FileProcessor class initialization

        Args:
            input_file (str): The name of CalculiX input file with the *inp extension
            opt_type (str): Type of the optimization: "Stress", "Strain" or "Displacement"
            opt_set (str): Name of the set to be evaluated
            opt_criteria (str): "Max" or "Average"
            max_iterations (int): Max number of iterations allowed
            *args: if opt_type is "Stress", first value must be "Tsai-Hill" or "Max stress"
                followed by X11T, X11C, X22T, X22C, X12 allowables. If opt_type is "Strain",
                E11T, E11C, E22T, E22C, E12 allowables.If opt_type is "Displacement", not 
                needed.
        """
        # Time evaluation
        start_time = time.time()

        # Standard definitions
        self.calculix_name = "ccx"
        self.work_directory = os.path.dirname(os.path.abspath(__file__))

        # Local variables
        self.opt_type = opt_type
        self.opt_set = opt_set
        self.opt_criteria = opt_criteria
        self.max_iterations = max_iterations
        self.allowables = args

        # FileProcessor definitions
        self.opt_object = FileProcessor()
        self.output_file = self.opt_object.output_file
        self.opt_object.read_file(input_file)
        aux_out, *_ = self.opt_object.search_orientation()
        self.num_variables = len(aux_out)

        # Optimizer definitions
        instrum = ng.p.Instrumentation(
            *[ng.p.Scalar(lower=0, upper=90) for _ in range(self.num_variables)])
        self.optimizer = ng.optimizers.OnePlusOne(parametrization=instrum)

        # Time evaluation print
        end_time = time.time()
        self.elapsed_time = end_time - start_time
        self.calculix_time = None
        print(f"Initialization in {self.elapsed_time:.4f} seconds\n")

    def objective_function(self, *angles: float):
        """
        Comprises file_manager functions to output the minimization criteria

        Args:
            *angles (float): receives the rotation angles around local z-axis [0,90]

        Returns:
            objective (float): optimization criteria for minimization, such as highest
                Tsai-Hill failure index, maximum displacement or most critical strain.
        """

        self.opt_object.write_input_file(self.opt_type, self.opt_set, *angles)
        self.calculix_time = self.opt_object.run_calculix(
            self.work_directory, self.calculix_name, self.output_file)
        self.opt_object.retrieve_results(self.opt_type)
        objective = self.opt_object.process_results(
            self.opt_type, self.opt_criteria, *self.allowables)
        return objective

    def change_default_definitions(self, calculix_name, work_directory):
        """
        Changes the opt. module default definitions

        Args:
            calculix_name (str): Calculix executable without the ".exe"
            output_file (str): Name of the output file in each iteration of the
                optimizer
            work_directory (str): Name of the current work directory
        """
        self.calculix_name = calculix_name
        self.work_directory = work_directory

    def run_optimization(self):
        """
        Run command of the optimization

        Returns:
            best_solution (list): Contains the respective best angles given by the optimizer
        """

        for _ in range(self.max_iterations):

            start_time = time.time()

            candidate = self.optimizer.ask()
            objective_value = self.objective_function(
                *candidate.args, **candidate.kwargs)
            self.optimizer.tell(candidate, objective_value)

            end_time = time.time()

            elapsed_time = end_time - start_time

            # If needed, one can uncomment below code to study performance
            percent_runtime = (elapsed_time - self.calculix_time) / elapsed_time * 100
            print(f"CalculiX time: {self.calculix_time:.4f} seconds")
            print(f"Total time = {elapsed_time:.4f} seconds")
            print(f"Optimizer runtime represents {percent_runtime:.2f}% of total time elapsed\n")


        best_solution = self.optimizer.provide_recommendation().args

        return best_solution

class MultiParameterOptimizationModule:
    """
    Optimization module for optComp software that can handle multiple parameters such as different
    materials, thickness variation (for shell elements), variable number of plies (only for 
    composite shells) and multiple orientations.
    """
    def __init__(self) -> None:
        # Initialization of booleans that define which type of optimization will be conducted
        self.material_optimization = True
        self.thickness_optimization = True
        self.orientation_optimization = True
        self.orientation_continuous = False
        self.number_of_plies_optimization = False
        self.optimizer = None

    def objective_function(self) -> None:
        """Objective function declaration"""

    def optimizer_setup(self, *args: list) -> None:
        """
        Comprises the parametrization of the applicable optimization variables.
        
        Args:
            *args (list): the first positional argument should be the material list, the second one 
            must be the thickness bounds, the third one must be the orientation bounds or discrete
            values, the fourth one must be the number of plies interval
        """
        material_list, thickness_list, orientations_list, plies_list = args

        # Creation of Nevergrad parametrizations
        parametrizations = []
        if self.material_optimization:
            parametrizations.append(ng.p.Choice(material_list))
        if self.number_of_plies_optimization:
            parametrizations.append(ng.p.Choice(plies_list))
        if self.thickness_optimization:
            parametrizations.append(ng.p.Array(shape = 1).set_bounds(thickness_list[0],
                                                                     thickness_list[1]))
        # Treatment for continuous or discrete case
        if self.orientation_continuous:
            parametrizations.append(ng.p.Array(shape = 1).set_bounds(orientations_list[0],
                                                                   orientations_list[1]))
        else:
            parametrizations.append(ng.p.Choice(orientations_list))

        # Joining all parametrizations in a single object
        nevergrad_parametrization = ng.p.Instrumentation(parametrizations)
        self.optimizer = ng.optimizers.NGOpt(parametrization = nevergrad_parametrization)


# debug = OptimizationModule("Shell_3_sections_flipped.inp", "Stress", "design_elements",
#                            "Max", 50, "Tsai-Hill", 1500, 1200, 50, 250, 70)
# debug = OptimizationModule("Wing.inp", "Strain", "Both_spars",
#                            "Max", 5, 0.01050, 0.00850, 0.00500, 0.02500, 0.01400)
# best = debug.run_optimization()
# print(best)
