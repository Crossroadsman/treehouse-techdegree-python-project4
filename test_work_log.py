"""Test DB Manager
Unit Tests for work_log.py

Created: 2018
Last Update: 2018-05-30
Author: Alex Koumparos
"""
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
        """Ensure that what is displayed to the user is what we expect to
        be displayed to the user.
        """
        # to test this we don't actually need to write to the database,
        # we just need a list of ordered_dicts in menu.records
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
        """Ensure that what is displayed to the user is what we expect to
        be displayed to the user.
        """
        # to test this we don't actually need to write to the database,
        # we just need a list of ordered_dicts in menu.records
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
            OrderedDict([
                ('name', 'Test Employee 3'),
                ('date', datetime.date(2018,5,3)),
                ('task_name', 'Test Task 3'),
                ('duration', 3),
                ('notes', 'This is a note for the third test task')
            ]),
        ]
        old_entries_per_page = self.menu.OPTIONS['entries per page']
        self.menu.OPTIONS['entries per page'] = 1
        self.menu.records = test_records
        self.menu.current_page_start = 1
        user_inputs = {
            'n': self.menu.next_page,
            'p': self.menu.previous_page,
            'v': self.menu.select_detail,
            'e': self.menu.edit_record,
            'd': self.menu.delete_record,
            'm': self.menu.main_menu,
            'q': self.menu.quit_program,
        }
        results = []
        expected_results = []
        for key, value in user_inputs.items():
            expected_results.append(value)
            with patch('builtins.input', side_effect=key):
                results.append(self.menu.present_results())
        
        self.assertEqual(expected_results, results)
        self.menu.OPTIONS['entries per page'] = old_entries_per_page

    # present_next_result
    def test_present_next_result_displays_result(self):
        """Ensure that what is displayed to the user is what we expect to
        be displayed to the user.
        """
        # to test this we don't actually need to write to the database,
        # we just need a list of ordered_dicts in menu.records
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
            OrderedDict([
                ('name', 'Test Employee 3'),
                ('date', datetime.date(2018,5,3)),
                ('task_name', 'Test Task 3'),
                ('duration', 3),
                ('notes', 'This is a note for the third test task')
            ]),
        ]
        self.menu.records = test_records
        self.menu.current_record = 1
        line0 = test_records[1]['name'] + "\n"
        f_date = test_records[1]['date'].strftime("%Y-%m-%d")
        f_task_name = test_records[1]['task_name']
        line1 = "{}: {}".format(f_date, f_task_name)
        line2 = "\n" + ("-" * len(line1)) + "\n"
        f_time_taken = str(test_records[1]['duration'])
        line3 = "{} minutes\n".format(f_time_taken)
        line4 = "{}\n".format(test_records[1]['notes'])
        long_form = (line0 +
                     line1 +
                     line2 +
                     line3 +
                     line4
        )
        expected_output = (long_form +
                           "\n" +
                           "Available actions:\n" +
                           "p) Previous\n" +
                           "n) Next\n" +
                           "b) Back to list view\n" +
                           "e) Edit\n" +
                           "d) Delete\n" +
                           "m) go back to Main menu\n" +
                           "q) quit\n")

        # Create a StringIO object to be a capture object
        captured_output = io.StringIO()
        # point stdout at the capture object
        sys.stdout = captured_output
        # Do anything that's going to have a print statement
        # (these will be accumulated in the captured_output object)
        example_input = 'q'
        with patch('builtins.input', side_effect=example_input):
            self.menu.present_next_result()

        # Revert stdout (captured_output still holds the captured items)
        sys.stdout = sys.__stdout__
        # Do any other test code (e.g., asserts)
        self.assertEqual(expected_output, captured_output.getvalue())

    def test_present_next_result_loads_correct_next_menu(self):
        """Ensure that the correct next menu is loaded.
        """
        # this can be just like the previous tests that return menus
        # with the only wrinkle that we need to handle the different 
        # values for self.menu.current_page_start do determine whether
        # next or previous menus are available
        # Add an entry to the database
        
        # to test this we don't actually need to write to the database,
        # we just need a list of ordered_dicts in menu.records
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
            OrderedDict([
                ('name', 'Test Employee 3'),
                ('date', datetime.date(2018,5,3)),
                ('task_name', 'Test Task 3'),
                ('duration', 3),
                ('notes', 'This is a note for the third test task')
            ]),
        ]
        self.menu.records = test_records
        self.menu.current_record = 1
        user_inputs = {
            'n': self.menu.next_result,
            'p': self.menu.previous_result,
            'b': self.menu.present_results,
            'e': self.menu.edit_current_record,
            'd': self.menu.delete_current_record,
            'm': self.menu.main_menu,
            'q': self.menu.quit_program,
        }
        results = []
        expected_results = []
        for key, value in user_inputs.items():
            expected_results.append(value)
            with patch('builtins.input', side_effect=key):
                results.append(self.menu.present_next_result())
        
        self.assertEqual(expected_results, results)
        
    # search_employee
    def test_search_employee_displays_employee_names(self):
        """Ensure that what is displayed to the user is what we expect to
        be displayed to the user.
        """
        # add some data to the database
        test_employees = [
            {'id': 1, 'name': "Test Employee 1"},
            {'id': 2, 'name': "Test Employee 2"}
        ]
        for employee in test_employees:
            e = db_manager.Employee.get_or_create(name=employee['name'])
            # give each employee an associated logentry
            db_manager.LogEntry.create(
                employee=e[0],
                date=datetime.date(2018,1,2),
                task_name='Test task {}'.format(employee['id']),
                duration=employee['id'],
                notes='Note'
            )

        title = "\nSEARCH BY EMPLOYEE" + "\n"
        employee_rows = ""
        for employee in test_employees:
            employee_rows += "{}) {}\n".format(employee['id'], 
                                               employee['name'])
        
        expected_output = (title +
                           employee_rows)

        # Create a StringIO object to be a capture object
        captured_output = io.StringIO()
        # point stdout at the capture object
        sys.stdout = captured_output
        # Do anything that's going to have a print statement
        # (these will be accumulated in the captured_output object)
        example_input = '1'
        with patch('builtins.input', side_effect=example_input):
            self.menu.search_employee()

        # Revert stdout (captured_output still holds the captured items)
        sys.stdout = sys.__stdout__
        # Do any other test code (e.g., asserts)
        self.assertEqual(expected_output, captured_output.getvalue())
        

    def test_search_employee_returns_the_correct_menu(self):
        """Ensure that the correct next menu is loaded.
        """
        # add some employees to the database
        test_employees = [
            {'id': 1, 'name': "Test Employee 1"},
            {'id': 2, 'name': "Test Employee 2"}
        ]
        for employee in test_employees:
            e = db_manager.Employee.get_or_create(name=employee['name'])
            # give each employee an associated logentry
            db_manager.LogEntry.create(
                employee=e[0],
                date=datetime.date(2018,1,2),
                task_name='Test task {}'.format(employee['id']),
                duration=employee['id'],
                notes='Note'
            )
        user_input='1'
        with patch('builtins.input', side_effect=user_input):
            result = self.menu.search_employee()
        
        expected_result = self.menu.present_next_result
        
        self.assertEqual(expected_result, result)

    # search_employee_text
    def test_search_employee_text_finds_matching_employees(self):
        """Ensure that all matching employees are displayed and no non-
        matching employees are displayed
        """
        # add some employees to the database
        test_pattern = 'foo'
        test_employees = [
            {'id': 1, 'name': "Test Employee 1 foo"},
            {'id': 2, 'name': "Test Employee 2 foo"},
            {'id': 3, 'name': "Test Employee 3 bar"},
        ]
        for employee in test_employees:
            e = db_manager.Employee.get_or_create(name=employee['name'])
            db_manager.LogEntry.create(
                employee=e[0],
                date=datetime.date(2018,1,2),
                task_name='Test task {}'.format(employee['id']),
                duration=employee['id'],
                notes='Note')

        title = "FIND EMPLOYEE NAME USING TEXT STRING" + "\n"
        subtitle = "Enter the text string to search on" + "\n"
        employee_rows = ""
        for employee in test_employees:
            if test_pattern in employee['name']:
                employee_rows += "{}) {}\n".format(employee['id'], 
                                                   employee['name'])
        
        expected_output = (title +
                           subtitle +
                           employee_rows)

        # Create a StringIO object to be a capture object
        captured_output = io.StringIO()
        # point stdout at the capture object
        sys.stdout = captured_output
        # Do anything that's going to have a print statement
        # (these will be accumulated in the captured_output object)
        example_input = [test_pattern, '1']
        with patch('builtins.input', side_effect=example_input):
            self.menu.search_employee_text()

        # Revert stdout (captured_output still holds the captured items)
        sys.stdout = sys.__stdout__
        # Do any other test code (e.g., asserts)
        self.assertEqual(expected_output, captured_output.getvalue())
        
    def test_search_employees_returns_correct_menu(self):
        """Ensure that the correct next menu is loaded.
        """
        # add some employees to the database
        test_employees = [
            {'id': 1, 'name': "Test Employee 1"},
            {'id': 2, 'name': "Test Employee 2"}
        ]
        for employee in test_employees:
            e = db_manager.Employee.get_or_create(name=employee['name'])
            # give each employee an associated logentry
            db_manager.LogEntry.create(
                employee=e[0],
                date=datetime.date(2018,1,2),
                task_name='Test task {}'.format(employee['id']),
                duration=employee['id'],
                notes='Note'
            )
        user_inputs=['Test', '1']
        with patch('builtins.input', side_effect=user_inputs):
            result = self.menu.search_employee_text()
        
        expected_result = self.menu.present_next_result
        
        self.assertEqual(expected_result, result)

    # search_exact_date
    def test_search_exact_date_displays_correct_dates(self):
        """Ensure that all dates are displayed"""
        # add some data to the database
        test_employee = [
            {'id': 1, 'name': "Test Employee 1"},
        ]
        test_log_entry_dates = [
            datetime.date(2018,1,1),
            datetime.date(2018,1,2),
            datetime.date(2018,3,4),
            datetime.date(2018,5,6),
            datetime.date(2018,5,7),
        ]
        e = db_manager.Employee.get_or_create(name=test_employee[0]['name'])
        # create some log entries
        for date in test_log_entry_dates:
            db_manager.LogEntry.create(
                employee=e[0],
                date=date,
                task_name='Test task for date {}'.format(date),
                duration=10,
                notes='Note'
            )
            
        title = "\nSEARCH EXACT DATE" + "\n"
        date_rows = ""
        for i, date in enumerate(test_log_entry_dates):
            date_string = date.strftime("%Y-%m-%d")
            date_rows += "{}) {}\n".format(i + 1, date_string)
        
        expected_output = (title +
                           date_rows)

        # Create a StringIO object to be a capture object
        captured_output = io.StringIO()
        # point stdout at the capture object
        sys.stdout = captured_output
        # Do anything that's going to have a print statement
        # (these will be accumulated in the captured_output object)
        example_input = ['1']
        with patch('builtins.input', side_effect=example_input):
            self.menu.search_exact_date()

        # Revert stdout (captured_output still holds the captured items)
        sys.stdout = sys.__stdout__
        # Do any other test code (e.g., asserts)
        self.assertEqual(expected_output, captured_output.getvalue())
    
    def test_search_exact_date_returns_correct_menu(self):
        """Ensure that the correct next menu is loaded.
        """
        # add some data to the database
        test_employee = [
            {'id': 1, 'name': "Test Employee 1"},
        ]
        test_log_entry_dates = [
            datetime.date(2018,1,1),
            datetime.date(2018,1,2),
            datetime.date(2018,3,4),
            datetime.date(2018,5,6),
            datetime.date(2018,5,7),
        ]
        e = db_manager.Employee.get_or_create(name=test_employee[0]['name'])
        # create some log entries
        for date in test_log_entry_dates:
            db_manager.LogEntry.create(
                employee=e[0],
                date=date,
                task_name='Test task for date {}'.format(date),
                duration=10,
                notes='Note'
            )
            
        example_input = ['1']
        with patch('builtins.input', side_effect=example_input):
            result = self.menu.search_exact_date()

        expected_result = self.menu.present_next_result

        self.assertEqual(expected_result, result)

    # search_date_range
    def test_search_date_range_retrieves_corect_db_entries(self):
        """Ensure that all entries whose date in the specified range are
        retrieved from the DB"""
        # add some data to the database
        test_employee = [
            {'id': 1, 'name': "Test Employee 1"},
        ]
        test_log_entry_dates = [
            datetime.date(2018,1,1),
            datetime.date(2018,1,2),
            datetime.date(2018,3,4),
            datetime.date(2018,5,6),
            datetime.date(2018,5,7),
        ]
        e = db_manager.Employee.get_or_create(name=test_employee[0]['name'])
        # create some log entries
        for date in test_log_entry_dates:
            db_manager.LogEntry.create(
                employee=e[0],
                date=date,
                task_name='Test task for date {}'.format(date),
                duration=10,
                notes='Note'
            )

        start_index = 1
        end_index = -2

        match_slice = test_log_entry_dates[start_index:end_index + 1]

        expected_records = []
        for date in match_slice:
            new_record = OrderedDict([
                ('name', test_employee[0]['name']),
                ('date', date),
                ('task_name', 'Test task for date {}'.format(date)),
                ('duration', 10),
                ('notes', "Note")
            ])
            expected_records.append(new_record)
        
        start_date_string = test_log_entry_dates[start_index].strftime("%Y-%m-%d")
        end_date_string = test_log_entry_dates[end_index].strftime("%Y-%m-%d")
        user_inputs = [
            start_date_string,
            end_date_string
        ]
        
        with patch('builtins.input', side_effect=user_inputs):
            self.menu.search_date_range()
        
        self.assertEqual(expected_records, self.menu.records)
    
    def test_search_date_range_returns_correct_menu(self):
        """Ensure that the correct next menu is loaded.
        """
        # add some data to the database
        test_employee = [
            {'id': 1, 'name': "Test Employee 1"},
        ]
        test_log_entry_dates = [
            datetime.date(2018,1,1),
            datetime.date(2018,1,2),
            datetime.date(2018,3,4),
            datetime.date(2018,5,6),
            datetime.date(2018,5,7),
        ]
        e = db_manager.Employee.get_or_create(name=test_employee[0]['name'])
        # create some log entries
        for date in test_log_entry_dates:
            db_manager.LogEntry.create(
                employee=e[0],
                date=date,
                task_name='Test task for date {}'.format(date),
                duration=10,
                notes='Note'
            )

        start_index = 1
        end_index = -2

        start_date_string = test_log_entry_dates[start_index].strftime("%Y-%m-%d")
        end_date_string = test_log_entry_dates[end_index].strftime("%Y-%m-%d")
        user_inputs = [
            start_date_string,
            end_date_string
        ]
        
        with patch('builtins.input', side_effect=user_inputs):
            result = self.menu.search_date_range()
        
        expected_result = self.menu.present_next_result

        self.assertEqual(expected_result, result)

    # search_time_spent
    def test_search_time_spent_retrieves_corect_db_entries(self):
        """Ensure that all entries with the specified duration (and only those
        entries) are retrieved from the DB"""
        # add some data to the database
        test_employee = [
            {'id': 1, 'name': "Test Employee 1"},
        ]
        test_log_entry_durations = [
            1,
            2,
            2,
            3,
            5,
        ]
        e = db_manager.Employee.get_or_create(name=test_employee[0]['name'])
        # create some log entries
        for duration in test_log_entry_durations:
            db_manager.LogEntry.create(
                employee=e[0],
                date=datetime.date(2018, 1, duration),
                task_name='Test task of {}m'.format(duration),
                duration=duration,
                notes='Note'
            )
        match_duration = 2
        
        expected_results = []
        for duration in test_log_entry_durations:
            if duration == match_duration:
                new_record = OrderedDict([
                    ('name', test_employee[0]['name']),
                    ('date', datetime.date(2018, 1, duration)),
                    ('task_name', 'Test task of {}m'.format(duration)),
                    ('duration', duration),
                    ('notes', "Note")
                ])
                expected_results.append(new_record)
        
        user_input = str(match_duration)
        with patch('builtins.input', side_effect=user_input):
            self.menu.search_time_spent()

        self.assertEqual(expected_results, self.menu.records)

    def test_search_time_spent_returns_correct_menu(self):
        """Ensure that the correct next menu is loaded.
        """
        # add some data to the database
        test_employee = [
            {'id': 1, 'name': "Test Employee 1"},
        ]
        test_log_entry_durations = [
            1,
            2,
            2,
            3,
            5,
        ]
        e = db_manager.Employee.get_or_create(name=test_employee[0]['name'])
        # create some log entries
        for duration in test_log_entry_durations:
            db_manager.LogEntry.create(
                employee=e[0],
                date=datetime.date(2018, 1, duration),
                task_name='Test task of {}m'.format(duration),
                duration=duration,
                notes='Note'
            )
        match_duration = 2
        
        user_input = str(match_duration)
        with patch('builtins.input', side_effect=user_input):
            result = self.menu.search_time_spent()

        expected_result = self.menu.present_next_result

        self.assertEqual(expected_result, result)

    # search_text_search
    def test_search_text_search_retrieves_all_matching_records(self):
        """Ensure that all records matching the specified string (and only)
        those records are retrieved from the DB"""
        test_employees = [
            {'id': 1, 'name': "Test Employee 1 foo"},
            {'id': 2, 'name': "Test Employee 2 foo"},
            {'id': 3, 'name': "Test Employee 3 bar"},
        ]
        test_log_entries = [
            OrderedDict([
                ('name', test_employees[0]['name']),
                ('date', datetime.date(2018,1,2)),
                ('task_name', 'Test task alpha'),
                ('duration', 1),
                ('notes', 'Notes'),
            ]),
            OrderedDict([
                ('name', test_employees[1]['name']),
                ('date', datetime.date(2018,3,4)),
                ('task_name', 'Test task bravo'),
                ('duration', 2),
                ('notes', 'Notes'),
            ]),
            OrderedDict([
                ('name', test_employees[2]['name']),
                ('date', datetime.date(2018,5,6)),
                ('task_name', 'Test task bravo'),
                ('duration', 3),
                ('notes', 'Notes'),
            ]),
            OrderedDict([
                ('name', test_employees[0]['name']),
                ('date', datetime.date(2018,7,8)),
                ('task_name', 'Test task charlie'),
                ('duration', 4),
                ('notes', 'Notes'),
            ]),
        ]
        for employee in test_employees:
            e = db_manager.Employee.get_or_create(name=employee['name'])
            for entry in test_log_entries:
                if employee['name'] == entry['name']:
                    db_manager.LogEntry.create(
                        employee=e[0],
                        date=entry['date'],
                        task_name=entry['task_name'],
                        duration=entry['duration'],
                        notes=entry['notes']
                    )
        test_search_string = 'bravo'
        
        with patch('builtins.input', side_effect=test_search_string):
            self.menu.search_text_search()
        
        expected_results = []
        for entry in test_log_entries:
            if (test_search_string in entry['name'] or
                test_search_string in entry['task_name'] or
                test_search_string in entry['notes']):
                expected_results.append(entry)

        self.assertEqual(expected_results, self.menu.records)

    def test_search_test_search_returns_correct_menu(self):
        """Ensure that the correct next menu is loaded.
        """
        test_employees = [
            {'id': 1, 'name': "Test Employee 1 foo"},
            {'id': 2, 'name': "Test Employee 2 foo"},
            {'id': 3, 'name': "Test Employee 3 bar"},
        ]
        test_log_entries = [
            OrderedDict([
                ('name', test_employees[0]['name']),
                ('date', datetime.date(2018,1,2)),
                ('task_name', 'Test task alpha'),
                ('duration', 1),
                ('notes', 'Notes'),
            ]),
            OrderedDict([
                ('name', test_employees[1]['name']),
                ('date', datetime.date(2018,3,4)),
                ('task_name', 'Test task bravo'),
                ('duration', 2),
                ('notes', 'Notes'),
            ]),
            OrderedDict([
                ('name', test_employees[2]['name']),
                ('date', datetime.date(2018,5,6)),
                ('task_name', 'Test task bravo'),
                ('duration', 3),
                ('notes', 'Notes'),
            ]),
            OrderedDict([
                ('name', test_employees[0]['name']),
                ('date', datetime.date(2018,7,8)),
                ('task_name', 'Test task charlie'),
                ('duration', 4),
                ('notes', 'Notes'),
            ]),
        ]
        for employee in test_employees:
            e = db_manager.Employee.get_or_create(name=employee['name'])
            for entry in test_log_entries:
                if employee['name'] == entry['name']:
                    db_manager.LogEntry.create(
                        employee=e[0],
                        date=entry['date'],
                        task_name=entry['task_name'],
                        duration=entry['duration'],
                        notes=entry['notes']
                    )
        test_search_string = 'bravo'
        
        with patch('builtins.input', side_effect=test_search_string):
            result = self.menu.search_text_search()
        
        expected_result = self.menu.present_next_result

        self.assertEqual(expected_result, result)

    # edit_record
    def test_edit_record_edits_the_correct_record(self):
        """Ensure that the record retrieved from the DB corresponds to the
        record being requested by the user.

        This also ensures that the new value of the DB entry corresponds to 
        the new values supplied by the user
        """
        # create some db records
        test_employees = [
            {'id': 1, 'name': "Test Employee 1 foo"},
            {'id': 2, 'name': "Test Employee 2 foo"},
            {'id': 3, 'name': "Test Employee 3 bar"},
        ]
        test_log_entries = [
            OrderedDict([
                ('name', test_employees[0]['name']),
                ('date', datetime.date(2018,1,2)),
                ('task_name', 'Test task alpha'),
                ('duration', 1),
                ('notes', 'Notes'),
            ]),
            OrderedDict([
                ('name', test_employees[1]['name']),
                ('date', datetime.date(2018,3,4)),
                ('task_name', 'Test task bravo'),
                ('duration', 2),
                ('notes', 'Notes'),
            ]),
            OrderedDict([
                ('name', test_employees[2]['name']),
                ('date', datetime.date(2018,5,6)),
                ('task_name', 'Test task bravo'),
                ('duration', 3),
                ('notes', 'Notes'),
            ]),
            OrderedDict([
                ('name', test_employees[0]['name']),
                ('date', datetime.date(2018,7,8)),
                ('task_name', 'Test task charlie'),
                ('duration', 4),
                ('notes', 'Notes'),
            ]),
        ]
        for employee in test_employees:
            e = db_manager.Employee.get_or_create(name=employee['name'])
            for entry in test_log_entries:
                if employee['name'] == entry['name']:
                    db_manager.LogEntry.create(
                        employee=e[0],
                        date=entry['date'],
                        task_name=entry['task_name'],
                        duration=entry['duration'],
                        notes=entry['notes']
                    )
        # set the menu instance's `records` property
        self.menu.records = test_log_entries
        record_index = 1

        # handle the user input to select the record
        # handle the user input to specify the new values for the record
        user_inputs = [
            str(record_index + 1),
            "New Test Employee",
            "2017-10-05",
            "New Test Task",
            "55",
            "New Note"
        ]
        # get the unedited requested record from the db
        old_query = (db_manager
            .LogEntry
            .select()
            .join(db_manager.Employee)
            .where(
                db_manager.Employee.name == test_log_entries[record_index]['name'],
                db_manager.LogEntry.date == test_log_entries[record_index]['date'],
                db_manager.LogEntry.task_name == test_log_entries[record_index]['task_name'],
                db_manager.LogEntry.duration == test_log_entries[record_index]['duration'],
                db_manager.LogEntry.notes == test_log_entries[record_index]['notes']
            ))
        self.assertEqual(len(old_query), 1)
        
        # execute the method
        with patch('builtins.input', side_effect=user_inputs):
            self.menu.edit_record()
        
        # verify the record that was changed is the one selected by the user
        # (make sure we can get the record with the new details and we can't
        # get the record with the old details)
        new_query = (db_manager
            .LogEntry
            .select()
            .join(db_manager.Employee)
            .where(
                db_manager.Employee.name == user_inputs[1],
                db_manager.LogEntry.date == user_inputs[2],
                db_manager.LogEntry.task_name == user_inputs[3],
                db_manager.LogEntry.duration == user_inputs[4],
                db_manager.LogEntry.notes == user_inputs[5]
            ))
        repeat_old_query = (db_manager
            .LogEntry
            .select()
            .join(db_manager.Employee)
            .where(
                db_manager.Employee.name == test_log_entries[record_index]['name'],
                db_manager.LogEntry.date == test_log_entries[record_index]['date'],
                db_manager.LogEntry.task_name == test_log_entries[record_index]['task_name'],
                db_manager.LogEntry.duration == test_log_entries[record_index]['duration'],
                db_manager.LogEntry.notes == test_log_entries[record_index]['notes']
            ))

        self.assertEqual(len(new_query), 1) # new_query should return one result
        self.assertEqual(len(repeat_old_query), 0) # query should be empty
        
    def test_edit_record_returns_the_correct_menu(self):
        """Ensure that the method returns the correct next menu"""
        """Ensure that the record retrieved from the DB corresponds to the
        record being requested by the user.

        This also ensures that the new value of the DB entry corresponds to 
        the new values supplied by the user
        """
        # create some db records
        test_employees = [
            {'id': 1, 'name': "Test Employee 1 foo"},
        ]
        test_log_entries = [
            OrderedDict([
                ('name', test_employees[0]['name']),
                ('date', datetime.date(2018,1,2)),
                ('task_name', 'Test task alpha'),
                ('duration', 1),
                ('notes', 'Notes'),
            ]),
        ]
        for employee in test_employees:
            e = db_manager.Employee.get_or_create(name=employee['name'])
            for entry in test_log_entries:
                if employee['name'] == entry['name']:
                    db_manager.LogEntry.create(
                        employee=e[0],
                        date=entry['date'],
                        task_name=entry['task_name'],
                        duration=entry['duration'],
                        notes=entry['notes']
                    )
        # set the menu instance's `records` property
        self.menu.records = test_log_entries
        record_index = 0

        # handle the user input to select the record
        # handle the user input to specify the new values for the record
        user_inputs = [
            str(record_index + 1),
            "New Test Employee",
            "2017-10-05",
            "New Test Task",
            "55",
            "New Note"
        ]
        
        # execute the method
        with patch('builtins.input', side_effect=user_inputs):
            result = self.menu.edit_record()
        
        expected_result = self.menu.main_menu

        self.assertEqual(result, expected_result)

    # edit_current_record
    def test_edit_current_record_edits_the_correct_record(self):
        """Ensure that the record retrieved from the DB corresponds to the
        record being requested by the user.

        This also ensures that the new value of the DB entry corresponds to 
        the new values supplied by the user
        """
        # create some db records
        test_employees = [
            {'id': 1, 'name': "Test Employee 1 foo"},
            {'id': 2, 'name': "Test Employee 2 foo"},
            {'id': 3, 'name': "Test Employee 3 bar"},
        ]
        test_log_entries = [
            OrderedDict([
                ('name', test_employees[0]['name']),
                ('date', datetime.date(2018,1,2)),
                ('task_name', 'Test task alpha'),
                ('duration', 1),
                ('notes', 'Notes'),
            ]),
            OrderedDict([
                ('name', test_employees[0]['name']),
                ('date', datetime.date(2018,3,4)),
                ('task_name', 'Test task bravo'),
                ('duration', 2),
                ('notes', 'Notes'),
            ]),
            OrderedDict([
                ('name', test_employees[2]['name']),
                ('date', datetime.date(2018,5,6)),
                ('task_name', 'Test task bravo'),
                ('duration', 3),
                ('notes', 'Notes'),
            ]),
            OrderedDict([
                ('name', test_employees[1]['name']),
                ('date', datetime.date(2018,7,8)),
                ('task_name', 'Test task charlie'),
                ('duration', 4),
                ('notes', 'Notes'),
            ]),
        ]
        for employee in test_employees:
            e = db_manager.Employee.get_or_create(name=employee['name'])
            for entry in test_log_entries:
                if employee['name'] == entry['name']:
                    db_manager.LogEntry.create(
                        employee=e[0],
                        date=entry['date'],
                        task_name=entry['task_name'],
                        duration=entry['duration'],
                        notes=entry['notes']
                    )
        # set the menu instance's `records` property
        self.menu.records = test_log_entries
        record_index = 1
        self.menu.current_record = record_index

        # handle the user input to select the record
        # handle the user input to specify the new values for the record
        user_inputs = [
            "New Test Employee",
            "2017-10-05",
            "New Test Task",
            "55",
            "New Note"
        ]
        # get the unedited requested record from the db
        old_query = (db_manager
            .LogEntry
            .select()
            .join(db_manager.Employee)
            .where(
                db_manager.Employee.name == test_log_entries[record_index]['name'],
                db_manager.LogEntry.date == test_log_entries[record_index]['date'],
                db_manager.LogEntry.task_name == test_log_entries[record_index]['task_name'],
                db_manager.LogEntry.duration == test_log_entries[record_index]['duration'],
                db_manager.LogEntry.notes == test_log_entries[record_index]['notes']
            ))
        self.assertEqual(len(old_query), 1)
        
        # execute the method
        with patch('builtins.input', side_effect=user_inputs):
            self.menu.edit_current_record()
        
        # verify the record that was changed is the one selected by the user
        # (make sure we can get the record with the new details and we can't
        # get the record with the old details)
        new_query = (db_manager
            .LogEntry
            .select()
            .join(db_manager.Employee)
            .where(
                db_manager.Employee.name == user_inputs[0],
                db_manager.LogEntry.date == user_inputs[1],
                db_manager.LogEntry.task_name == user_inputs[2],
                db_manager.LogEntry.duration == user_inputs[3],
                db_manager.LogEntry.notes == user_inputs[4]
            ))
        repeat_old_query = (db_manager
            .LogEntry
            .select()
            .join(db_manager.Employee)
            .where(
                db_manager.Employee.name == test_log_entries[record_index]['name'],
                db_manager.LogEntry.date == test_log_entries[record_index]['date'],
                db_manager.LogEntry.task_name == test_log_entries[record_index]['task_name'],
                db_manager.LogEntry.duration == test_log_entries[record_index]['duration'],
                db_manager.LogEntry.notes == test_log_entries[record_index]['notes']
            ))
        self.assertEqual(len(new_query), 1) # new_query should return one result
        self.assertEqual(len(repeat_old_query), 0) # query should be empty
    
    def test_edit_current_record_applies_the_correct_changes(self):
        """Ensure that the new value of the DB entry corresponds to the
        new values supplied by the user
        """
        pass
    
    def test_edit_current_record_returns_the_correct_menu(self):
        """Ensure that the method returns the correct next menu"""
        pass


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