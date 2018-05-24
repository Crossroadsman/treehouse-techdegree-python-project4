import unittest
import datetime

from peewee import *

import db_manager
import wl_settings as settings


class DBManagerTests(unittest.TestCase):

    # Helper Methods
    # --------------
    def set_test_database(self):
        """Switch out the regular database and switch in a unittest-only
        database"""
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

    def db_record_to_dict(self, record):
        """Converts a DB record to a dict and returns it"""
        record_as_dict = {
            'name': record.employee.name,
            'date': record.date,
            'task_name': record.task_name,
            'duration': record.duration,
            'notes': record.notes,
        }
        return record_as_dict

    '''
    def db_employee_to_dict(self, record):
        """Converts a DB record of an employee to a dict and returns it"""
        record_as_dict = {'name': record.name}
        return record_as_dict
    '''
    
    def retrieve_database_entry(self, data):
        """Gets a DB record and returns the values as a dict"""
        retrieved_employee = db_manager.Employee.get(
            db_manager.Employee.name == data['name']
        )
        retrieved_log_entry = db_manager.LogEntry.get(
            db_manager.LogEntry.employee == retrieved_employee,
            db_manager.LogEntry.date == data["date"],
            db_manager.LogEntry.task_name == data["task_name"],
            db_manager.LogEntry.duration == data["duration"],
            db_manager.LogEntry.notes == data["notes"]
        )
        return self.db_record_to_dict(retrieved_log_entry)

    '''
    def retrieve_employee(self, data):
        """Gets a DB record of just an employee"""
        retrieved_employee = db_manager.Employee.get(
            db_manager.Employee.name == data['name']
        )
        return self.db_employee_to_dict(retrieved_employee)
    '''

    def create_mixed_test_data(self):
        """Creates four users and two log entries and writes them to the DB
        then returns a dictionary containing the users
        """
        # create 4 employees (2 with log entries, 2 without)
        test_employee_le_1_data = {'name': 'test user 1 (l.e.)'}
        test_employee_le_2_data = {'name': 'test user 2 (l.e.)'}
        test_employee_nle_1_data = {'name': 'test user 3 (no l.e.)'}
        test_employee_nle_2_data = {'name': 'test user 4 (no l.e.)'}
        # create 2 log entries (1 for each employee with logentry)
        test_log_entry_data_1 = {
            'name' : test_employee_le_1_data['name'],
            'date' : datetime.date(2018,5,24),
            'task_name' : 'test_entry',
            'duration' : 11,
            'notes' : 'This is for testing record retrieval'
        }
        test_log_entry_data_2 = {
            'name' : test_employee_le_2_data['name'],
            'date' : datetime.date(2018,5,24),
            'task_name' : 'test_entry',
            'duration' : 12,
            'notes' : 'This is for testing record retrieval'
        }
        # write the test data to the database
        employee_record_1 = db_manager.Employee.get_or_create(
            name=test_employee_le_1_data["name"]
        )
        employee_record_2 = db_manager.Employee.get_or_create(
            name=test_employee_le_2_data["name"]
        )
        db_manager.Employee.get_or_create(
            name=test_employee_nle_1_data["name"]
        )
        db_manager.Employee.get_or_create(
            name=test_employee_nle_2_data["name"]
        )
        db_manager.LogEntry.create(
            employee=employee_record_1[0],
            date=test_log_entry_data_1["date"],
            task_name=test_log_entry_data_1["task_name"],
            duration=test_log_entry_data_1["duration"],
            notes=test_log_entry_data_1["notes"],
        )
        db_manager.LogEntry.create(
            employee=employee_record_2[0],
            date=test_log_entry_data_2["date"],
            task_name=test_log_entry_data_2["task_name"],
            duration=test_log_entry_data_2["duration"],
            notes=test_log_entry_data_2["notes"],
        )
        return {
            'test_employee_le_1': test_employee_le_1_data,
            'test_employee_le_2': test_employee_le_2_data,
            'test_employee_nle_1': test_employee_nle_1_data,
            'test_employee_nle_2': test_employee_nle_2_data,
            'test_log_entry_1': test_log_entry_data_1,
            'test_log_entry_2': test_log_entry_data_2
        }

    # Setup and Teardown
    # ------------------
    def setUp(self):
        """Because these tests involve writing to the database, we switch
        out the database file, using a dedicated 'unittest.db' database file.
        At the end of the test it switches back to the live database.
        """
        self.set_test_database()
        self.dbm = db_manager.DBManager()
    
    def tearDown(self):
        self.revert_database()

    # Example tests
    # -------------
    '''
    def test_assertcountequal(self):
        """This is just a quick illustration of 
        `self.assertCountEqual(a, b)` : check a and b have the same number of
                                        the same elements, regardless of order
        """
        from collections import OrderedDict
        od = OrderedDict([('name_one', 'alice'), ('name_two', 'bob')])
        d = {'name_two': 'bob', 'name_one': 'alice'}
        d2 = {'name_two': 'alice', 'name_one': 'bob'}
        d3 = {'name_two': 'clarice', 'name_one': 'doug'}
        # note, it might seem that assertCountEqual() would be the ideal
        # assert for this test, but it seems that it only looks at keys and
        # ignores values.
        # so assertCountEqual() would cause each of the following comparisons
        # to pass
        self.assertEqual(od, d)
        self.assertNotEqual(od, d2)
        self.assertNotEqual(od, d3)
    '''
        
    # add_entry
    def test_add_entry_creates_valid_db_entry(self):
        """Check that data is correctly written to database"""
        test_employee_data = {'name': 'test user (add)'}
        test_log_entry_data = {
            'name' : test_employee_data['name'],
            'date' : datetime.date(2018,1,1),
            'task_name' : 'test_entry_add_entry',
            'duration' : 17,
            'notes' : 'This is a test of adding an entry',
        }
        
        # this is the actual transaction being tested:
        self.dbm.add_entry(test_log_entry_data)

        retrieved_log_entry_dict = self.retrieve_database_entry(
            test_log_entry_data
        )
        self.assertEqual(test_log_entry_data, retrieved_log_entry_dict)
    
    # edit_entry
    def test_edit_entry_correctly_changes_record(self):
        """Test that database records are correctly edited"""
        
        # create a database entry (to change)
        test_employee_data = {'name': 'test user (edit)'}
        test_log_entry_data = {
            'name' : test_employee_data['name'],
            'date' : datetime.date(2018,1,1),
            'task_name' : 'test_entry_edit_entry',
            'duration' : 18,
            'notes' : 'This is a test of editing an entry'
        }
        employee_record = db_manager.Employee.get_or_create(
            name=test_employee_data["name"]
        )
        db_manager.LogEntry.create(
            employee=employee_record[0],
            date=test_log_entry_data["date"],
            task_name=test_log_entry_data["task_name"],
            duration=test_log_entry_data["duration"],
            notes=test_log_entry_data["notes"],
        )

        # specify changed entry
        edited_employee_data = {'name': 'test user (edited)'}
        edited_log_entry_data = {
            'name' : edited_employee_data['name'],
            'date' : datetime.date(2017,2,2),
            'task_name' : 'test_entry_edit_entry (edited)',
            'duration' : 28,
            'notes' : 'This is a test of editing an entry (edited)',
        }
        
        # write changes to database using dbm method
        # (this is the actual transaction being tested)
        self.dbm.edit_entry(test_log_entry_data, edited_log_entry_data)
        
        # read record back from database &
        # convert record to dict
        retrieved_log_entry_dict = self.retrieve_database_entry(
            edited_log_entry_data
        )
        
        # check changed record == changed entry
        self.assertEqual(edited_log_entry_data, retrieved_log_entry_dict)

    # view_employees
    def test_view_employees_returns_all_employees_who_have_entries(self):
        """Confirm that querying the database gets all the employees
        who have created entries
        """
        test_data = self.create_mixed_test_data()

        # retrieve records (this is the actual transaction to test)
        employee_records = self.dbm.view_employees()

        # check that the employees are test1 and test2
        employees_le = []
        employees_le.append(test_data['test_employee_le_1'])
        employees_le.append(test_data['test_employee_le_2'])

        self.assertEqual(employee_records, employees_le)
    
    def test_view_employees_returns_no_employees_without_entries(self):
        """Confirm that querying the database gets no employees
        who have not created entries
        """
        test_data = self.create_mixed_test_data()

        # retrieve records (this is the actual transaction to test)
        employee_records = self.dbm.view_employees()

        # check that the employees are test1 and test2
        employees_nle = []
        employees_nle.append(test_data['test_employee_nle_1'])
        employees_nle.append(test_data['test_employee_nle_2'])

        self.assertNotEqual(employee_records, employees_nle)


    # view_dates

    # view_entries_for_date

    # view_entries_for_duration

    # view_entries_for_date_range

    # view_entries_with_text

    # view_names_with_text

    # view_everything

    # view_entry

    # delete_entry

    # record_to_dict

    # records_to_list

if __name__ == "__main__":
    unittest.main()