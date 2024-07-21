def ask_user_yn(message: str):
    while True:
        response = input(f"{message} Y|y|Yes / N|n|No: ").strip().lower()
        if response in ["y", "yes"]:
            return True
        elif response in ["n", "no"]:
            return False
        else:
            print("Invalid input. Please enter Y|y|Yes or N|n|No.")
