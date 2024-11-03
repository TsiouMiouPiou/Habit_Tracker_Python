from datetime import datetime, timedelta
import json
from tabulate import tabulate
import questionary
import os

class HabitTracker:

    def __init__(self, file_path):
        self.file_path = file_path
        self.habitDictionary = self.loadHabits()

    def loadHabits(self):
        try:
            if not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0:
                return {}
            else:
                with open(self.file_path, "r") as infile:
                    return json.load(infile)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}  # Initialize an empty dictionary if the file is missing or malformed

    def start(self):
        self.selection()

    # 1 VIEW ALL HABITS
    def displayHabit(self):
        # List of days for the week
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # Calculate the start of the current week (Monday)
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())  # Monday of the current week

        # Create headers for each day of the week with respective dates
        headers = ["Habit Name"] + [f" {days[i]} { (start_of_week + timedelta(days=i)).strftime('%d-%m') }" for i in range(7)]

        # Create a list to hold the rows for the table
        habit_data = []

        try:
            with open("habits.json", "r") as readFile:
                if readFile.readable() and readFile.seek(0, 2) == 0:
                    print("No habits found.")
                    return  # Do not call self.selection() during tests
                else:
                    readFile.seek(0)  # Go back to the beginning of the file
                    json_object = json.load(readFile)
                    if not json_object:
                        print("The habits file is empty or corrupted.")
                        return

            # Create a list of all habits with their completion status for each day
            for habit, details in json_object.items():
                row = [habit]
                for i in range(7):  # For each day of the week
                    day = start_of_week + timedelta(days=i)
                    date_str = day.strftime("%d-%m-%Y")  # Match this with your chosen date format
                    completion_status = details["completion"].get(date_str, "")
                    row.append(completion_status)

                habit_data.append(row)

            # Print the table
            print(tabulate(habit_data, headers=headers, tablefmt="grid", colalign=("left", "center", "center", "center", "center", "center", "center", "center")))

        except FileNotFoundError:
            print("No habits found. The file does not exist.")
        except json.JSONDecodeError:
            print("The habits file is empty or corrupted. No habits to display.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        

    # 2 ADD A NEW HABIT
    def addHabit(self):
        # Load existing habits
        try:
            with open(self.file_path, "r") as infile:
                self.habitDictionary = json.load(infile)
        except (FileNotFoundError, json.JSONDecodeError):
            self.habitDictionary = {}

        fully_defined = False

        while not fully_defined:
            # Capture habit name with validation
            habit = questionary.text("Add a habit or type 'exit' to Main Menu: ").ask()

            if habit.lower() == "exit":
                self.selection()  # Exit the method

            # Validate habit name
            if not habit.strip() or habit.startswith("&") or "python" in habit.lower():
                print("Invalid habit name. Please enter a descriptive name without special command-like characters.")
                continue  # Skip the rest of the loop and prompt again

            # Proceed to gather other details if the habit name is valid
            goal = questionary.select("Select your goal:", choices=["daily", "weekly"]).ask()
            start_date = datetime.now()
            weeks_ago = start_date - timedelta(weeks=4)
            completion = { (weeks_ago + timedelta(days=i)).strftime("%d-%m-%Y"): "-" for i in range(28) }
            creation_date_str = start_date.strftime("%d-%m-%Y %H:%M:%S")

            if goal == "daily":
                time = questionary.text("Enter time per day in minutes: ", validate=lambda text: text.isdigit()).ask()
                self.habitDictionary[habit] = {
                    "goal": "daily",
                    "time": int(time),
                    "frequency": "Daily",
                    "created": creation_date_str,
                    "completion": completion
                }
                fully_defined = True

            elif goal == "weekly":
                time = questionary.text("Enter time per day in minutes: ", validate=lambda text: text.isdigit()).ask()
                times_per_week = questionary.text("How many times per week do you want to do this habit? (1-7): ", 
                                                validate=lambda text: text.isdigit() and 1 <= int(text) <= 7).ask()
                self.habitDictionary[habit] = {
                    "goal": f"{times_per_week} times per week",
                    "time": int(time),
                    "frequency": "Weekly",
                    "created": creation_date_str,
                    "completion": completion
                }
                fully_defined = True

        # Save updated habits to JSON
        try:
            with open(self.file_path, "w") as outfile:
                json.dump(self.habitDictionary, outfile, indent=4)
            print(f"Habit '{habit}' added successfully.")
        except IOError as e:
            print(f"Error writing to file: {e}")

        
       
    #  3 Remove a habit       
    def removeHabit(self, habitName):
        try:
            with open("habits.json", "r") as infile:
                habitDictionary = json.load(infile)
        except FileNotFoundError:
            habitDictionary = {}
        except json.JSONDecodeError:
            habitDictionary = {}

        if habitName in habitDictionary:
            habitDictionary.pop(habitName)
            print(f"Habit '{habitName}' removed")
        else:
            print(f"Habit '{habitName}' not found")

        with open("habits.json", "w") as writeFile:
            json.dump(habitDictionary, writeFile)


    # 4 COMPLETION - Check Habit
    def checkHabit(self):
        try:
         with open("habits.json", "r") as infile:
            habitDictionary = json.load(infile)
        except (FileNotFoundError, json.JSONDecodeError):
            return

        fully_defined = False  # Control variable for the loop

        while not fully_defined:
            habitName = questionary.text("Enter the name of the habit you want to check off or press 'exit' to Main Menu:").ask().strip()
            
            if habitName.lower() == "exit":
                self.selection()
                fully_defined = True  # Exit the loop if user chooses to go to the main menu

            elif habitName in habitDictionary:
                current_date = datetime.now().strftime("%d-%m-%Y")
                habitDictionary[habitName]["completion"][current_date] = '✔️'
                print(f"Habit '{habitName}' is checked off for {current_date}")
                fully_defined = True  # Exit the loop after checking off a habit

            else:
                print(f"Habit '{habitName}' not found. Please try again.")

        # Write the updated habits back to the file
        with open("habits.json", "w") as writeFile:
            json.dump(habitDictionary, writeFile, indent=4)


    # 5 Periodicity habits
    def find_habit_by_periodicity(self):
        try:
            with open("habits.json", "r") as infile:
                habitDictionary = json.load(infile)
        except (FileNotFoundError, json.JSONDecodeError):
            print("No habits file found or error decoding JSON.")
            return

        fully_defined = False

        while not fully_defined:
            user_input = input("Enter the desired periodicity ('1 - 7' for weekly / 'daily' for daily) or 'exit' to Main Menu: ")

            if user_input.lower() == "exit":
                self.selection()
                return  # Exit the function after returning to the main menu

            periodicity_list = []

            if user_input.lower() == "daily":
                for habit, details in habitDictionary.items():
                    if details["goal"] == "daily":
                        periodicity_list.append(habit)

            else:
                try: # Enter 1-7 to check which habits are included at the specific range
                    periodicity = int(user_input)
                    if 1 <= periodicity <= 7:
                        for habit, details in habitDictionary.items():
                            if details["goal"] == f"{periodicity} times per week":
                                periodicity_list.append(habit)
                    else:
                        print("Invalid number. Enter a number between 1 and 7.")
                        continue
                except ValueError:
                    print("Invalid input. Please try again.")
                    continue

            if periodicity_list:
                print(f"Habits with {user_input} periodicity:")
                for habit in periodicity_list:
                    print("- " + habit)
                fully_defined = True  # Set to True to exit the loop
            else:
                print("No habits found with the desired periodicity.")



    # 6 Return streak
    def get_longest_streak(self):
        fully_defined = False

        while not fully_defined:
            habit_name = input("Enter the name of the habit you want to check the longest streak for or type 'exit' to Main Menu: ").strip()

            if habit_name.lower() == "exit":
                self.selection()
                return

            try:
                with open("habits.json", "r") as infile:
                    habitDictionary = json.load(infile)
            except (FileNotFoundError, json.JSONDecodeError):
                print("No habits file found or error decoding JSON.")
                continue

            if habit_name not in habitDictionary:
                print(f"Habit '{habit_name}' not found.")
                continue

            habit_details = habitDictionary[habit_name]
            completion = habit_details["completion"]

            streak = 0
            max_streak = 0
            for date_str, status in completion.items():
                if status == "✔️":
                    streak += 1
                else:
                    max_streak = max(max_streak, streak)
                    streak = 0  # Reset streak if there's a missed day

            # The final comparison after the loop
            max_streak = max(max_streak, streak)

            print(f"Longest streak for '{habit_name}' is {max_streak} days.")
            fully_defined = True  # Set to True to exit the loop


    def get_longest_streak_of_all_habits(self, testing_mode=False):
        try:
            with open(self.file_path, "r") as infile:
                self.habitDictionary = json.load(infile)  # Load data into the class attribute
        except FileNotFoundError:
            print("No habits file found")
            return
        except json.JSONDecodeError:
            print("Error decoding JSON.")
            return

        results = []

        for habit_name, details in self.habitDictionary.items():  
            goal = details["goal"]
            completion_data = details["completion"]

            if "times per week" in goal:

                # Extract the number of times a habit should be completed per week
                times_per_week = int(goal.split()[0])
                # Weekly habits
                current_streak = 0
                longest_streak = 0
                completion_dates = sorted(completion_data.keys(), key=lambda x: datetime.strptime(x, "%d-%m-%Y"))

                week_start = datetime.strptime(completion_dates[0], "%d-%m-%Y")
                end_date = datetime.strptime(completion_dates[-1], "%d-%m-%Y")

                # Iterate over weeks, starting from 'week_start' and moving in weekly increments
                while week_start <= end_date:
                    # Define the end of the current week (6 days after the start of the week)
                    week_end = week_start + timedelta(days=6)
                    # Initialize a counter to track the number of completions within the week
                    week_completions = 0

                     # Check each date in the list of completion dates
                    for date_str in completion_dates:
                        current_date = datetime.strptime(date_str, "%d-%m-%Y")
                        if week_start <= current_date <= week_end and completion_data[date_str] == '✔️':
                            week_completions += 1

                     # Check if the weekly completions meet or exceed the required frequency (times_per_week)
                    if week_completions >= times_per_week:
                        current_streak += 1
                    else:
                        current_streak = 0

                    longest_streak = max(longest_streak, current_streak)
                    week_start += timedelta(days=7)

                results.append((habit_name, longest_streak if longest_streak > 0 else '-', 'weekly'))

            elif goal == "daily":
                # Daily habits
                completion_dates = sorted(completion_data.keys(), key=lambda x: datetime.strptime(x, "%d-%m-%Y"))

                current_streak = 0
                longest_streak = 0

                for date_str in completion_dates:
                    if completion_data[date_str] == '✔️':
                        current_streak += 1
                        longest_streak = max(longest_streak, current_streak)
                    else:
                        current_streak = 0

                results.append((habit_name, longest_streak if longest_streak > 0 else '-', 'daily'))

            else:
                results.append((habit_name, '-', 'unknown'))

        # Print results
        print(f"{'Habit Name':<15} {'Longest Streak':<18} {'Goal Type':<10}")
        print("-" * 45)
        for habit_name, streak, goal_type in results:
            print(f"{habit_name:<20} {str(streak):<15} {goal_type:<10}")

        # Skip prompt if in testing mode
        if not testing_mode:
            user_input = input("\nType 'exit' to return to the main menu or press Enter to check again: ").strip().lower()
            if user_input == 'exit':
                return self.selection()  # Call the main menu function



    # Main menu logic

    def selection(self):
      try:
            case = questionary.select(
                  "---Main Menu---",
                  choices=[
                  "1. View all Habits",
                  "2. Add a new Habit",
                  "3. Delete a Habit",
                  "4. Check a Habit",
                  "5. Return a periodicity list",
                  "6. Get the longest streak",
                  "7. Get all streaks",
                  ]).ask()

            if case == "1. View all Habits":
                  self.displayHabit()
            elif case == "2. Add a new Habit":
                  self.addHabit()
            elif case == "3. Delete a Habit":
                  while True:
                        habitToRemove = questionary.text("Enter the name of the habit to remove or type 'exit' to Main Menu:").ask().strip()
                        if habitToRemove.lower() == "exit":
                              self.selection()
                              break
                        else:
                         self.removeHabit(habitToRemove)
            elif case == "4. Check a Habit":
                  self.checkHabit()
            elif case == "5. Return a periodicity list":
                  self.find_habit_by_periodicity()
            elif case == "6. Get the longest streak":
                  self.get_longest_streak()
            elif case == "7. Get all streaks":
                  self.get_longest_streak_of_all_habits()
      except ValueError:
            print("Enter a valid option")
            self.selection()

if __name__ == "__main__":
    file_path = "habits.json"  # Path to habits file
    tracker = HabitTracker(file_path)
    tracker.selection()  # Call the selection() function to pop up the Main Menu

# Utility function to check if pytest is running
def pytest_running():
    import sys
    return 'pytest' in sys.modules
