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

    def read_file(self, file_path: str) -> None:
        """Opens the specified file and stores its data in a string"""
        try:
            with open(file_path, 'r') as file:
                self.read_lines = file.readlines()

        except FileNotFoundError:
            print("Sorry, the file path cannot be found or is invalid.")

    def search_sets(self, set_type: str) -> list:
        """Searches for sets inside the file and stores its name and number of elements"""
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
                    line_splitted_by_commas = self.read_lines[j].strip().split(",")
                    # Removes residual spaces from operation
                    if "" in line_splitted_by_commas:
                        line_splitted_by_commas.remove("")
                    count_numbers += len(line_splitted_by_commas)

                # Stores the sets name and contents inside the lists
                sets.append(nset_name)
                data_values.append(count_numbers)

        return sets, data_values

    def search_orientation(self) -> list:
        """Searches for orientation cards inside the input file"""
        self.orientation_line = []
        orientation_list =[]
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
                z_local = np.cross(x_local, point_xy) / np.linalg.norm(np.cross(x_local, point_xy))
                y_local = np.cross(z_local, x_local)

                # Angle calculation
                angle_x = np.degrees(np.arccos(np.dot(x_local, np.array([1, 0, 0]))))
                angle_y = np.degrees(np.arccos(np.dot(y_local, np.array([0, 1, 0]))))
                angle_z = np.degrees(np.arccos(np.dot(z_local, np.array([0, 0, 1]))))

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

    def write_new_orientation(self, input_inp) -> ".inp":
        a=2

debug = FileProcessor()
debug.read_file("Shell_3_sections_flipped.inp")
debug.search_orientation()
