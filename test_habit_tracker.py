from io import StringIO
import pytest
import json
from unittest.mock import patch, mock_open, ANY
from habit_tracker import HabitTracker
from datetime import datetime, timedelta
import io

# Command to run the test
#  pytest -s -v test_habit_tracker.py

@pytest.fixture
def mock_file_open():
    """Mock open function to simulate file read/write."""
    m = mock_open(read_data="{}")
    with patch('builtins.open', m) as mock_file:
        yield mock_file

                                                # 1 test_display_habit_with_data()
def test_display_habit_with_data():
    # Adjusted JSON data to match the date range that displayHabit might generate
    sample_data = json.dumps({
        "Gym": {
            "goal": "weekly",
            "time": 40,
            "frequency": "Weekly",
            "created": "22-09-2024 02:02:51",
            "completion": {
                "28-10-2024": "-",
                "29-10-2024": "-",
                "30-10-2024": "-",
                "31-10-2024": "-",
                "01-11-2024": "-",
                "02-11-2024": "-",
                "03-11-2024": "✔️"
            }
        }
    })

    # Mocking the open function to simulate reading from a file
    mock_file = mock_open(read_data=sample_data)
    with patch("builtins.open", mock_file):

        # Redirecting stdout to capture print statements
        with patch("sys.stdout", new_callable=StringIO) as fake_out:
            # Initialize HabitTracker and call displayHabit method
            habit_tracker = HabitTracker("habits.json")
            habit_tracker.displayHabit()

            # Capture the printed output
            output = fake_out.getvalue()

            # Assertions to check for expected output in the printed table
            assert "Gym" in output  # Verify habit name is present
            assert "Monday" in output  # Ensure table headers with dates are present
            assert "\u2714\ufe0f" in output  # Confirm completion mark is displayed for the correct date
            assert "-" in output 


def get_mock_date():
    # Return a fixed datetime for testing
    return datetime.now()


@patch('habit_tracker.datetime')

                                         # 2 test_add_daily_habit

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

            # Print actual and expected data (optional)

            # print("Actual Data:")
            # print(json.dumps(data, indent=4))  # Pretty-print the actual data
            
            # print("Expected Data:")
            # print(json.dumps(expected_data, indent=4))  # Pretty-print the expected data

            # Check that the data matches the expected format
            assert data == expected_data, f"Data mismatch:\nActual: {json.dumps(data, indent=4)}\nExpected: {json.dumps(expected_data, indent=4)}"





                                            # 3 test_add_weekly_habit

def test_add_weekly_habit(setup_habit_tracker):
    # Define the mock date
    mock_date = get_mock_date()
    
    # Patch datetime.now()
    with patch("habit_tracker.datetime") as mock_datetime:
        mock_datetime.now.return_value = mock_date
        
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
                today = mock_date
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


                                                    # 4 test_remove_habit_existing

def test_remove_habit_existing(mock_file_open):
    # Sample JSON data to simulate habits
    sample_data = json.dumps({
        "Meditation": {
            "goal": "daily",
            "time": 30,
            "frequency": "Daily",
            "created": "22-09-2024 02:02:51",
            "completion": {
                "22-09-2024": "-",
                "21-09-2024": "-",
                "20-09-2024": "-"
            }
        }
    })

    # Mock the file read
    mock_file_open.return_value.read.return_value = sample_data

    habit_tracker = HabitTracker("habits.json")  # Use test file

    # Capture the output during the removal
    with patch('sys.stdout', new_callable=StringIO) as fake_out:
        habit_tracker.removeHabit("Meditation")  # Attempt to remove an existing habit

        # Check the write call to ensure data is being written
        mock_file_open.return_value.write.assert_called_once()

        # Get what would be written to the file
        written_data = json.loads(mock_file_open.return_value.write.call_args[0][0])

        # Assertions to verify that the habit was removed
        assert "Meditation" not in written_data  # Ensure the habit is no longer in the data
        assert fake_out.getvalue().strip() == "Habit 'Meditation' removed"  # Check output message

                                            
                                            
                                            # 5 test_remove_habit_non_existing

def test_remove_habit_non_existing(mock_file_open):
    # Sample JSON data to simulate habits
    sample_data = json.dumps({
        "Meditation": {
            "goal": "daily",
            "time": 30,
            "frequency": "Daily",
            "created": "22-09-2024 02:02:51",
            "completion": {
                "22-09-2024": "-",
                "21-09-2024": "-",
                "20-09-2024": "-"
            }
        }
    })

    # Mock the file read
    mock_file_open.return_value.read.return_value = sample_data

    habit_tracker = HabitTracker("habits.json")  # Use test file

    # Capture the output during the removal
    with patch('sys.stdout', new_callable=StringIO) as fake_out:
        habit_tracker.removeHabit("non_existing_habit")  # Attempt to remove a non-existing habit

        # Load the habits to check the content
        with open("habits.json", "r") as infile:
            updated_data = json.load(infile)

        # Assertions to verify that the habit is unchanged
        assert updated_data == json.loads(sample_data)  # Ensure the data remains the same
        assert fake_out.getvalue().strip() == "Habit 'non_existing_habit' not found"  # Check output message


                                # 6  test_check_habit_existing

def test_check_habit_existing():
    # Define the sample data
    sample_data = json.dumps({
        "Meditation": {
            "goal": "daily",
            "completion": {}
        }
    })

    # Define the mock date for this test
    mock_date = datetime(2024, 9, 22)

    # Mock file reading/writing and questionary input
    mock_file = mock_open(read_data=sample_data)

    with patch("builtins.open", mock_file):
        with patch('questionary.text') as mock_questionary:
            mock_questionary.return_value.ask.return_value = "Meditation"  # Simulate user input

            # Mock datetime to return mock_date
            with patch("habit_tracker.datetime") as mock_datetime:
                mock_datetime.now.return_value = mock_date
                mock_datetime.strftime = datetime.strftime

                # Initialize HabitTracker and check the habit
                habit_tracker = HabitTracker("habits.json")
                habit_tracker.checkHabit()

    # Retrieve the data written to the mock file
    written_data = ''.join(call[0][0] for call in mock_file().write.call_args_list)

    # Debug print to verify written data
    # print(f"Written Data: {written_data}")

    # Verify that the habit is marked as completed on the mock date
    updated_data = json.loads(written_data)
    assert updated_data["Meditation"]["completion"]["22-09-2024"] == '✔️'



def test_find_habit_by_periodicity_daily():
    sample_data = json.dumps({
        "yoga": {
            "goal": "daily",
            "completion": {}
        },
        "gym": {
            "goal": "3 times per week",
            "completion": {}
        }
    })

    mock_file = mock_open(read_data=sample_data)

    with patch("builtins.open", mock_file):
        with patch("builtins.input", side_effect=["daily", "exit"]):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                habit_tracker = HabitTracker("habits.json")
                habit_tracker.find_habit_by_periodicity()
                output = fake_out.getvalue()

    assert "Habits with daily periodicity:" in output
    assert "- yoga" in output


                                    
                                    # 8 test_find_habit_by_periodicity_weekly()

def test_find_habit_by_periodicity_weekly():
    sample_data = json.dumps({
        "yoga": {
            "goal": "3 times per week",
            "time": 40,
            "frequency": "Daily",
            "created": "22-09-2024 02:02:51",
            "completion": {
                "22-09-2024": "-",
                "21-09-2024": "-",
                "20-09-2024": "-"
            }
        },
        "gym": {
            "goal": "3 times per week",
            "time": 40,
            "frequency": "Daily",
            "created": "22-09-2024 02:02:51",
            "completion": {
                "22-09-2024": "-",
                "21-09-2024": "-",
                "20-09-2024": "-"
            }
        }
    })

    mock_file = mock_open(read_data=sample_data)

    with patch("builtins.open", mock_file):
        with patch("builtins.input", side_effect=["3", "exit"]):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                habit_tracker = HabitTracker("habits.json")
                habit_tracker.find_habit_by_periodicity()
                output = fake_out.getvalue()

    assert "Habits with 3 periodicity:" in output
    assert "- gym" in output



# # Sample habit data for testing
habit_data = {
    "gym": {
        "goal": "daily",
        "completion": {
            "21-09-2024": "✔️",
            "22-09-2024": "✔️",
            "23-09-2024": "-",
            "24-09-2024": "✔️",
            "25-09-2024": "✔️",
        }
    },
    "yoga": {
        "goal": "daily",
        "completion": {
            "21-09-2024": "✔️",
            "22-09-2024": "✔️",
            "23-09-2024": "✔️",
            "24-09-2024": "-",
            "25-09-2024": "✔️",
        }
    }
}

                                    # 9 test_get_longest_streak(capsys):
 
def test_get_longest_streak(capsys):
    # Mock the JSON file
    mock_file = mock_open(read_data=json.dumps(habit_data))

    with patch("builtins.open", mock_file):
        with patch('builtins.input', side_effect=["gym", "exit"]):
            habit_tracker = HabitTracker("habits.json")
            habit_tracker.get_longest_streak()

    # Capture the output
    captured = capsys.readouterr()

    # Assertions
    assert "Longest streak for 'gym' is 2 days." in captured.out
    assert "Longest streak for 'yoga' is 3 days." not in captured.out  # Ensure it doesn't print this, as we only queried 'gym'



                                                # 10 test_get_longest_streak_of_all_habits

@pytest.fixture
def setup_habit_tracker():
    # Create a temporary habits.json for testing
    test_data = {
        "thai": {
            "goal": "daily",
            "time": 50,
            "frequency": "Daily",
            "created": "30-10-2024 12:00:30",
            "completion": {
                "02-10-2024": "-",
                "03-10-2024": "-",
                "04-10-2024": "-",
                "05-10-2024": "-",
                "06-10-2024": "-",
                "07-10-2024": "-",
                "08-10-2024": "-",
                "09-10-2024": "-",
                "10-10-2024": "-",
                "11-10-2024": "-",
                "12-10-2024": "-",
                "13-10-2024": "-",
                "14-10-2024": "-",
                "15-10-2024": "-",
                "16-10-2024": "-",
                "17-10-2024": "-",
                "18-10-2024": "-",
                "19-10-2024": "-",
                "20-10-2024": "-",
                "21-10-2024": "-",
                "22-10-2024": "-",
                "23-10-2024": "-",
                "24-10-2024": "-",
                "25-10-2024": "-",
                "26-10-2024": "-",
                "27-10-2024": "-",
                "28-10-2024": "-",
                "29-10-2024": "✔️",
                "30-10-2024": "✔️"
            }
        },
        "yoga": {
            "goal": "3 times per week",
            "time": 40,
            "frequency": "Weekly",
            "created": "30-10-2024 12:05:59",
            "completion": {
                "02-10-2024": "-",
                "03-10-2024": "-",
                "04-10-2024": "-",
                "05-10-2024": "-",
                "06-10-2024": "-",
                "07-10-2024": "-",
                "08-10-2024": "-",
                "09-10-2024": "-",
                "10-10-2024": "-",
                "11-10-2024": "-",
                "12-10-2024": "-",
                "13-10-2024": "-",
                "14-10-2024": "-",
                "15-10-2024": "-",
                "16-10-2024": "-",
                "17-10-2024": "-",
                "18-10-2024": "✔️",
                "19-10-2024": "✔️",
                "20-10-2024": "",
                "21-10-2024": "-",
                "22-10-2024": "-",
                "23-10-2024": "-",
                "24-10-2024": "-",
                "25-10-2024": "-",
                "26-10-2024": "-",
                "27-10-2024": "✔️",
                "28-10-2024": "✔️",
                "29-10-2024": "✔️"
            }
        }
    }

    with open("habits.json", "w") as outfile:
        json.dump(test_data, outfile)

    # Initialize the HabitTracker with the test file
    habit_tracker = HabitTracker("habits.json")
    yield habit_tracker  # This will pass the habit_tracker to the test function

    # Clean up after tests
    import os
    os.remove("habits.json")


def test_get_longest_streak_of_all_habits(setup_habit_tracker, capsys):
    habit_tracker = setup_habit_tracker

    # Debug: Verify that JSON data is loading properly
    print("Loaded habits:", habit_tracker.habitDictionary)  # Should show "thai" and "yoga"

    # Call the method that calculates the longest streak
    habit_tracker.get_longest_streak_of_all_habits()

    # Capture the output
    captured = capsys.readouterr()

    #  Debug: print captured output
    # print("Captured Output:", captured.out)

    # Check for 'thai' in the captured output
    assert "thai" in captured.out  # Ensure 'thai' habit is included
    assert "yoga" in captured.out  # Ensure 'yoga' habit is included

    assert "Longest Streak" in captured.out  # Check if "Longest Streak" header exists