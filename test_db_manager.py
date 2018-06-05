"""Test DB Manager
Unit Tests for db_manager.py

Created: 2018
Last Update: 2018-06-05
Author: Alex Koumparos
"""
import unittest
import datetime
from collections import OrderedDict

from peewee import *

import db_manager
import wl_settings as settings


class DBManagerTests(unittest.TestCase):

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

    def create_mixed_test_data(self):
        """Creates four users and two log entries and writes them to the DB
        then returns a dictionary containing the users and log entries
        """
        # create 4 employees (2 with log entries, 2 without)
        test_employee_le_1_data = {'name': 'test user 1 (l.e.)'}
        test_employee_le_2_data = {'name': 'test user 2 (l.e.)'}
        test_employee_nle_1_data = {'name': 'test user 3 (no l.e.)'}
        test_employee_nle_2_data = {'name': 'test user 4 (no l.e.)'}
        # create 2 log entries (1 for each employee with logentry)
        test_log_entry_data_1 = {
            'name': test_employee_le_1_data['name'],
            'date': datetime.date(2018, 5, 24),
            'task_name': 'test_entry',
            'duration': 11,
            'notes': 'This is for testing record retrieval'
        }
        test_log_entry_data_2 = {
            'name': test_employee_le_2_data['name'],
            'date': datetime.date(2018, 5, 24),
            'task_name': 'test_entry',
            'duration': 12,
            'notes': 'This is for testing record retrieval'
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

    def create_test_dates(self):
        """Creates one user and five log entries and writes them to the DB
        then returns a dictionary containing the user and log entries
        """
        # create 1 employee
        test_employee_data = {'name': 'date test user'}
        # create 5 log entries (4 unique dates and 1 duplicated)
        test_log_entry_data_1 = {
            'name': test_employee_data['name'],
            'date': datetime.date(1999, 1, 15),
            'task_name': 'test_date_entry',
            'duration': 10,
            'notes': 'This is for testing retrieval by date'
        }
        test_log_entry_data_2 = {
            'name': test_employee_data['name'],
            'date': datetime.date(2010, 5, 25),
            'task_name': 'test_date_entry',
            'duration': 20,
            'notes': 'This is also for testing retrieval by date'
        }
        test_log_entry_data_3 = {
            'name': test_employee_data['name'],
            'date': datetime.date(2018, 11, 30),
            'task_name': 'test_date_entry',
            'duration': 30,
            'notes': 'This is still for testing retrieval by date'
        }
        test_log_entry_data_4 = {
            'name': test_employee_data['name'],
            'date': datetime.date(2010, 5, 25),
            'task_name': 'test_date_entry',
            'duration': 40,
            'notes': 'This is still also for testing retrieval by date'
        }
        test_log_entry_data_5 = {
            'name': test_employee_data['name'],
            'date': datetime.date(2015, 12, 1),
            'task_name': 'test_date_entry',
            'duration': 50,
            'notes': 'This is yet still also for testing retrieval by date'
        }
        # write the test data to the database
        employee_record = db_manager.Employee.get_or_create(
            name=test_employee_data["name"]
        )
        db_manager.LogEntry.create(
            employee=employee_record[0],
            date=test_log_entry_data_1["date"],
            task_name=test_log_entry_data_1["task_name"],
            duration=test_log_entry_data_1["duration"],
            notes=test_log_entry_data_1["notes"],
        )
        db_manager.LogEntry.create(
            employee=employee_record[0],
            date=test_log_entry_data_2["date"],
            task_name=test_log_entry_data_2["task_name"],
            duration=test_log_entry_data_2["duration"],
            notes=test_log_entry_data_2["notes"],
        )
        db_manager.LogEntry.create(
            employee=employee_record[0],
            date=test_log_entry_data_3["date"],
            task_name=test_log_entry_data_3["task_name"],
            duration=test_log_entry_data_3["duration"],
            notes=test_log_entry_data_3["notes"],
        )
        db_manager.LogEntry.create(
            employee=employee_record[0],
            date=test_log_entry_data_4["date"],
            task_name=test_log_entry_data_4["task_name"],
            duration=test_log_entry_data_4["duration"],
            notes=test_log_entry_data_4["notes"],
        )
        db_manager.LogEntry.create(
            employee=employee_record[0],
            date=test_log_entry_data_5["date"],
            task_name=test_log_entry_data_5["task_name"],
            duration=test_log_entry_data_5["duration"],
            notes=test_log_entry_data_5["notes"],
        )
        return {
            'test_employee_data': test_employee_data,
            'test_log_entry_data': [
                test_log_entry_data_1,
                test_log_entry_data_2,
                test_log_entry_data_3,
                test_log_entry_data_4,
                test_log_entry_data_5
            ]
        }

    def create_test_durations(self):
        """Creates one user and four log entries and writes them to the DB
        then returns a dictionary containing the user and log entries
        """
        # create 1 employee
        test_employee_data = {'name': 'duration test user'}
        # create 4 log entries (3 unique durations and 1 duplicated)
        test_log_entry_data_1 = {
            'name': test_employee_data['name'],
            'date': datetime.date(1999, 1, 15),
            'task_name': 'test_duration_entry',
            'duration': 10,
            'notes': 'This is for testing retrieval by duration'
        }
        test_log_entry_data_2 = {
            'name': test_employee_data['name'],
            'date': datetime.date(2010, 5, 25),
            'task_name': 'test_duration_entry',
            'duration': 20,
            'notes': 'This is for testing retrieval by duration'
        }
        test_log_entry_data_3 = {
            'name': test_employee_data['name'],
            'date': datetime.date(2018, 11, 30),
            'task_name': 'test_duration_entry',
            'duration': 30,
            'notes': 'This is for testing retrieval by duration'
        }
        test_log_entry_data_4 = {
            'name': test_employee_data['name'],
            'date': datetime.date(2010, 5, 25),
            'task_name': 'test_duration_entry',
            'duration': 20,
            'notes': 'This is for testing retrieval by duration'
        }
        # write the test data to the database
        employee_record = db_manager.Employee.get_or_create(
            name=test_employee_data["name"]
        )
        db_manager.LogEntry.create(
            employee=employee_record[0],
            date=test_log_entry_data_1["date"],
            task_name=test_log_entry_data_1["task_name"],
            duration=test_log_entry_data_1["duration"],
            notes=test_log_entry_data_1["notes"],
        )
        db_manager.LogEntry.create(
            employee=employee_record[0],
            date=test_log_entry_data_2["date"],
            task_name=test_log_entry_data_2["task_name"],
            duration=test_log_entry_data_2["duration"],
            notes=test_log_entry_data_2["notes"],
        )
        db_manager.LogEntry.create(
            employee=employee_record[0],
            date=test_log_entry_data_3["date"],
            task_name=test_log_entry_data_3["task_name"],
            duration=test_log_entry_data_3["duration"],
            notes=test_log_entry_data_3["notes"],
        )
        db_manager.LogEntry.create(
            employee=employee_record[0],
            date=test_log_entry_data_4["date"],
            task_name=test_log_entry_data_4["task_name"],
            duration=test_log_entry_data_4["duration"],
            notes=test_log_entry_data_4["notes"],
        )
        return {
            'test_employee_data': test_employee_data,
            'test_log_entry_data': [
                test_log_entry_data_1,
                test_log_entry_data_2,
                test_log_entry_data_3,
                test_log_entry_data_4
            ]
        }

    def create_test_employees(self):
        """Creates three users and four log entries and writes them to the DB
        then returns a dictionary containing the user and log entries
        """
        # create 1 employee
        test_employee_1_data = {'name': 'employee test user'}
        test_employee_2_data = {'name': 'second employee test user'}
        test_employee_3_data = {'name': 'third test user'}
        # create 4 log entries (3 unique users and 1 duplicated)
        test_log_entry_data_1 = {
            'name': test_employee_1_data['name'],
            'date': datetime.date(1999, 1, 15),
            'task_name': 'test_duration_entry',
            'duration': 10,
            'notes': 'This is for testing retrieval by duration'
        }
        test_log_entry_data_2 = {
            'name': test_employee_2_data['name'],
            'date': datetime.date(2010, 5, 25),
            'task_name': 'test_duration_entry',
            'duration': 20,
            'notes': 'This is for testing retrieval by duration'
        }
        test_log_entry_data_3 = {
            'name': test_employee_3_data['name'],
            'date': datetime.date(2018, 11, 30),
            'task_name': 'test_duration_entry',
            'duration': 30,
            'notes': 'This is for testing retrieval by duration'
        }
        test_log_entry_data_4 = {
            'name': test_employee_2_data['name'],
            'date': datetime.date(2010, 5, 25),
            'task_name': 'test_duration_entry',
            'duration': 20,
            'notes': 'This is for testing retrieval by duration'
        }
        # write the test data to the database
        employee_record_1 = db_manager.Employee.get_or_create(
            name=test_employee_1_data["name"]
        )
        employee_record_2 = db_manager.Employee.get_or_create(
            name=test_employee_2_data["name"]
        )
        employee_record_3 = db_manager.Employee.get_or_create(
            name=test_employee_3_data["name"]
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
        db_manager.LogEntry.create(
            employee=employee_record_3[0],
            date=test_log_entry_data_3["date"],
            task_name=test_log_entry_data_3["task_name"],
            duration=test_log_entry_data_3["duration"],
            notes=test_log_entry_data_3["notes"],
        )
        db_manager.LogEntry.create(
            employee=employee_record_2[0],
            date=test_log_entry_data_4["date"],
            task_name=test_log_entry_data_4["task_name"],
            duration=test_log_entry_data_4["duration"],
            notes=test_log_entry_data_4["notes"],
        )
        return {
            'test_employee_data': [
                test_employee_1_data,
                test_employee_2_data,
                test_employee_3_data,
            ],
            'test_log_entry_data': [
                test_log_entry_data_1,
                test_log_entry_data_2,
                test_log_entry_data_3,
                test_log_entry_data_4
            ]
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

    # Actual tests
    # ------------
    # add_entry
    def test_add_entry_creates_valid_db_entry(self):
        """Check that data is correctly written to database"""
        test_employee_data = {'name': 'test user (add)'}
        test_log_entry_data = {
            'name': test_employee_data['name'],
            'date': datetime.date(2018, 1, 1),
            'task_name': 'test_entry_add_entry',
            'duration': 17,
            'notes': 'This is a test of adding an entry',
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
            'name': test_employee_data['name'],
            'date': datetime.date(2018, 1, 1),
            'task_name': 'test_entry_edit_entry',
            'duration': 18,
            'notes': 'This is a test of editing an entry'
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
            'name': edited_employee_data['name'],
            'date': datetime.date(2017, 2, 2),
            'task_name': 'test_entry_edit_entry (edited)',
            'duration': 28,
            'notes': 'This is a test of editing an entry (edited)',
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

    def test_edit_entry_invalid_employee_raises_doesnotexist(self):
        """Ensure that passing a missing employee raises doesnot exist"""
        pass

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
    def test_view_dates_returns_all_dates(self):
        """Ensure that every date in the test_data_set is returned

        We can test this by checking that the length of the returned
        iterable of dates is equal to the number of unique dates in
        the test dataset (we have a separate test to ensure no duplicates)
        """
        test_data = self.create_test_dates()
        dates = [entry['date'] for entry in test_data['test_log_entry_data']]
        unique_dates = set(dates)
        unique_date_count = len(unique_dates)

        records = self.dbm.view_dates()

        self.assertEqual(unique_date_count, len(records))

    def test_view_dates_returns_no_duplicates(self):
        """Ensure that no duplicate dates are returned.

        We know that there are no duplicates if the length of the iterable
        containing the dates is the same as the set of the iterable containing
        the dates
        """
        self.create_test_dates()

        records = self.dbm.view_dates()

        dates = []
        for record in records:
            dates.append(record['date'])

        self.assertEqual(len(set(dates)), len(dates))

    # view_entries_for_date
    def test_view_entries_for_date_returns_all_matches(self):
        """Ensure that all the entries with a date matching the query
        are returned ad no entries with a date not matching the query
        are returned.
        """
        data = self.create_test_dates()['test_log_entry_data']
        date = data[1]['date']  # the duplicated date
        matching_dates = [datum for datum in data if datum['date'] == date]

        records = self.dbm.view_entries_for_date(date)

        self.assertCountEqual(matching_dates, records)

    # view_entries_for_duration
    def test_view_entries_for_duration_returns_all_matches(self):
        """Ensure that all the entries with a duration matching the query
        are returned and no entries with a duration not matching the query
        are returned.
        """
        data = self.create_test_durations()['test_log_entry_data']
        duration = data[1]['duration']  # the duplicated date
        matches = [datum for datum in data if datum['duration'] == duration]

        records = self.dbm.view_entries_for_duration(duration)

        self.assertCountEqual(matches, records)

    # view_entries_for_date_range
    def test_view_entries_for_date_range_returns_all_matches(self):
        """Ensure that all the entries with a date in the specified
        range that match the query are returned and no entries with a date not
        matching the query are returned.
        """
        data = self.create_test_dates()['test_log_entry_data']
        start = datetime.date(2010, 5, 25)
        end = datetime.date(2015, 12, 1)
        matching_dates = []
        for datum in data:
            if datum['date'] >= start and datum['date'] <= end:
                matching_dates.append(datum)

        records = self.dbm.view_entries_for_date_range(start, end)

        self.assertCountEqual(matching_dates, records)

    # view_entries_with_text
    def test_view_entries_with_text_returns_all_matches(self):
        """Ensure that all entries whose text fields contain the specified
        test string are returned and no entries that do not have a text field
        containing the test string are returned.
        """
        data = self.create_test_dates()['test_log_entry_data']
        pattern = 'still'
        matching_data = []
        for datum in data:
            if (
                pattern in datum['name'] or
                pattern in datum['task_name'] or
                pattern in datum['notes']
            ):
                matching_data.append(datum)

        records = self.dbm.view_entries_with_text(pattern)

        self.assertCountEqual(matching_data, records)

    # view_names_with_text
    def test_view_names_with_text_returns_all_matches(self):
        """Ensure that all entries whose name field contains the specified
        test string are returned and no entries that do not have the test
        string in the name field are returned
        """
        data = self.create_test_employees()['test_employee_data']
        pattern = 'second'
        matching_data = []
        for datum in data:
            if pattern in datum['name']:
                matching_data.append(datum)

        records = self.dbm.view_names_with_text(pattern)

        self.assertCountEqual(matching_data, records)

    # view_everything
    def test_view_everything_returns_all_records(self):
        """Ensure that all entries are returned."""
        data = self.create_test_dates()['test_log_entry_data']

        records = self.dbm.view_everything()
        records = [dict(entry) for entry in records]

        self.assertEqual(len(data), len(records))
        for datum in data:
            self.assertIn(datum, records)

    def test_view_everything_sorted_returns_sorted_results(self):
        """When date_sorted=True, ensure that the results are sorted
        in ascending date order.
        """
        # create test db records
        data = self.create_test_dates()
        log_entries = data['test_log_entry_data']
        dates = [log_entry['date'] for log_entry in log_entries]
        sorted_dates = sorted(dates)

        # pull the records from the database
        records = self.dbm.view_everything(date_sorted=True)

        # transform the db result into a list of dates
        record_dates = [record['date'] for record in records]

        # assert that the order of dates == the order from the dataset
        self.assertEqual(sorted_dates, record_dates)

    def test_view_everything_employee_filters_by_employee(self):
        """When employee is not set to None, ensure that returned records
        are only for the specified employee
        """
        # load mixed_data into db
        data = self.create_test_employees()
        employee = data['test_employee_data'][1]  # duplicated employee

        # view_everything with duplicated employee
        records = self.dbm.view_everything(employee=employee['name'])

        # check that the length of the returned records == number of
        #   elements in dataset with that employee
        self.assertEqual(len(records), 2)

        # check that all returned records are for that employee
        for record in records:
            self.assertEqual(record['name'], employee['name'])

    # view_entry
    def test_view_entry_returns_correct_record(self):
        """Ensure that the correct entry is returned."""
        data = self.create_mixed_test_data()['test_log_entry_1']

        record = self.dbm.view_entry(data)

        self.assertEqual(data, record)

    def test_view_entry_raises_DoesNotExist_for_missing_employee(self):
        """If an invalid employee is provided, should raise DoesNotExist"""
        data = self.create_mixed_test_data()
        nonexistent_employee_name = "This employee does not exist"

        real_log_entry = data['test_log_entry_1']

        log_entry_with_nonexistent_employee = {
            'name': nonexistent_employee_name,
            'date': real_log_entry['date'],
            'task_name': real_log_entry['task_name'],
            'duration': real_log_entry['duration'],
            'notes': real_log_entry['notes']
        }
        with self.assertRaises(DoesNotExist):
            self.dbm.view_entry(log_entry_with_nonexistent_employee)

    def test_view_entry_raises_DoesNotExist_for_missing_log_entry(self):
        """If an invalid logentry is provided, should raise DoesNotExist"""
        data = self.create_mixed_test_data()
        real_employee_data = data['test_employee_le_1']

        real_employee = db_manager.Employee.get(
            name=real_employee_data['name']
        )

        nonexistent_logentry_data = {
            'name': real_employee.name,
            'date': datetime.date(2018, 1, 1),
            'task_name': "Non-existent task for non-existent logentry",
            'duration': 1,
            'notes': "Non-existent note for non-existent logentry"
        }

        with self.assertRaises(DoesNotExist):
            self.dbm.view_entry(nonexistent_logentry_data)

    # delete_entry
    def test_delete_entry_removes_the_specified_record(self):
        """Ensure that a) the specified record is removed and b) only
        the specified record is removed.
        """
        data = self.create_mixed_test_data()
        datum_to_delete = data['test_log_entry_1']

        records_before_deletion = db_manager.LogEntry.select()
        number_records_before_deletion = len(records_before_deletion)

        # Make sure we can get the record before we delete it
        employee = db_manager.Employee.get(name=datum_to_delete['name'])
        db_manager.LogEntry.get(
                employee=employee,
                task_name=datum_to_delete['task_name'],
                date=datum_to_delete['date'],
                notes=datum_to_delete['notes'],
                duration=datum_to_delete['duration']
        )

        # Delete the record
        self.dbm.delete_entry(datum_to_delete)

        records_after_deletion = db_manager.LogEntry.select()
        number_records_after_deletion = len(records_after_deletion)

        # Make sure that only one record was deleted
        self.assertEqual(number_records_before_deletion - 1,
                         number_records_after_deletion)

        # Make sure that we now get DoesNotExist when we try to get the
        # deleted record
        with self.assertRaises(DoesNotExist):
            db_manager.LogEntry.get(
                employee=employee,
                task_name=datum_to_delete['task_name'],
                date=datum_to_delete['date'],
                notes=datum_to_delete['notes'],
                duration=datum_to_delete['duration']
            )

    # record_to_dict
    def test_record_to_dict_returns_orderedDict_matching_record(self):
        """Ensure that the returned object has the same elements as the record.

        Check by getting a particular record from the database, getting the OD
        from that record then attempt to get the same record from the database
        using the values from the OD
        """
        data = self.create_mixed_test_data()
        log_entry_data = data['test_log_entry_1']

        employee = db_manager.Employee.get(name=log_entry_data['name'])
        log_entry = db_manager.LogEntry.get(
            employee=employee,
            task_name=log_entry_data['task_name'],
            date=log_entry_data['date'],
            notes=log_entry_data['notes'],
            duration=log_entry_data['duration']
        )

        ordered_dict = self.dbm.record_to_dict(log_entry)

        employee_from_od = db_manager.Employee.get(
            name=ordered_dict['name']
        )
        log_entry_from_od = db_manager.LogEntry.get(
            employee=employee_from_od,
            task_name=ordered_dict['task_name'],
            date=ordered_dict['date'],
            notes=ordered_dict['notes'],
            duration=ordered_dict['duration']
        )

        self.assertEqual(log_entry, log_entry_from_od)

    def test_record_to_dict_returns_orderedDict(self):
        """Ensure that the returned collection is actually of type OrderedDict.
        """
        data = self.create_mixed_test_data()
        log_entry_data = data['test_log_entry_1']

        employee = db_manager.Employee.get(name=log_entry_data['name'])
        log_entry = db_manager.LogEntry.get(
            employee=employee,
            task_name=log_entry_data['task_name'],
            date=log_entry_data['date'],
            notes=log_entry_data['notes'],
            duration=log_entry_data['duration']
        )

        ordered_dict = self.dbm.record_to_dict(log_entry)

        self.assertIsInstance(ordered_dict, OrderedDict)

    # records_to_list
    def test_records_to_list_returns_list_matching_records(self):
        """Ensure that the list has the same elements as the collection of
        records."""
        data = self.create_mixed_test_data()

        entries = db_manager.LogEntry.select()
        number_of_entries = len(entries)

        list_of_ods = self.dbm.records_to_list(entries)
        number_in_list = len(list_of_ods)

        self.assertEqual(number_of_entries, number_in_list)

if __name__ == "__main__":
    unittest.main()
