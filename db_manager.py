#!/usr/bin/env python3
from collections import OrderedDict

from peewee import *

import wl_settings as settings


db = SqliteDatabase(settings.DATABASE_NAME)

class DBManager:

    def __init__(self):
        """Create the database and the table if they don't already exist
        Note that we don't HAVE to explicitly connect to the DB now but it
        makes bug checking easier than having the connection fail when we try
        to do a query
        """
        try:
            db.connect()
        except OperationalError as err:
            if err == "Connection already opened.":
                print('connection open, skipping connect()')
            else:
                print("operational error!")
                print("detailed error information:")
                print(err)
        db.create_tables(tables, safe=True)
        
    def add_entry(self, entry):
        """Add an entry."""
        print(entry)
        try:
            employee_record = Employee.get(Employee.name == entry["name"])
        except DoesNotExist:
            # right now we can handle DoesNotExist cleanly because the only
            # value we need to know to create a new Employee instance is
            # provided as part of the entry.
            # If ever Employee ever becomes a more sophisticated model, we'll
            # need to go back to the user to get them to provide more info
            employee_record = Employee.create(name=entry["name"])
        except IntegrityError as err:
            # if unable to create a record because it would violate, e.g.,
            # a UNIQUE constraint.
            # Note this won't help us we accidentally try to add duplicate
            # records that don't violate any constraints.

            #current_record = LogEntry.get(<some unique field>)
            #current_record.employee = entry['employee']
            #<etc>
            #current_record.save()
            print("integrity error!")
            print("detailed error information:")
            print(err)
        try:
            LogEntry.create(
                employee=employee_record,
                date=entry["date"],
                task_name=entry["task_name"],
                duration=entry["duration"],
                notes=entry["notes"],
            )
        except IntegrityError as err:
            print("integrity error!")
            print("detailed error information:")
            print(err)

    def view_employees(self):
        """get all employees who have made entries"""
        # join() defaults to inner join
        #joined = Employee.join(LogEntry)
        #query = joined.select()
        query = Employee.select(Employee.name).join(LogEntry).distinct()
        return [OrderedDict([('name', record.name)]) for record in query]

    def view_dates(self, sorted=True):
        """get all unique date records"""
        query = LogEntry.select(LogEntry.date).distinct()
        if sorted:
            query = query.order_by(LogEntry.date)
        return [OrderedDict([('date', record.date)]) for record in query]

    def view_entries_for_date(self, date):
        """get all the entries for the given date"""
        query = (LogEntry
                 .select()
                 .join(Employee)
                 .where(LogEntry.date == date)
        )
        return self.records_to_list(query)

    def view_entries_for_duration(self, duration):
        """get all the entries for the given duration"""
        query = (LogEntry
                 .select()
                 .join(Employee)
                 .where(LogEntry.duration == duration)
        )
        return self.records_to_list(query)
    
    def view_entries_for_date_range(self, start_date, end_date):
        """get all entries with a date is between start_date and
        end_date (inclusive)"""
        query = (LogEntry
                 .select()
                 .join(Employee)
                 .where(
                     (LogEntry.date >= start_date) &
                     (LogEntry.date <= end_date)
                 )
                 .order_by(LogEntry.date)
        )
        return self.records_to_list(query)

    def view_entries_with_text(self, text_string):
        """Get all entries where any of the text fields contains the
        specified text string"""
        query = (LogEntry
                 .select()
                 .join(Employee)
                 .where(
                     (Employee.name.contains(text_string)) |
                     (LogEntry.task_name.contains(text_string)) |
                     (LogEntry.notes.contains(text_string))
                 )
        )
        return self.records_to_list(query)

    def view_names_with_text(self, text_string):
        """Get all employee names where any of the text in the name matches
        the specified text string"""
        Employee.select(Employee.name).join(LogEntry).distinct()
        query = (Employee
                 .select(Employee.name)
                 .join(LogEntry)
                 .distinct()
                 .where(
                     Employee.name.contains(text_string)
                 )
        )
        return [OrderedDict([('name', record.name)]) for record in query]

    def view_everything(self, employee=None, date_sorted=False):
        """get every field for every log entry
        - Can optionally specify a particular employee name to filter by that
        employee
        - Can optionally sort by date
        """
        if employee is not None:
            query = (LogEntry
                     .select()
                     .join(Employee)
                     .where(employee == Employee.name)
            )
        else:
            query = LogEntry.select().join(Employee)
        if date_sorted:
            query = query.order_by(LogEntry.date)
        return self.records_to_list(query)

    def view_entries(self):
        """View previous entries"""

    def delete_entry(self, entry):
        """Delete the specified entry"""

    # Helper Methods
    def record_to_dict(self, record):
        """Takes a single record and returns an OrderedDict representing that 
        data"""
        return OrderedDict([
            ('name', record.employee.name),
            ('date', record.date),
            ('task_name', record.task_name),
            ('duration', record.duration),
            ('notes', record.notes)
        ])

    def records_to_list(self, records):
        """Creates a list from a collection of records"""
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

# -----------------------------

if __name__ == "__main__":

    log_entries = [
        {'employee': 'lucy',
        'date': '2015-07-07',
        'task_name': 'be the original dog',
        'duration': 1,
        'notes': 'Very class dog'},
        {'employee': 'rosie',
        'date': '2018-01-03',
        'task_name': 'be the most mischievous but loveable puppy',
        'duration': 2,
        'notes': 'Naughty but nice!'},
    ]

    def add_log_entries(log_entries_list):
        for entry in log_entries_list:
            dbm.add_entry(entry)

    dbm = DBManager()
    #menu_loop()

    # Peewee ORM methods
    # create a new instance 'all at once'
    # .create()
    #add_employees(employees)
    add_log_entries(log_entries)

    # retrieve records in table
    # .select()
    
    # retrieve a single record
    # .get()

    # update a row in table
    # .save()

    # remove a record
    # .delete_instance()

    # specify sort criteria
    # .order_by()