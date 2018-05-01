from peewee import *


db = SqliteDatabase('work_log.db')

class LogEntry(Model):
    """This is the class to represent the log entry database table"""
    employee = CharField(max_length=255)
    date = DateField()
    task_name = CharField(max_length=255)
    duration = IntegerField()
    notes = CharField(max_length=255)

    class Meta:
        database = db

# -------------------------

if __name__ == '__main__':
    db.connect()
    db.create_tables([LogEntry], safe=True)