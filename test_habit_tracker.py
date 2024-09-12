import pytest
import json
from unittest.mock import patch, mock_open
from habit_tracker import HabitTracker
import io
from datetime import datetime
# pytest test_habit_tracker.py

@pytest.fixture
def setup_habit_tracker():
    """Fixture to create a HabitTracker instance."""
    return HabitTracker()


def test_display_habit_with_data():
    habit_tracker = HabitTracker()

    # Sample JSON data to simulate habits
    sample_data = json.dumps({
        "thai": {
            "goal": "5 times per week",
            "time": 60,
            "frequency": "Weekly",
            "created": "06-09-2024 / 20:41:44",
            "completion": {
                "06-09-2024": "",
                "07-09-2024": "",
                "08-09-2024": "",
                "09-09-2024": "✔️",
                "10-09-2024": "✔️",
                "11-09-2024": "",
                "12-09-2024": "",
                "13-09-2024": "",
                "14-09-2024": "",
                "15-09-2024": "",
                "16-09-2024": "",
                "17-09-2024": "",
                "18-09-2024": "",
                "19-09-2024": "",
                "20-09-2024": "",
                "21-09-2024": "",
                "22-09-2024": "",
                "23-09-2024": "",
                "24-09-2024": "",
                "25-09-2024": "",
                "26-09-2024": "",
                "27-09-2024": "",
                "28-09-2024": "",
                "29-09-2024": "",
                "03-10-2024": ""
            }
        }
    })

    # Mock the open function and simulate reading the sample JSON data
    with patch("builtins.open", mock_open(read_data=sample_data)):
        # Capture the print output
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            habit_tracker.displayHabit()

            # Retrieve the captured output
            printed_output = fake_out.getvalue()

            # Print the captured output for debugging
            print("Captured Output (With Data):")
            print(printed_output)

            # Check if the habit name "thai" and relevant details are present in the output
            assert "thai" in printed_output
            assert "✔️" in printed_output  # Check for the completion status
            assert "09-09" in printed_output  # Check for specific dates
            assert "10-09" in printed_output  # Check for specific dates



def test_remove_habit(setup_habit_tracker, monkeypatch, capsys):
    tracker = setup_habit_tracker

    # Mock user input for removing a habit
    inputs = iter([
        "3",  # Choose 'Delete a Habit'
        "Daily Exercise",  # Habit to remove
        "exit",  # Exit option
        "1",
        "exit" # Choose 'View all Habits' (to check if habit was removed)
    ])

    def mock_input(prompt):
        try:
            value = next(inputs)
            print(f"Mock Input: '{value}'")  # Debug print statement
            return value
        except StopIteration:
            raise AssertionError("Not enough inputs provided.")

    monkeypatch.setattr('builtins.input', mock_input)

    # Mock the open() function to simulate file handling
    habit_data = {
        "Daily Exercise": {
            "goal": "daily",
            "time": 30,
            "frequency": "Daily",
            "created": "01-09-2024 12:00:00",
            "completion": {}
        }
    }
    mock_file = mock_open(read_data=json.dumps(habit_data))

    with patch('builtins.open', mock_file):
        tracker.selection()  # Start the menu-driven method

    # Check the captured output
    output = capsys.readouterr().out
    assert "Habit 'Daily Exercise' removed" in output
    assert "Daily Exercise" not in output

    # Verify the file contents
    mock_file.assert_called_once_with("w")
    written_data = json.loads(mock_file().write.call_args[0][0])
    assert "Daily Exercise" not in written_data
