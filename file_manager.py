"""
v.1.0.0 - Basic release
Comprises all data management for reading, modifying and writing *inp files,
process *.dat files output requests and run CalculiX by CMD.
"""

import subprocess
import re
import os
import numpy as np


class FileProcessor:
    """Processes the FEM files reading and writing"""

    def __init__(self) -> None:
        """
        Initialization of local class variables
        """
        self.read_lines = None
        self.output_file = "MOD_file"
        self.orientation_line = []
        self.modified_lines = []
        self.sxx_values = []
        self.syy_values = []
        self.sxy_values = []
        self.exx_values = []
        self.eyy_values = []
        self.exy_values = []
        self.uxx_values = []
        self.uyy_values = []
        self.uzz_values = []

        self.orientations_list = []
        self.orientations_index = []
        self.materials_list = []
        self.steps_list = []
        self.nsets_list = []
        self.elsets_list = []
        self.solid_section_list = []
        self.solid_section_index = []
        self.shell_list = []
        self.composite_list = []
        self.composite_layers = []
        self.composite_index = []
        self.shell_list = []
        self.shell_index = []

    def read_file(self, file_path: str) -> None:
        """
        Opens the specified file and stores its data in a string
        
        Args:
            file_path (str): path of the specified input file
        """
        try:
            with open(file_path, 'r', encoding="utf-8") as file:
                self.read_lines = file.readlines()

        except FileNotFoundError:
            print("Sorry, the file path cannot be found or is invalid.")

    def search_sets(self, set_type: str) -> list:
        """
        Searches for sets inside the file and stores its name and number of elements

        Args:
            set_type (str): "ELSET" for element based or "NSET" for node based
             
        Returns:
            sets (list): sets names
            data_values (list): amount of nodes/elements in each set
        """
        sets = []
        data_values = []

        for i in range(len(self.read_lines)):
            line = self.read_lines[i]

            # If a set is found
            if set_type in line.upper():
                split_line = line.split("=")
                nset_name = split_line[1].strip()

                # Counts how many lines after the *NSET starts with a number to count them
                lines_of_data = 0
                for j in range(i+1, len(self.read_lines)):
                    first_character = self.read_lines[j].strip()[0]
                    if first_character.isdigit():
                        lines_of_data += 1
                    else:
                        break

                # Counts how many nodes/elements are inside the set
                count_numbers = 0
                for j in range(i+1, i+1+lines_of_data):
                    line_splitted_by_commas = self.read_lines[j].strip().split(
                        ",")
                    # Removes residual spaces from operation
                    if "" in line_splitted_by_commas:
                        line_splitted_by_commas.remove("")
                    count_numbers += len(line_splitted_by_commas)

                # Stores the sets name and contents inside the lists
                sets.append(nset_name)
                data_values.append(count_numbers)

        return sets, data_values

    def search_orientation(self) -> list:
        """
        Searches for orientation cards inside the input file and outputs useful information.

        Returns:
            orientation_list (list):
            x_local_list (list): (i, j k) vector for each x local axis
            y_local_list (list): (i, j k) vector for each y local axis
            z_local_list (list): (i, j k) vector for each z local axis
            x_angle_list (list): angle between each x local axis and x global axis
            y_angle_list (list): angle between each y local axis and y global axis
            z_angle_list (list): angle between each z local axis and z global axis
        """
        orientation_list = []
        x_local_list = []
        y_local_list = []
        z_local_list = []
        x_angle_list = []
        y_angle_list = []
        z_angle_list = []

        for i in range(len(self.read_lines)):
            line = self.read_lines[i]

            # If a orientation card is found
            if "*ORIENTATION" in line.upper():
                split_line = line.split("=")
                orientation_name = split_line[-1].strip()
                input_line = self.read_lines[i+1].split(",")
                input_line = [float(num) for num in input_line]

                # Vector manipulations
                vector_x = np.array(input_line[:3])
                point_xy = np.array(input_line[-3:])
                x_local = vector_x / np.linalg.norm(vector_x)
                z_local = np.cross(x_local, point_xy) / \
                    np.linalg.norm(np.cross(x_local, point_xy))
                y_local = np.cross(z_local, x_local)

                # Angle calculation
                angle_x = np.degrees(
                    np.arccos(np.dot(x_local, np.array([1, 0, 0]))))
                angle_y = np.degrees(
                    np.arccos(np.dot(y_local, np.array([0, 1, 0]))))
                angle_z = np.degrees(
                    np.arccos(np.dot(z_local, np.array([0, 0, 1]))))

                # List append
                orientation_list.append(orientation_name)
                x_local_list.append(x_local.tolist())
                y_local_list.append(y_local.tolist())
                z_local_list.append(z_local.tolist())
                x_angle_list.append(angle_x)
                y_angle_list.append(angle_y)
                z_angle_list.append(angle_z)
                self.orientation_line.append(i)

        return (orientation_list, x_local_list, y_local_list, z_local_list,
                x_angle_list, y_angle_list, z_angle_list)

    def write_input_file(self, optimization_type: str, optimization_set: str, *args: float) -> None:
        """
        Rewrites input file to change orientation decks and includes output request.

        Args:
            optimization_type (str): can be "Stress", "Strain" or "Displacement"
            optimization_set (str): name of the evaluated set
            *args (float): angles of rotation for each *ORIENTATION card
        """

        # Empty the modification lines
        self.modified_lines = []

        # Checks if input angles are the same number of orientations
        if len(args) != len(self.orientation_line):
            num_angles = str(len(args))
            num_orientations = str(len(self.orientation_line))
            raise ValueError(
                f"Input angles ({num_angles}) differ from orientations ({num_orientations})")

        # Appends all data before the first *ORIENTATION deck
        for i in range(self.orientation_line[0]):
            self.modified_lines.append(self.read_lines[i])

        # Appends the rotation angle around Z axis
        for i in range(len(self.orientation_line)):
            self.modified_lines.append(
                self.read_lines[self.orientation_line[i]])
            self.modified_lines.append(
                self.read_lines[self.orientation_line[i] + 1])
            self.modified_lines.append(f"3, {args[i]:.4f}\n")

        # Appends the rest of the data
        for i in range(self.orientation_line[-1] + 2, len(self.read_lines)):
            self.modified_lines.append(self.read_lines[i])

        # Sets the output request according to user entry
        if optimization_type == "Displacement":
            output_request = "*NODE PRINT, NSET=" + optimization_set + "\nU\n"
        elif optimization_type == "Stress":
            output_request = "*EL PRINT, ELSET=" + optimization_set + "\nS\n"
        elif optimization_type == "Strain":
            output_request = "*EL PRINT, ELSET=" + optimization_set + "\nE\n"
        else:
            raise ValueError("Invalid")

        # Finds the *END STEP card of the file
        for i in range(len(self.modified_lines)):
            # Compatibility with PrePoMax v1.3.5.1
            if "** END STEP" in self.modified_lines[i].upper():
                end_step_line = i
                compatibility_prepomax = True
                break
            elif "*END STEP" in self.modified_lines[i].upper():
                end_step_line = i
                compatibility_prepomax = False

        # Writes the output request just above the end of the step
        with open(self.output_file + ".inp", 'w', encoding="utf-8") as file:
            if compatibility_prepomax:
                file.writelines(self.modified_lines[:end_step_line - 1])
                file.writelines(output_request)
                file.writelines(self.modified_lines[end_step_line - 1:])
            else:
                file.writelines(self.modified_lines[:end_step_line])
                file.writelines(output_request)
                file.writelines(self.modified_lines[end_step_line:])

    def retrieve_results(self, optimization_type: str) -> None:
        """
        Retrieve the results from a dat file and stores them locally in the class.

        Args:
            optimization_type (str): can be "Stress", "Strain" or "Displacement"
        """
        # Empty the lists of results
        self.sxx_values = []
        self.syy_values = []
        self.sxy_values = []
        self.exx_values = []
        self.eyy_values = []
        self.exy_values = []
        self.uxx_values = []
        self.uyy_values = []
        self.uzz_values = []

        if optimization_type == "Stress":
            with open(self.output_file + ".dat", 'r', encoding="utf-8") as file:

                # Header skip
                for _ in range(3):
                    next(file)

                for line in file:
                    elements = line.split()
                    self.sxx_values.append(float(elements[2]))
                    self.syy_values.append(float(elements[3]))
                    self.sxy_values.append(float(elements[5]))

        elif optimization_type == "Strain":
            with open(self.output_file + ".dat", 'r', encoding="utf-8") as file:

                # Header skip
                for _ in range(3):
                    next(file)

                for line in file:
                    elements = line.split()
                    self.exx_values.append(float(elements[2]))
                    self.eyy_values.append(float(elements[3]))
                    self.exy_values.append(float(elements[5]))

        elif optimization_type == "Displacement":
            with open(self.output_file + ".dat", 'r', encoding="utf-8") as file:

                # Header skip
                for _ in range(3):
                    next(file)

                for line in file:
                    elements = line.split()
                    self.uxx_values.append(float(elements[1]))
                    self.uyy_values.append(float(elements[2]))
                    self.uzz_values.append(float(elements[3]))

    def process_results(
            self, optimization_type: str, optimization_criteria: str, *args: float) -> float:
        """
        Processes the results of the *.dat file.

        Args:
            optimization_type (str): can be "Stress", "Strain" or "Displacement"
            optimization_criteria (str): can be "Max" or "Average"
            *args (None): If "Stress", the first arg (str) need to be "Tsai-Hill" or "Max stress"
                and the next ones (float) are the allowables X11T, X11C, X22T, X22C, X12. If
                "Strain", the args (float) are the allowables E11T, E11C, E22T, E22C, E12. If
                "Displacement", no arg is needed.

        Returns:
            max_value (float): most structural critical value according to optimization type and
                criteria, such as higher Tsai-Hill index, average displacement, etc.    
        """
        if optimization_type == "Stress":

            if len(args) == 6:
                calculation_methodology, x11t, x11c, x22t, x22c, x12 = args
            else:
                raise ValueError("Stress calculation requires 6 args")

            if calculation_methodology == "Tsai-Hill":
                tsai_hill_output = []

                # Calculates the Tsai-Hill failure index according to the signal (+ -)
                for i in range(len(self.sxx_values)):
                    x_stress = self.sxx_values[i]
                    y_stress = self.syy_values[i]
                    xy_stress = self.sxy_values[i]

                    if self.sxx_values[i] < 0:
                        x11 = x11c
                    else:
                        x11 = x11t

                    if self.syy_values[i] < 0:
                        x22 = x22c
                    else:
                        x22 = x22t

                    failure_index = (x_stress / x11) ** 2 + (y_stress / x22) ** 2 + \
                        (xy_stress / x12) ** 2 - \
                        x_stress * y_stress / (x11 ** 2)
                    tsai_hill_output.append(failure_index)

                # Outputs a value according to the criteria choosen
                if optimization_criteria == "Max":
                    return max(tsai_hill_output)
                if optimization_criteria == "Average":
                    return sum(tsai_hill_output) / len(tsai_hill_output)

            if calculation_methodology == "Max stress":
                sxx_ratios = []
                syy_ratios = []
                sxy_ratios = []

                # Calculates the ratio of max stress according to signal (+ -)
                for i in range(len(self.sxx_values)):
                    x_stress = self.sxx_values[i]
                    y_stress = self.syy_values[i]
                    xy_stress = self.sxy_values[i]

                    if self.sxx_values[i] < 0:
                        x11 = x11c
                    else:
                        x11 = x11t

                    if self.syy_values[i] < 0:
                        x22 = x22c
                    else:
                        x22 = x22t

                    sxx_failure_index = abs(x_stress / x11)
                    syy_failure_index = abs(y_stress / x22)
                    sxy_failure_index = abs(xy_stress / x12)

                    sxx_ratios.append(sxx_failure_index)
                    syy_ratios.append(syy_failure_index)
                    sxy_ratios.append(sxy_failure_index)

                # Outputs a value according to the criteria choosen
                if optimization_criteria == "Max":
                    max_sxx = max(sxx_ratios)
                    max_syy = max(syy_ratios)
                    max_sxy = max(sxy_ratios)
                    return max(max_sxx, max_syy, max_sxy)

                if optimization_criteria == "Average":
                    average_sxx = sum(sxx_ratios) / len(sxx_ratios)
                    average_syy = sum(syy_ratios) / len(syy_ratios)
                    average_sxy = sum(sxy_ratios) / len(sxy_ratios)
                    return max(average_sxx, average_syy, average_sxy)

        if optimization_type == "Strain":

            if len(args) == 5:
                e11t, e11c, e22t, e22c, e12 = args
            else:
                raise ValueError("Strain calculation requires 5 args")

            exx_ratios = []
            eyy_ratios = []
            exy_ratios = []

            # Calculates the ratio of max stress according to signal (+ -)
            for i in range(len(self.exx_values)):
                x_strain = self.exx_values[i]
                y_strain = self.eyy_values[i]
                xy_strain = self.exy_values[i]

                if self.exx_values[i] < 0:
                    e11 = e11c
                else:
                    e11 = e11t

                if self.eyy_values[i] < 0:
                    e22 = e22c
                else:
                    e22 = e22t

                exx_failure_index = abs(x_strain / e11)
                eyy_failure_index = abs(y_strain / e22)
                exy_failure_index = abs(xy_strain / e12)

                exx_ratios.append(exx_failure_index)
                eyy_ratios.append(eyy_failure_index)
                exy_ratios.append(exy_failure_index)

            # Outputs a value according to the criteria choosen
            if optimization_criteria == "Max":
                max_exx = max(exx_ratios)
                max_eyy = max(eyy_ratios)
                max_exy = max(exy_ratios)
                return max(max_exx, max_eyy, max_exy)

            if optimization_criteria == "Average":
                average_exx = sum(exx_ratios) / len(exx_ratios)
                average_eyy = sum(eyy_ratios) / len(eyy_ratios)
                average_exy = sum(exy_ratios) / len(exy_ratios)
                return max(average_exx, average_eyy, average_exy)

        if optimization_type == "Displacement":

            u_magnitude = []

            for i in range(len(self.uxx_values)):
                uxx_value = self.uxx_values[i]
                uyy_value = self.uyy_values[i]
                uzz_value = self.uzz_values[i]
                resultant = (uxx_value ** 2 + uyy_value **
                             2 + uzz_value ** 2) ** 0.5

                u_magnitude.append(resultant)

            if optimization_criteria == "Max":
                return max(u_magnitude)
            if optimization_criteria == "Average":
                return sum(u_magnitude) / len(u_magnitude)

    def run_calculix(self, work_directory: str, ccx_name: str, file_name: str) -> float:
        """
        Runs calculix by CMD shell.
        
        Args:
            work_directory (str): the work directory of the file
            ccx_name (str): name of CalculiX executable without *.exe
            file_name (str): name of the input file with *.inp

        Returns:
            time_spent (float): time spent in CalculiX run (seconds)
        """

        os.chdir(work_directory)
        output = subprocess.check_output(
            ["start", "/B", "/WAIT", "cmd", "/C", f"{ccx_name} {file_name}"],
            shell=True,
            encoding="utf-8"
        )
        time_pattern = r"Total CalculiX Time: (\d+\.\d+)"
        match = re.search(time_pattern, output)
        time_spent = float(match.group(1))
        return time_spent

    def search_information(self) -> None:
        """
        Searches for relevant information in *.inp file and stores them inside the class
        environment. Cards that the purpose is only to show to the user get the first line saved,
        such as materials, steps, node sets and element sets. To those which may be edited, the
        index of the line is also saved such as orientations, shell sections, composites and solid
        sections.
        """
        for index, line in enumerate(self.read_lines):

            if "*ORIENTATION" in line.upper():
                self.orientations_index.append(index)
                self.orientations_list.append(line.strip())

                # Checks if the third line has input data
                if self.read_lines[index + 2][0].isdigit():
                    raise ValueError(f"Not allowed: orientation {line} has 2 lines of input")

            elif "*MATERIAL" in line.upper():
                self.materials_list.append(line.strip())

            elif "*STEP" in line.upper():
                self.steps_list.append(self.read_lines[index + 1].strip())

            elif "*NSET" in line.upper():
                self.nsets_list.append(line.strip())

            elif "*ELSET" in line.upper():
                self.elsets_list.append(line.strip())

            elif "*SOLID SECTION" in line.upper():
                self.solid_section_list.append(line.strip())
                self.solid_section_index.append(index)

            elif "*SHELL SECTION" in line.upper():

                if "COMPOSITE" in line.upper():
                    self.composite_list.append(line.strip())
                    self.composite_index.append(index)

                else:
                    self.shell_list.append(line.strip())
                    self.shell_index.append(index)

    def count_composite_layers(self, index_list: list) -> None:
        """
        Counts the number of layers in each composite card and store the result inside the class.
        
        Args:
            index_list (list): list with the indexes of each composite card in the input file.
        """

        for index in index_list:
            num_layers = 0
            for i in range(1,999):
                starts_with_number = self.read_lines[index + i][0].isdigit()

                if starts_with_number:
                    num_layers += 1
                else:
                    break

            self.composite_layers.append(num_layers)
