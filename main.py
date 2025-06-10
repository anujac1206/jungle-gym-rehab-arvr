# rehab_app/main.py
import sys
import os
def main():
    
    print("Current working dir:", os.getcwd())

    print("Choose rehab mode:")
    print("1 - Hand Exercises")
    print("2 - Arm Exercises")
    choice = input("Enter 1 or 2: ").strip()

    if choice == '1':
        import main_hand
        main_hand.run()
    elif choice == '2':
        import main_arm
        main_arm.run()
    else:
        print("Invalid choice, exiting...")
        sys.exit()

if __name__ == "__main__":
    main()
