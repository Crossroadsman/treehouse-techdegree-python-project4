#!/usr/bin/env python3

"""DB Manager
All the database-related functionality.
Communicates with the rest of the application using OrderDicts

Created: 2018
Last Update: 2018-06-05
Author: Alex Koumparos
"""
from collections import OrderedDict

from peewee import *

import wl_settings as settings


db = SqliteDatabase(settings.DATABASE_NAME)


class DBManager:
    """The Database Manager, has all the functionality for initialising and
    maintaining the database. Has methods to provide data to the rest of the
    application in the form of OrderDicts so the nature and implementation of
    the database itself is abstracted away.
    """
    def __init__(self):
        """Create the database and the table if they don't already exist.

        Note that we don't HAVE to explicitly connect to the DB now but it
        makes bug checking easier than having the connection fail when we try
        to do a query
        """
        try:
            # reuse_if_open -> prevents connection already open error
            db.connect(reuse_if_open=True)
        except OperationalError as err:
            print("operational error!")
            print("detailed error information:")
            print(err)
        db.create_tables(tables, safe=True)

    def add_entry(self, entry):
        """Add an entry. Writes the specified entry to the database.

        The entry should be in the form of a dict or OrderedDict.
        """
        try:
            employee_record = Employee.get(Employee.name == entry["name"])
        except DoesNotExist:
            # right now we can handle DoesNotExist cleanly because the only
            # value we need to know to create a new Employee instance is
            # provided as part of the entry.
            # If ever Employee ever becomes a more sophisticated model, we'll
            # need to go back to the user to get them to provide more info
            employee_record = Employee.create(name=entry["name"])
        LogEntry.create(
            employee=employee_record,
            date=entry["date"],
            task_name=entry["task_name"],
            duration=entry["duration"],
            notes=entry["notes"],
        )

    def edit_entry(self, entry, new_value):
        """Edits an existing entry.

        `entry` and `new_value` should be key-value pairs (e.g., dict or
        OrderedDict).

        Returns the new record as an OrderedDict.
        """
        # first make sure that the Employee exists and can be retrieved
        try:
            employee_record = Employee.get(Employee.name == entry["name"])
        except DoesNotExist as err:
            print("Employee Does not exist error!")
            print("detailed error information:")
            print(err)
            raise
        # next, make sure that the LogEntry record exists and can be retrieved
        try:
            log_entry_record = LogEntry.get(
                LogEntry.employee == employee_record,
                LogEntry.date == entry["date"],
                LogEntry.task_name == entry["task_name"],
                LogEntry.duration == entry["duration"],
                LogEntry.notes == entry["notes"]
            )
        except DoesNotExist as err:
            print("Log Entry Does not exist error!")
            print("detailed error information:")
            print(err)
            raise
        # try to set the employee record to the new employee
        employee_record = Employee.get_or_create(
            name=new_value["name"]
        )[0]
        employee_record.save()
        # try to set the log entry record to the new record
        log_entry_record.employee = employee_record
        log_entry_record.date = new_value["date"]
        log_entry_record.task_name = new_value["task_name"]
        log_entry_record.duration = new_value["duration"]
        log_entry_record.notes = new_value["notes"]
        log_entry_record.save()
        return self.record_to_dict(log_entry_record)

    def view_employees(self):
        """Get all employees who have made entries.

        Returns a list of records (where each record is an OrderedDict)
        """
        # join() defaults to inner join
        # joined = Employee.join(LogEntry)
        # query = joined.select()
        query = Employee.select(Employee.name).join(LogEntry).distinct()
        return [OrderedDict([('name', record.name)]) for record in query]

    def view_dates(self, sorted=True):
        """get all unique date records.

        Returns them as a list of OrderedDicts.
        """
        query = LogEntry.select(LogEntry.date).distinct()
        if sorted:
            query = query.order_by(LogEntry.date)
        return [OrderedDict([('date', record.date)]) for record in query]

    def view_entries_for_date(self, date):
        """Get all the entries for the given date.

        Return the entries as a list of OrderedDicts.
        """
        query = (LogEntry
                 .select()
                 .join(Employee)
                 .where(LogEntry.date == date))
        return self.records_to_list(query)

    def view_entries_for_duration(self, duration):
        """Get all the entries with the given duration.

        Returns them as a list of OrderedDicts.
        """
        query = (LogEntry
                 .select()
                 .join(Employee)
                 .where(LogEntry.duration == duration))
        return self.records_to_list(query)

    def view_entries_for_date_range(self, start_date, end_date):
        """Get all entries with a date is between start_date and
        end_date (inclusive).

        Return them as a list of OrderedDicts.
        """
        query = (LogEntry
                 .select()
                 .join(Employee)
                 .where(
                     (LogEntry.date >= start_date) &
                     (LogEntry.date <= end_date)
                 )
                 .order_by(LogEntry.date))
        return self.records_to_list(query)

    def view_entries_with_text(self, text_string):
        """Get all entries where any of the text fields contains the
        specified text string.

        Return them as a list of OrderedDicts.
        """
        query = (LogEntry
                 .select()
                 .join(Employee)
                 .where(
                     (Employee.name.contains(text_string)) |
                     (LogEntry.task_name.contains(text_string)) |
                     (LogEntry.notes.contains(text_string))
                 ))
        return self.records_to_list(query)

    def view_names_with_text(self, text_string):
        """Get all employee names where any of the text in the name matches
        the specified text string.

        Returns them as a list of OrderedDicts.
        """
        Employee.select(Employee.name).join(LogEntry).distinct()
        query = (Employee
                 .select(Employee.name)
                 .join(LogEntry)
                 .distinct()
                 .where(
                     Employee.name.contains(text_string)
                 ))
        return [OrderedDict([('name', record.name)]) for record in query]

    def view_everything(self, employee=None, date_sorted=False):
        """Gets every field for every log entry.
        - Can optionally specify a particular employee name to filter by that
        employee;
        - Can optionally sort by date.

        Returns a list of OrderedDicts.
        """
        if employee is not None:
            query = (LogEntry
                     .select()
                     .join(Employee)
                     .where(employee == Employee.name))
        else:
            query = LogEntry.select().join(Employee)
        if date_sorted:
            query = query.order_by(LogEntry.date)
        return self.records_to_list(query)

    def view_entry(self, entry, return_model=False):
        """Gets a single entry from the database that matches the
        specifications from entry.

        Returns a single entry:
        - if return_model is set to True, returns a model instance,
        - otherwise returns OrderedDict
        """
        # first make sure that the Employee exists and can be retrieved
        try:
            employee_record = Employee.get(Employee.name == entry["name"])
        except DoesNotExist as err:
            print("Employee Does not exist error!")
            print("detailed error information:")
            print(err)
            raise err
        # next, make sure that the LogEntry record exists and can be retrieved
        try:
            log_entry_record = LogEntry.get(
                LogEntry.employee == employee_record,
                LogEntry.date == entry["date"],
                LogEntry.task_name == entry["task_name"],
                LogEntry.duration == entry["duration"],
                LogEntry.notes == entry["notes"]
            )
        except DoesNotExist as err:
            print("Log Entry Does not exist error!")
            print("detailed error information:")
            print(err)
            raise err
        if return_model:
            return log_entry_record
        else:
            return self.record_to_dict(log_entry_record)

    def delete_entry(self, entry):
        """Delete the specified entry from the database."""
        log_entry = self.view_entry(entry, return_model=True)
        log_entry.delete_instance()
        return True

    # Helper Methods
    def record_to_dict(self, record):
        """Converts a value representing DB record into an OrderedDict.

        Returns that OrderedDict.
        """
        return OrderedDict([
            ('name', record.employee.name),
            ('date', record.date),
            ('task_name', record.task_name),
            ('duration', record.duration),
            ('notes', record.notes)
        ])

    def records_to_list(self, records):
        """Converts a value representing a collection of DB records into a
        list of OrderedDicts.

        Returns that list of OrderedDicts.
        """
        list = []
        for record in records:
            list.append(self.record_to_dict(record))
        return list

# -- Database Model Classes --


class Employee(Model):
    """This is the class to represent an employee"""
    name = CharField(max_length=255)

    class Meta:
        database = db


class LogEntry(Model):
    """This is the class to represent the log entry database table"""
    employee = ForeignKeyField(Employee, backref='log_entries')
    date = DateField()
    task_name = CharField(max_length=255)
    duration = IntegerField()
    notes = CharField(max_length=255)

    class Meta:
        database = db


tables = [
    Employee,
    LogEntry,
]
