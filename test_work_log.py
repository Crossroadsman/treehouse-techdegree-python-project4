import unittest
from unittest.mock import patch
# (see: https://dev.to/patrnk/how-to-test-input-processing-in-python-3)
import datetime

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

    def test_add_entry_returns_main_returns_main_menu(self):
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

    # search_entries

    # quit_program

    # present_results

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