#!/usr/bin/env python3
from collections import OrderedDict

from peewee import *

import wl_settings as settings


db = SqliteDatabase(settings.DATABASE_NAME)

class DBManager:

    def initialize(self):
        """Create the database and the table if they don't already exist
        Note that we don't HAVE to explicitly connect to the DB now but it
        makes bug checking easier than having the connection fail when we try
        to do a query
        """
        db.connect()
        db.create_tables(tables, safe=True)
        
    def add_entry(self, entry):
        """Add an entry."""
        try:
            employee_record = Employee.get(Employee.name == entry["employee"])
        except DoesNotExist:
            # right now we can handle DoesNotExist cleanly because the only
            # value we need to know to create a new Employee instance is
            # provided as part of the entry.
            # If ever Employee ever becomes a more sophisticated model, we'll
            # need to go back to the user to get them to provide more info
            employee_record = Employee.create(name=entry["employee"])
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
        query = Employee.select(Employee.name).join(LogEntry)
        return [OrderedDict([('name', record.name)]) for record in query]
    
    def view_everything(self):
        """get every field for every log entry"""
        query = LogEntry.select().join(Employee)
        print("employee | date | task_name | duration | notes")
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
    dbm.initialize()
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