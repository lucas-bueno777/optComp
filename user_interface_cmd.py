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
        self.input_handler = {
            "0": None,
            "1": self.material_input_processing
        }

    def process_file(self, file_path: str) -> None:
        """
        Calls the methods from FileProcessor to read file and search information
        
        Args:
            file_path (str): path of the *.inp file
        """
        self.file_processor.read_file(file_path)
        self.file_processor.search_information()

    def material_input_processing(self) -> None:
        """User interaction to define material selection"""
        while True:
            print("\n********** MATERIAL DEFINITION **********")
            print("The materials are:")

            for index, material in enumerate(self.file_processor.materials_list):
                print(f"{index} - {material}")

            print("NEXT - All materials set")
            print("CLEAR - clear current selection")
            material_input = input(
                "Please select which materials will be included in the optimization: ")

            if material_input.upper() == "NEXT":
                print(f"\nSelected materials = {self.materials_choosen}")
                break

            if material_input.upper() == "CLEAR":
                self.materials_choosen = []
                print("\nList of materials has been cleared")

            elif material_input.isdigit() is False:
                print("\nPlease insert only numbers, one at a time")

            elif int(material_input) in self.materials_choosen:
                print("\nMaterial already selected, please choose another one")

            elif int(material_input) in range(len(self.file_processor.materials_list)):
                self.materials_choosen.append(int(material_input))

    def dialog_file_input(self) -> None:
        """Initialization of user interaction to read the file path"""
        print(f"Welcome to optComp {self.optcomp_version}")

        # Input file processing
        while True:
            file_path = input("Please paste the path to your CalculiX input file (*.inp): ")
            try:
                self.process_file(file_path)
            except TypeError:
                print("The file could not be loaded. Check its path, spelling and presence of .inp")
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
