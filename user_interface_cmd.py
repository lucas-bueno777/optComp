"""
v.1.0.0 - Basic release
Comprises user interaction interface to retrieve optimization parameters
"""
from file_manager import FileProcessor

class UserInterfaceCMD:
    """Main user interaction module"""

    def __init__(self) -> None:
        """Initialization of local variables and FileProcessor instance"""
        self.optcomp_version = "v.1.0.0"
        self.file_processor = FileProcessor()
        self.materials_choosen = []
        self.nset_choosen = ''
        self.elset_choosen = ''
        self.orient_choosen = []
        self.orient_type = []
        self.input_handler = {
            "0": None,
            "1": self.material_input_processing,
            "2": self.step_input_processing,
            "3": self.node_sets_processing,
            "4": self.element_sets_processing,
            "5": self.orientation_processing,
            "6": self.shell_processing,
            "7": self.composite_processing,
            "8": self.solid_processing,
            "9": self.opt_processing
        }

    def material_input_processing(self) -> None:
        """User interaction to define material selection"""
        while True:
            print("\n********** MATERIAL DEFINITION **********")
            print("The materials are:")

            for index, material in enumerate(self.file_processor.materials_list):
                print(f"{index} - {material}")

            print("NEXT - All materials set")
            print("CLEAR - clear current selection")
            print("ALL - Select all materials at once")
            material_input = input(
                "\nPlease select which materials will be included in the optimization: ")

            if material_input.upper() == "NEXT":
                print(f"\nSelected materials = {self.materials_choosen}")
                break

            if material_input.upper() == "CLEAR":
                self.materials_choosen = []
                print("\nList of materials has been cleared")

            elif material_input.upper() == "ALL":
                for i in range(len(self.file_processor.materials_list)):
                    self.materials_choosen.append(i)
                print(f"\nSelected materials = {self.materials_choosen}")
                break

            elif material_input.isdigit() is False:
                print("\nPlease insert only numbers, one at a time")

            elif int(material_input) in self.materials_choosen:
                print("\nMaterial already selected, please choose another one")

            elif int(material_input) in range(len(self.file_processor.materials_list)):
                self.materials_choosen.append(int(material_input))

            else:
                print("Invalid selection.")

    def step_input_processing(self) -> None:
        """User interaction to define step selection"""
        while True:
            print("\n********** STEP DEFINITION **********")
            print("The steps are:")

            for index, steps in enumerate(self.file_processor.steps_list):
                print(f"{index} - {steps}")

            print("At the moment, changes in steps are unavailable. Please use NEXT to return.")
            print("NEXT - All steps set")
            print("CLEAR - clear current selection")
            steps_input = input(
                "\nPlease select which steps will be included in the optimization: ")

            if steps_input.upper() == "NEXT":
                break

            else:
                print("Invalid input.")

    def node_sets_processing(self) -> None:
        """User interaction to define node set selection"""
        while True:
            print("\n********** NODE SETS DEFINITION **********")
            print("The available node sets are:")

            for index, nset in enumerate(self.file_processor.nsets_list):
                print(f"{index} - {nset}")

            print("NEXT - Node set selected")
            print("CLEAR - clear current selection")
            nset_input = input(
                "\nPlease select which node set will be included in the optimization: ")

            if nset_input.upper() == "NEXT":
                print(f"\nSelected node set = {self.nset_choosen}")
                break

            if nset_input.upper() == "CLEAR":
                self.nset_choosen = ''
                print("\nNode set selection has been cleared")

            elif nset_input.isdigit() is False:
                print("\nPlease insert only one number")

            elif int(nset_input) in range(len(self.file_processor.nsets_list)):
                self.nset_choosen = nset_input
                print(f"\nSelected node set = {self.nset_choosen}")
                break

            else:
                print("\nInvalid selection.")

    def element_sets_processing(self) -> None:
        """User interaction to define element set selection"""
        while True:
            print("\n********** ELEMENT SETS DEFINITION **********")
            print("The available element sets are:")

            for index, elset in enumerate(self.file_processor.elsets_list):
                print(f"{index} - {elset}")

            print("NEXT - element set selected")
            print("CLEAR - clear current selection")
            elset_input = input(
                "\nPlease select which element set will be included in the optimization: ")

            if elset_input.upper() == "NEXT":
                print(f"\nSelected element set = {self.elset_choosen}")
                break

            if elset_input.upper() == "CLEAR":
                self.elset_choosen = ''
                print("\nElement set selection has been cleared")

            elif elset_input.isdigit() is False:
                print("\nPlease insert only one number")

            elif int(elset_input) in range(len(self.file_processor.elsets_list)):
                self.elset_choosen = elset_input
                print(f"\nSelected element set = {self.elset_choosen}")
                break

            else:
                print("\nInvalid selection.")

    def orientation_processing(self) -> None:
        """User interaction to define orientation selection and type (discrete/continuous)"""

        # Initialize all orientations as continuous
        self.orient_type = ['CONTINUOUS'] * len(self.file_processor.orientations_list)

        while True:
            print("\n********** ORIENTATIONS DEFINITION **********")
            print("The available orientation cards are:")

            for index, orientation in enumerate(self.file_processor.orientations_list):
                print(f"{index} - [{self.orient_type[index]}] - {orientation}")

            print("NEXT - orientations selected")
            print("CLEAR - clear current selection")
            print("ALL - Include all orientations at once")
            orientation_input = input(
                "\nPlease select an orientation to modify its parameters: ")

            if orientation_input.upper() == "NEXT":
                print(f"\nSelected orientations = {self.orient_choosen}")
                break

            if orientation_input.upper() == "CLEAR":
                self.orient_choosen = []
                print("\nList of orientations to be included has been cleared")

            elif orientation_input.upper() == "ALL":
                self.orient_choosen = []
                for i in range(len(self.file_processor.orientations_list)):
                    self.orient_choosen.append(i)
                print(f"\nSelected orientations = {self.orient_choosen}")
                break

            elif orientation_input.isdigit() is False:
                print("\nPlease insert only numbers, one at a time")

            elif int(orientation_input) in self.orient_choosen:
                print("\nOrientation already selected, please choose another one")

            elif int(orientation_input) in range(len(self.file_processor.orientations_list)):
                while True:
                    inclusion_answer = input("Do you want to include this card? [Y/N]\t")
                    if inclusion_answer.upper() == 'Y':
                        self.orient_choosen.append(int(orientation_input))
                        type_answer = input("Which is the TYPE of this card? [CONTINUOUS/DISCRETE]")
                        if type_answer.upper() == 'DISCRETE' or type_answer.upper() == 'CONTINUOUS':
                            self.orient_type[int(orientation_input)] = type_answer.upper()
                            break
                        print("Invalid entry.")
                        break
                    if inclusion_answer.upper() == 'N':
                        break
                    else:
                        print("Invalid entry.")
                        break

            else:
                print("Invalid selection.")

    def shell_processing(self) -> None:
        pass

    def composite_processing(self) -> None:
        pass

    def solid_processing(self) -> None:
        pass

    def opt_processing(self) -> None:
        pass

    def dialog_file_input(self) -> None:
        """Initialization of user interaction to read the file path"""
        print(f"Welcome to optComp {self.optcomp_version}")

        # Input file processing
        while True:
            file_path = input("Please paste the path to your CalculiX input file (*.inp): ")
            try:
                self.file_processor.read_file(file_path)
                self.file_processor.search_information()
            except TypeError:
                print("The file couldn't be loaded. Check its path, spelling and presence of *.inp")
            else:
                break

    def dialog_analysis_parameters(self) -> None:
        """Dialog of GUI to adjust analysis parameters"""
        while True:
            print("\nSelect one option to adjust the analysis parameters:")
            print("1 - Materials")
            print("2 - Steps")
            print("3 - Node sets")
            print("4 - Element sets")
            print("5 - Orientations")
            print("6 - Shell sections")
            print("7 - Composite sections")
            print("8 - Solid sections")
            print("9 - Optimizer parameters")
            print("NEXT - All parameters set, optimization can start")
            user_option = input("\nEnter your option: ")

            # Handles the user input and warns if invalid entries are given.
            if user_option.isdigit() is False:
                print("\nWARNING: Please insert only a number\n")

            if user_option in self.input_handler:
                self.input_handler[user_option]()

            else:
                print("Invalid input. Try again")

    def main(self) -> None:
        """Main method for execution"""

        self.dialog_file_input()
        self.dialog_analysis_parameters()


if __name__ == "__main__":
    instance = UserInterfaceCMD()
    instance.main()
    # BYPASS = "ccx_files/Wing.inp"
