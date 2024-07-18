def user_confirmation():
    while True:
        response = input("Do you want to continue Y|y|Yes / N|n|No: ").strip().lower()
        if response in ["y", "yes"]:
            return True
        elif response in ["n", "no"]:
            return False
        else:
            print("Invalid input. Please enter Y|y|Yes or N|n|No.")
