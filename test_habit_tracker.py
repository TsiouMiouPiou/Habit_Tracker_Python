from io import StringIO
import pytest
import json
from unittest.mock import patch, mock_open, ANY
from habit_tracker import HabitTracker
from datetime import datetime, timedelta
import os
#  pytest -v test_habit_tracker.py



def setup_module(module):
    """Ensure test_habits.json file exists and is empty before tests."""
    if not os.path.exists("test_habits.json"):
        with open("test_habits.json", "w") as outfile:
            outfile.write("{}")
    else:
        # Clear the content but keep the file
        with open("test_habits.json", "w") as outfile:
            outfile.write("{}")


@pytest.fixture
def setup_habit_tracker():
    """Fixture to create a HabitTracker instance with the test_habits.json file."""
    return HabitTracker("test_habits.json")  # Use test file


@pytest.fixture
def mock_file_open():
    """Mock open function to simulate file read/write."""
    m = mock_open(read_data="{}")
    with patch('builtins.open', m) as mock_file:
        yield mock_file


def test_display_habit_with_data(mock_file_open):
    habit_tracker = HabitTracker("test_habits.json")  # Use test file

    # Sample JSON data to simulate habits
    sample_data = json.dumps({
        "thai": {
            "goal": "5 times per week",
            "time": 60,
            "frequency": "Weekly",
            "created": "06-09-2024 20:41:44",
            "completion": {
                "06-09-2024": "",
                "07-09-2024": "",
                "08-09-2024": "",
                "09-09-2024": "✔️",
                "10-09-2024": "✔️",
                # more dates...
            }
        }
    })




def setup_module(module):
    """Clear the habits.json file before tests."""
    with open("habits.json", "w") as outfile:
        outfile.write("{}")

@pytest.fixture
def setup_habit_tracker():
    """Fixture to create a HabitTracker instance with the habits.json file."""
    return HabitTracker("habits.json")

@pytest.fixture
def mock_file_open():
    """Mock open function to simulate file read/write."""
    m = mock_open(read_data="{}")
    with patch('builtins.open', m) as mock_file:
        yield mock_file

def get_mock_date():
    # Return a fixed datetime for testing
    return datetime.now()

@patch('habit_tracker.datetime')
def test_add_daily_habit(mock_datetime, setup_habit_tracker):
    # Set the mock date to current datetime
    mock_datetime.now.return_value = get_mock_date()

    # Simulate user inputs using questionary
    with patch('questionary.text') as mock_text, patch('questionary.select') as mock_select:
        # Mock user input: habit name "Read a book", 30 minutes, daily habit
        mock_text.return_value.ask.side_effect = ['Read a book', '30']
        mock_select.return_value.ask.return_value = 'daily'

        # Create a habit tracker instance
        habit_tracker = setup_habit_tracker

        # Mock the file writing process
        with patch('builtins.open', mock_open()) as mock_file:
            # Call the addHabit method to add a daily habit
            with patch('sys.stdout', new_callable=StringIO) as fake_out:
                habit_tracker.addHabit()

                # Verify output
                output = fake_out.getvalue()
                assert "Habit 'Read a book' added" in output

            # Aggregate all write calls
            written_data = ''.join(call[0][0] for call in mock_file().write.call_args_list)

            # Ensure data was written to the file
            assert written_data != '{}', "File was not updated with new data"

            # Parse the JSON from the mock file data
            try:
                data = json.loads(written_data)
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
                data = {}

            # Use the actual created date for comparison
            created_date = data["Read a book"]["created"]

            # Expected completion data generation
            expected_data = {
                "Read a book": {
                    "goal": "daily",
                    "time": 30,
                    "frequency": "Daily",
                    "created": created_date,  # Use the actual created date
                    "completion": {
                        (get_mock_date() - timedelta(days=i)).strftime("%d-%m-%Y"): "-"
                        for i in range(1, 29)  # Start from 1 day ago to 28 days ago, leaving today as empty
                    }
                }
            }

            # Print actual and expected data
            print("Actual Data:")
            print(json.dumps(data, indent=4))  # Pretty-print the actual data
            
            print("Expected Data:")
            print(json.dumps(expected_data, indent=4))  # Pretty-print the expected data

            # Check that the data matches the expected format
            assert data == expected_data, f"Data mismatch:\nActual: {json.dumps(data, indent=4)}\nExpected: {json.dumps(expected_data, indent=4)}"

@patch('habit_tracker.datetime')
def test_add_weekly_habit(mock_datetime, setup_habit_tracker):
    # Set the mock date to current datetime
    mock_datetime.now.return_value = get_mock_date()
    
    # Simulate user inputs using questionary
    with patch('questionary.text') as mock_text, patch('questionary.select') as mock_select:
        # Mock user input: habit name "Exercise", 45 minutes, weekly 3 times
        mock_text.return_value.ask.side_effect = ['Exercise', '45', '3']
        mock_select.return_value.ask.return_value = 'weekly'

        # Create a habit tracker instance
        habit_tracker = setup_habit_tracker

        # Mock the file writing process
        with patch('builtins.open', mock_open()) as mock_file:
            # Call the addHabit method to add a weekly habit
            with patch('sys.stdout', new_callable=StringIO) as fake_out:
                habit_tracker.addHabit()

                # Verify output
                output = fake_out.getvalue()
                assert "Habit 'Exercise' added" in output

            # Aggregate all write calls
            written_data = ''.join(call[0][0] for call in mock_file().write.call_args_list)

            # Ensure data was written to the file
            assert written_data != '{}', "File was not updated with new data"

            # Parse the JSON from the mock file data
            try:
                data = json.loads(written_data)
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
                data = {}

            # Use the actual created date for comparison
            created_date = data["Exercise"]["created"]

            # Generate the expected completion data
            today = get_mock_date()
            today_str = today.strftime("%d-%m-%Y")
            start_date = today - timedelta(weeks=4)
            completion = {}

            for i in range(28):
                current_date = start_date + timedelta(days=i)
                date_str = current_date.strftime("%d-%m-%Y")
                if date_str == today_str:
                    completion[date_str] = ""
                else:
                    completion[date_str] = "-"

            expected_data = {
                "Exercise": {
                    "goal": "3 times per week",
                    "time": 45,
                    "frequency": "Weekly",
                    "created": created_date,
                    "completion": completion
                }
            }

            # Check that the data matches the expected format, including the created field
            assert data == expected_data, f"Data mismatch:\nActual: {json.dumps(data, indent=4)}\nExpected: {json.dumps(expected_data, indent=4)}"