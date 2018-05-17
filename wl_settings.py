DATABASE_NAME = 'test.db'
#DATABASE_NAME = 'work_log.db'

HEADERS = {
        'user': 'employee',
        'date': 'date',
        'task_name': 'task_name',
        'duration': 'duration',
        'notes': 'notes'
}

DATE_FORMATS = {
        'iso 8601': {'UI format': 'yyyy-mm-dd',
                     'datetime format': '%Y-%m-%d'},
        'uk':       {'UI format': 'dd/mm/yyyy',
                     'datetime format': '%d/%m/%Y'},
        'us':       {'UI format': 'mm/dd/yyyy',
                     'datetime format': '%m/%d/%Y'},
}