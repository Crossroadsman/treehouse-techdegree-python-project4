import unittest
import datetime

from peewee import *

import db_manager
import wl_settings as settings


class DBManagerTests(unittest.TestCase):

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


    def test_five_plus_five(self):
        assert 5 + 5 == 10
    
    def test_one_plus_one(self):
        assert not 1 + 1 == 3

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
        
    # add_entry
    def test_add_entry_creates_valid_db_entry(self):
        """Check that data is correctly written to database
        
        Note, because this test involves writing to the database it switches
        out the database file, using a dedicated 'unittest.db' database file.
        At the end of the test it switches back to the live database.
        """
        self.set_test_database()
        
        test_employee_data = {'name': 'test user'}
        test_log_entry_data = {
            'name' : test_employee_data['name'],
            'date' : datetime.date(2018,1,1),
            'task_name' : 'test_entry',
            'duration' : 17,
            'notes' : 'This is a test',
        }
        
        dbm = db_manager.DBManager()
        dbm.add_entry(test_log_entry_data)

        retrieved_employee = db_manager.Employee.get(
            db_manager.Employee.name == test_employee_data['name']
        )
        retrieved_log_entry = db_manager.LogEntry.get(
            db_manager.LogEntry.employee == retrieved_employee,
            db_manager.LogEntry.date == test_log_entry_data["date"],
            db_manager.LogEntry.task_name == test_log_entry_data["task_name"],
            db_manager.LogEntry.duration == test_log_entry_data["duration"],
            db_manager.LogEntry.notes == test_log_entry_data["notes"]
        )
        retrieved_log_entry_dict = {
            'name': retrieved_log_entry.employee.name,
            'date': retrieved_log_entry.date,
            'task_name': retrieved_log_entry.task_name,
            'duration': retrieved_log_entry.duration,
            'notes': retrieved_log_entry.notes,
        }
        self.assertEqual(test_log_entry_data, retrieved_log_entry_dict)

        self.revert_database()
    
    # edit_entry

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