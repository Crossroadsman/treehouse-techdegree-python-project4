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
        db_manager.db = SqliteDatabase(settings.LIVE_DATABASE_NAME)
        db_manager.Employee._meta.database = db_manager.db
        db_manager.LogEntry._meta.database = db_manager.db
    
    def retrieve_database_entry(self, record):
        """Gets a DB record and returns the values as a dict"""
        retrieved_employee = db_manager.Employee.get(
            db_manager.Employee.name == record['name']
        )
        retrieved_log_entry = db_manager.LogEntry.get(
            db_manager.LogEntry.employee == retrieved_employee,
            db_manager.LogEntry.date == record["date"],
            db_manager.LogEntry.task_name == record["task_name"],
            db_manager.LogEntry.duration == record["duration"],
            db_manager.LogEntry.notes == record["notes"]
        )
        retrieved_log_entry_dict = {
            'name': retrieved_log_entry.employee.name,
            'date': retrieved_log_entry.date,
            'task_name': retrieved_log_entry.task_name,
            'duration': retrieved_log_entry.duration,
            'notes': retrieved_log_entry.notes,
        }
        return retrieved_log_entry_dict


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
        """Check that data is correctly written to database
        
        Note, because this test involves writing to the database it switches
        out the database file, using a dedicated 'unittest.db' database file.
        At the end of the test it switches back to the live database.
        """
        self.set_test_database()
        
        test_employee_data = {'name': 'test user (add)'}
        test_log_entry_data = {
            'name' : test_employee_data['name'],
            'date' : datetime.date(2018,1,1),
            'task_name' : 'test_entry_add_entry',
            'duration' : 17,
            'notes' : 'This is a test of adding an entry',
        }
        
        dbm = db_manager.DBManager()
        # this is the actual transaction being tested:
        dbm.add_entry(test_log_entry_data)

        retrieved_log_entry_dict = self.retrieve_database_entry(
            test_log_entry_data
        )
        self.assertEqual(test_log_entry_data, retrieved_log_entry_dict)

        self.revert_database()
    
    # edit_entry
    def test_edit_entry_correctly_changes_record(self):
        self.set_test_database()

        dbm = db_manager.DBManager()
        
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
        logentry_record = db_manager.LogEntry.create(
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
        dbm.edit_entry(test_log_entry_data, edited_log_entry_data)
        
        # read record back from database &
        # convert record to dict
        retrieved_log_entry_dict = self.retrieve_database_entry(
            edited_log_entry_data
        )
        
        # check changed record == changed entry
        self.assertEqual(edited_log_entry_data, retrieved_log_entry_dict)

        self.revert_database()

    # view_employees

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