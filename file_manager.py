"""
v.1.0.0 - Basic release
*.inp file manager for *ORIENTATION, *NSET and *ELSET parameters extraction and riting
"""

import numpy as np


class FileProcessor:
    """Processes the input file reading and writing data"""

    def __init__(self) -> None:
        """Initialization of local class variables"""
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

    def read_file(self, file_path: str) -> None:
        """Opens the specified file and stores its data in a string"""
        try:
            with open(file_path, 'r') as file:
                self.read_lines = file.readlines()

        except FileNotFoundError:
            print("Sorry, the file path cannot be found or is invalid.")

    def search_sets(self, set_type: str) -> list:
        """
        Searches for sets inside the file and stores its name and number of elements, requires the
        set type (ELSET or NSET) and outputs the sets names and amount of nodes/elements
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
        Searches for orientation cards inside the input file and outputs the list of orientations,
        local axis and angles between local axis and the global ones.
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

        return orientation_list, x_local_list, y_local_list, z_local_list, x_angle_list, y_angle_list, z_angle_list

    def write_input_file(self, optimization_type: str, optimization_set: str, *args: float) -> None:
        """
        Rewrites input file to change orientation decks and includes output request, requires the
        optimization type (Stress, Strain or Displacement) and the set used for evaluating the 
        results. 
        """

        # Checks if input angles are the same number of orientations
        if len(args) != len(self.orientation_line):
            raise ValueError(
                "The input angles are not the same number of orientations")

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
        with open(self.output_file + ".inp", 'w') as file:
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
        Retrieve the results from a dat file according to the optimization type storing them
        locally in the class.
        """

        if optimization_type == "Stress":
            with open(self.output_file + ".dat", 'r') as file:

                # Header skip
                for _ in range(3):
                    next(file)

                for line in file:
                    elements = line.split()
                    self.sxx_values.append(float(elements[2]))
                    self.syy_values.append(float(elements[3]))
                    self.sxy_values.append(float(elements[5]))

        elif optimization_type == "Strain":
            with open(self.output_file + ".dat", 'r') as file:

                # Header skip
                for _ in range(3):
                    next(file)

                for line in file:
                    elements = line.split()
                    self.exx_values.append(float(elements[2]))
                    self.eyy_values.append(float(elements[3]))
                    self.exy_values.append(float(elements[5]))

        elif optimization_type == "Displacement":
            with open(self.output_file + ".dat", 'r') as file:

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
        Processes the results according to the optimization type: if stress-based, uses Tsai-Hill
        failure criteria (*args = X11 traction, X11 compression, X22 traction, X22 compression,
        and X12). Additionaly, the stress computation can be switched to max-stress by the sixth 
        *arg ("Tsai-Hill" or "Max stress") If strain based, calculates each ratio (*args = e*11 
        traction, e*11 compression, e*22 traction, e*22 compression and e*12). If displacement 
        based, no *args needed as the output will be the resultant.
        """
        if optimization_type == "Stress":

            x11t, x11c, x22t, x22c, x12 = args[1:6]
            calculation_methodology = args[0]

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
            e11t, e11c, e22t, e22c, e12 = args

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
                resultant = (uxx_value ** 2 + uyy_value ** 2 + uzz_value ** 2) ** 0.5

                u_magnitude.append(resultant)
            
            if optimization_criteria == "Max":
                return max(u_magnitude)
            if optimization_criteria == "Average":
                return sum(u_magnitude) / len(u_magnitude)

debug = FileProcessor()
debug.read_file("Shell_3_sections_flipped.inp")
debug.search_orientation()
# debug.write_input_file("Stress", "design_elements",
#                        50.213412312, 65.12341234523, 75.128739821763)
# debug.retrieve_results("Stress")
# a = debug.process_results(
    # "Stress", "Max", "Max stress", 1500, 1200, 50, 250, 70)
# print(a)
# debug.write_input_file("Strain", "design_elements",
#                        50.213412312, 65.12341234523, 75.128739821763)
# debug.retrieve_results("Strain")
# a = debug.process_results(
#     "Strain", "Max", 0.01050, 0.00850, 0.00500, 0.02500, 0.01400)
# print(a)
debug.write_input_file("Displacement", "design_elements",
                       50.213412312, 65.12341234523, 75.128739821763)
debug.retrieve_results("Displacement")
a = debug.process_results(
    "Displacement", "Average")
print(a)