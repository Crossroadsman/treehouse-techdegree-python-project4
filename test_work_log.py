import io
import sys
import unittest
from unittest.mock import patch
# (see: https://dev.to/patrnk/how-to-test-input-processing-in-python-3)
import datetime
from collections import OrderedDict

from peewee import *

import work_log
import db_manager
import wl_settings as settings


class MenuTests(unittest.TestCase):
    """This class has tests for work_log.py.

    Note that some code paths in db_manager.py would likely never be
    encountered when running work_log (e.g., various errors) so coverage
    for db_manager is going to be inadequate if just testing work_log.

    Need to also run the tests in test_db_manager.py
    """
    # Helper Methods
    # --------------
    def set_test_database(self):
        """Switch out the regular database and switch in a unittest-only
        database
        """
        db_manager.db = SqliteDatabase(settings.UNITTEST_DATABASE_NAME)
        db_manager.Employee._meta.database = db_manager.db
        db_manager.LogEntry._meta.database = db_manager.db

    def revert_database(self):
        """Switch back to regular database"""
        # make sure that in unittest database
        db_manager.db = SqliteDatabase(settings.UNITTEST_DATABASE_NAME)
        db_manager.Employee._meta.database = db_manager.db
        db_manager.LogEntry._meta.database = db_manager.db
        
        # delete all test data
        q = db_manager.LogEntry.delete()
        q.execute()
        q = db_manager.Employee.delete()
        q.execute()

        # switch back to live database
        db_manager.db = SqliteDatabase(settings.LIVE_DATABASE_NAME)
        db_manager.Employee._meta.database = db_manager.db
        db_manager.LogEntry._meta.database = db_manager.db

    # Setup and Teardown
    # ------------------
    def setUp(self):
        self.set_test_database()
        self.menu = work_log.Menu(load_menu=False)
    
    def tearDown(self):
        self.revert_database()
    
    # Example Tests
    # -------------

    # Actual Tests
    # ------------

    # main_menu
    def test_main_menu_selection_returns_correct_menu(self):
        """Ensure that the main menu loads the correct menu in response to
        user input.
        """
        user_inputs = {
            'a': self.menu.add_entry,
            's': self.menu.search_entries,
            'o': self.menu.options,
            'q': self.menu.quit_program,
        }
        results = []
        expected_results = []
        for key, value in user_inputs.items():
            expected_results.append(value)
            with patch('builtins.input', side_effect=key):
                results.append(self.menu.main_menu())
        
        self.assertEqual(expected_results, results)

    # add_entry
    def test_add_entry_creates_db_entry_with_correct_details(self):
        """Ensure that the add entry menu creates a record with the entered
        details
        """
        example_inputs = [
            'Example Employee',
            '2018-05-01',
            'Example Task',
            100,
            'Example Note'
        ]
        with patch('builtins.input', side_effect=example_inputs):
            self.menu.add_entry()
        
        query = (db_manager
            .LogEntry
            .select()
            .join(db_manager.Employee)
            .where(
                db_manager.Employee.name == example_inputs[0],
                db_manager.LogEntry.date == example_inputs[1],
                db_manager.LogEntry.task_name == example_inputs[2],
                db_manager.LogEntry.duration == example_inputs[3],
                db_manager.LogEntry.notes == example_inputs[4]
            ))
        record = query[0]
        record_data = [
            record.employee.name,
            record.date.strftime("%Y-%m-%d"),
            record.task_name,
            record.duration,
            record.notes
        ]
        self.assertEqual(example_inputs, record_data)

    def test_add_entry_returns_main_menu(self):
        """Ensure that the add_entry menu finishes by returning main_menu
        """
        example_inputs = [
            'Example Employee',
            '2018-05-01',
            'Example Task',
            100,
            'Example Note'
        ]
        with patch('builtins.input', side_effect=example_inputs):
            returned_menu = self.menu.add_entry()
        
        self.assertEqual(returned_menu, self.menu.main_menu)
        
    # options
    def test_options_date_format_choice_updates_settings(self):
        """Ensure that the options menu sets the correct settings in response
        to user input.
        """
        user_inputs = settings.DATE_FORMATS.keys()
        results = []
        expected_results = list(settings.DATE_FORMATS.values())
        for i in range(1, len(user_inputs) + 1):
            with patch('builtins.input', side_effect=str(i)):
                self.menu.options()
                results.append(self.menu.OPTIONS['date format'])
        
        self.assertEqual(results, expected_results)        
    
    def test_options_returns_main_menu(self):
        """Ensure that the options menu finishes by returning main_menu
        """
        example_input = '1'
        with patch('builtins.input', side_effect=example_input):
            returned_menu = self.menu.options()
        
        self.assertEqual(returned_menu, self.menu.main_menu)
        

    # search_entries
    def test_search_entries_returns_correct_menu(self):
        """Ensure that the search_entries menu loads the correct menu in
        response to user input.
        """
        user_inputs = {
            'l': self.menu.search_employee,
            'e': self.menu.search_employee_text,
            'd': self.menu.search_exact_date,
            'r': self.menu.search_date_range,
            't': self.menu.search_time_spent,
            's': self.menu.search_text_search,
            'b': self.menu.main_menu,
        }
        results = []
        expected_results = []
        for key, value in user_inputs.items():
            expected_results.append(value)
            with patch('builtins.input', side_effect=key):
                results.append(self.menu.search_entries())
        
        self.assertEqual(expected_results, results)

    # quit_program
    def test_quit_program_sets_quit_status_to_true(self):
        """Ensure that the quit function sets the program's quit state to
        True
        """
        self.menu.quit_program()
        self.assertTrue(self.menu.quit)

    # present_results
    def test_present_results_displays_results(self):
        # to test this we don't actually need to write to the database,
        # we just need a list of ordered_dicts in menu.records
        # Add an entry to the database
        test_records = [
            OrderedDict([
                ('name', 'Test Employee 1'),
                ('date', datetime.date(2018,5,1)),
                ('task_name', 'Test Task 1'),
                ('duration', 1),
                ('notes', 'This is a note for the first test task')
            ]),
            OrderedDict([
                ('name', 'Test Employee 2'),
                ('date', datetime.date(2018,5,2)),
                ('task_name', 'Test Task 2'),
                ('duration', 2),
                ('notes', 'This is a note for the second test task')
            ]),
        ]
        self.menu.records = [test_records[0]]
        f_username = test_records[0]['name']
        f_date = test_records[0]['date'].strftime("%Y-%m-%d")
        f_time_taken = str(test_records[0]['duration'])
        f_task_name = test_records[0]['task_name']
        f_notes = test_records[0]['notes']
        short_form = "{}: {} ({}m): {} | {}".format(
            f_username,
            f_date,
            f_time_taken,
            f_task_name,
            f_notes
        )
        expected_output = ("\nSearch Results\n" + 
                           "1) {}\n".format(short_form) +
                           "\n" +
                           "Available actions:\n" +
                           "v) View detail\n" +
                           "e) Edit\n" +
                           "d) Delete\n" +
                           "m) go back to Main menu\n" +
                           "q) quit\n")

        '''The process for capturing `print()` statements and redirecting to
        an accumulating object for later processing has the following steps:
        1. import io and sys
        2. in the test function, create a StringIO object
           (this is a buffer object that will be the destination for the
            redirected stdout)
           ```
           captured_output = io.StringIO()
           ```
        3. point stdout at the capture object
           ```
           sys.stdout = captured_output
           ```
        4. Run code as normal, any print() statement will go to 
           the StringIO object instead of standard out
        5. Revert stdout (will not affect the contents of the StringIO buffer)
           ```
           sys.stdout = sys.__stdout__
           ```
        6. Run the rest of the code. The contents of the StringIO buffer can
           be accessed as follows:
           ```
           captured_output.getvalue()
           ```
        '''
        # Create a StringIO object to be a capture object
        captured_output = io.StringIO()
        # point stdout at the capture object
        sys.stdout = captured_output
        # Do anything that's going to have a print statement
        # (these will be accumulated in the captured_output object)
        example_input = 'q'
        with patch('builtins.input', side_effect=example_input):
            self.menu.present_results()

        # Revert stdout (captured_output still holds the captured items)
        sys.stdout = sys.__stdout__
        # Do any other test code (e.g., asserts)
        self.assertEqual(expected_output, captured_output.getvalue())

    def test_present_results_loads_correct_next_menu(self):
        # this can be just like the previous tests that return menus
        # with the only wrinkle that we need to handle the different 
        # values for self.menu.current_page_start do determine whether
        # next or previous menus are available
        # Add an entry to the database
        '''
        test_employee_data = {'name': 'Test Employee'}
        test_log_entry_data = {
            'employee': test_employee_data,
            'date': datetime.date(2018,5,1),
            'task_name': 'Test task',
            'duration': 1,
            'notes': 'This is a note for a test task',
        }
        test_employee_record = db_manager.Employee.get_or_create(
            name=test_employee_data['name']
        )
        test_log_entry_record = db_manager.LogEntry.create(
            employee=test_employee_record[0],
            date=test_log_entry_data['date'],
            task_name=test_log_entry_data['task_name'],
            duration=test_log_entry_data['duration'],
            notes=test_log_entry_data['notes']
        )
        self.menu.records = [test_log_entry_record]
        f_username = test_employee_data['name']
        f_date = test_log_entry_data['date'].strftime("%Y-%m-%d")
        f_time_taken = str(test_log_entry_data['duration'])
        f_task_name = test_log_entry_data['task_name']
        f_notes = test_log_entry_data['notes']
        short_form = "{}: {} ({}m) {} | {}".format(
            f_username,
            f_date,
            f_time_taken,
            f_task_name,
            f_notes
        )
        expected_output = ("\nSearch Results\n" + 
                           "1) {}\n".format(short_form))
        '''
        pass

    # present_next_result

    # search_employee

    # search_employee_text

    # search_exact_date

    # search_date_range

    # search_time_spent

    # search_text_search

    # edit_record

    # edit_current_record

    # select_detail

    # delete_record

    # delete_current_record

    # display_entry

    # previous_result

    # next_result

    # previous_page

    # next_page

    # validate_date_entry

    # date_entry

    # date_to_string

# ------------------------

if __name__ == "__main__":
    unittest.main()