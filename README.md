# ✨ Habit Tracker ✨

This project is a Python-based habit tracker that allows users to add, save, delete, and check habits, as well as display the longest streak of each habit. The program uses a JSON file to store habit data, making it easy to track and review progress over time.



* Files 📃  
**habit_tracker.py**: Contains the main habit tracker logic. Run this file to interact with the habit tracker through a menu with seven options, which include adding, viewing, and managing your habits.  
**test_habit_tracker.py**: Unit tests for the habit tracker functions to ensure that each component is working as expected.  
**habits.json**: Stores all added habits along with their checkmarks and creation dates.

* Requirements:  
To ensure that all dependencies are met, please install the following Python packages if they are not already installed:

## Copy code
```bash
pip install tabulate
pip install questionary
pip install pytest
```

# 🚀 How to Run 🚀

Do not forget to change directory:  
```bash
cd Habit_Tracker_Python
```

To use the habit tracker, execute the following command:  

```bash
python habit_tracker.py
```
This will launch the main menu with options to add, check, delete, or analyze your habits.

Run the Tests
To test the project, use the following command in the terminal:

```bash
pytest -s -v test_habit_tracker.py
```

⚠ Note 1 ⚠  
When running the tests, you may be prompted to press Enter to continue during the execution of the last test function. This happens because the test framework waits for an input in the interactive sections of the code (such as with questionary prompts), even if the test doesn't strictly require it. To ensure the test completes successfully, simply press Enter when prompted.    

⚠ Note 2 ⚠  
The displayHabit function shows only the habits for the current week. To view all recorded habits, you need to open the habits.json file directly. Checkmarks in the habits.json file are displayed in Unicode format as \u2714\ufe0f.