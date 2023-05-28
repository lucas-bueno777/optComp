def option_one():
    # Function for option one
    print("You selected Option One.")
    # Add your logic for option one here


def option_two():
    # Function for option two
    print("You selected Option Two.")
    # Add your logic for option two here


def main():
    print("Welcome to the CMD program!")
    print("Please select an option:")
    print("1. Option One")
    print("2. Option Two")

    while True:
        choice = input("Enter your choice (1 or 2): ")

        if choice == "1":
            option_one()
            break
        elif choice == "2":
            option_two()
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()