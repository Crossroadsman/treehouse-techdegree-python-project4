import datetime
import re

#from csv_manager import CsvManager
from db_manager import DBManager
import wl_settings as settings

class Menu:

    # STATUS VARIABLES
    # ----------------
    quit = False

    # INITIALIZER
    # -----------
    def __init__(self):
        print("\nWORK LOG")
        print("========")
        self.OPTIONS = {
            'date format': settings.DATE_FORMATS['iso 8601'],
            'save format (date)': settings.DATE_FORMATS['iso 8601'],
            'case sensitive search': False,
            'entries per page': 10,
            'allow future dates': False,
            'earliest allowed date': datetime.datetime(1900,1,1),
        }
        self.current_record = 0
        self.current_page_start = 0

        menu = self.main_menu()
        while not self.quit:
            menu = menu()

    # MENU METHODS
    # ------------
    def main_menu(self):
        """This is the root menu. The user selects which activity to perform
        and then the method returns the function for the activity.
        """
        inputs = {
            'a': {'text': 'Add new entry',
                  'function': self.add_entry},
            's': {'text': 'Search in existing entries',
                  'function': self.search_entries},
            'o': {'text': 'Options',
                  'function': self.options},
            'q': {'text': 'Quit program',
                  'function': self.quit_program}
        }
        while True:
            print("\nMAIN MENU")
            print("What would you like to do?")
            for key, value in inputs.items():
                print("{}) {}".format(key, value['text']))
            user_entry = input("> ").lower()

            if user_entry not in inputs.keys():
                continue

            return inputs[user_entry]['function']

    def add_entry(self):
        """This is the menu where the user can add a task that was completed
        """
        while True:
            print("\nADD ENTRY")
            print("Username")
            input_text = input("Enter your name > ")
            username = input_text
            date = None
            while date is None:
                print("Date of the Task")
                user_entry = self.date_entry()
                if user_entry[0] is not None:  # error
                    print(user_entry[0])
                    continue
                else:
                    date = user_entry[1]
                    date_string = self.date_to_string(date, target='file')
            print("Name of the Task")
            input_text = input("Enter the name of the task > ")
            task_name = input_text
            time_spent = None
            while time_spent is None:
                print("Time spent")
                print("Enter a whole number of minutes (rounded)")
                input_text = input("> ")
                try:
                    time_spent = int(input_text)
                except ValueError:
                    print("Invalid value, please try again")
                    continue
                if time_spent < 0:
                    print("Invalid value, please try again")
                    continue
            print("Notes")
            input_text = input("(Optional, leave blank for none) ")
            notes = input_text
            # call method to write data to file
            dbm = DBManager()
            file_data = {
                settings.HEADERS['user']: username,
                settings.HEADERS['date']: date_string,
                settings.HEADERS['task_name']: task_name,
                settings.HEADERS['duration']: time_spent,
                settings.HEADERS['notes']: notes
            }
            dbm.add_entry(file_data)
            return self.main_menu

    def options(self):
        """This is the menu where the user can specify user-configurable
        options
        """
        print('OPTIONS')

        print("Choose a display date format")
        menu_choices = list(settings.DATE_FORMATS.keys())
        menu_size = len(menu_choices)
        for i in range(len(menu_choices)):
            print("({}) - {}".format(i + 1, menu_choices[i]))
        input_text = input("> ")
        if input_text in [str(x) for x in range(1, menu_size + 1)]:
            choice = int(input_text) - 1
            choice = menu_choices[choice]
            print("You chose: {}".format(choice))
            self.OPTIONS['date format'] = settings.DATE_FORMATS[choice]
            print('going back to main menu')
        else:
            print("Invalid entry, returning to main menu")

        return self.main_menu

    def search_entries(self):
        """This is the search menu. The user selects how they want to search.
        """
        inputs = {
            'l': {'text': 'employee names List',
                  'function': self.search_employee},
            'e': {'text': 'Employee name Search',
                  'function': self.search_employee_text},
            'd': {'text': 'single Date',
                  'function': self.search_exact_date},
            'r': {'text': 'date Range',
                  'function': self.search_date_range},
            't': {'text': 'Time spent',
                  'function': self.search_time_spent},
            's': {'text': 'text Search',
                  'function': self.search_text_search},
            'b': {'text': 'Back to main menu',
                  'function': self.main_menu}
        }
        while True:
            print("\nSEARCH ENTRIES")
            print("How would you like to search?")
            for key, value in inputs.items():
                print("{}) {}".format(key, value['text']))
            user_entry = input("> ").lower()

            if user_entry not in inputs.keys():
                continue
            return inputs[user_entry]['function']

    def quit_program(self):
        print("Quitting")
        self.quit = True

    def present_results(self):
        """Show all the results from the search and then provide interaction
        choices
        """
        inputs = {
            'n': {'text': 'Next page',
                  'function': self.next_page},
            'p': {'text': 'Previous page',
                  'function': self.previous_page},
            'v': {'text': 'View detail',
                  'function': self.select_detail},
            'e': {'text': 'Edit',
                  'function': self.edit_record},
            'd': {'text': 'Delete',
                  'function': self.delete_record},
            'm': {'text': 'go back to Main menu',
                  'function': self.main_menu},
            'q': {'text': 'quit',
                  'function': self.quit_program},
        }
        if self.current_page_start == 0:
            del(inputs['p'])
        next_start = self.current_page_start + self.OPTIONS['entries per page']
        if next_start >= len(self.records):
            del(inputs['n'])
        print("\nSearch Results")
        if len(self.records) > next_start:
            current_page_end = next_start
        else:
            current_page_end = len(self.records) - 1
        for index in range(self.current_page_start, current_page_end + 1):
            value = self.records[index]
            short_form = self.display_entry(value, return_only=True)
            print("{}) {}".format(index + 1, short_form))

        print("\nAvailable actions:")
        for key, value in inputs.items():
            print('{}) {}'.format(key, value['text']))

        while True:
            user_entry = input("> ").lower()

            if user_entry not in inputs.keys():
                continue
            return inputs[user_entry]['function']

    def present_next_result(self):
        """Show the next available result"""
        inputs = {
            'p': {'text': 'Previous',
                  'function': self.previous_result},
            'n': {'text': 'Next',
                  'function': self.next_result},
            'b': {'text': 'Back to list view',
                  'function': self.present_results},
            'e': {'text': 'Edit',
                  'function': self.edit_current_record},
            'd': {'text': 'Delete',
                  'function': self.delete_current_record},
            'm': {'text': 'go back to Main menu',
                  'function': self.main_menu},
            'q': {'text': 'quit',
                  'function': self.quit_program},
        }
        if self.current_record == 0:
            del(inputs['p'])
        if self.current_record == len(self.records) - 1:
            del(inputs['n'])
        print("\nResult {}".format(self.current_record + 1))
        record = self.records[self.current_record]
        print("this is the record: {}".format(record))
        self.display_entry(record, verbose=True)

        print("\nAvailable actions:")
        for key, value in inputs.items():
            print('{}) {}'.format(key, value['text']))

        while True:
            user_entry = input("> ").lower()

            if user_entry not in inputs.keys():
                continue
            return inputs[user_entry]['function']

    # Specific Search Menus
    # .....................
    def search_employee(self):
        """This is the menu where the user is given a list of all employees
        who have entries, and can select a particular employee to see
        all their entries"""
        print("\nSEARCH BY EMPLOYEE")
        #load the db manager
        dbm = DBManager()
        employee_names = dbm.view_employees()
        for i, value in enumerate(employee_names):
            print("{}) {}".format(i + 1, value['name']))
        selected_employee = None
        while selected_employee is None:
            user_input = input("> ")
            # perform input validation
            try:
                user_input = int(user_input) - 1
            except ValueError:
                print("Invalid value, try again")
                continue
            if user_input < 0:
                print("Value out of range. Try again.")
                continue
            try:
                selected_employee = employee_names[user_input]['name']
                print(selected_employee)
            except IndexError:
                print("Value out of range. Try again.")
                continue
            # when an employee is selected, show all the entries with that e'ee
            matching_records = dbm.view_everything(employee=selected_employee)
        self.records = matching_records
        print(self.records)
        self.current_record = 0
        return self.present_next_result

    def search_employee_text(self):
        """This is the menu where the user enters a text string and is presented
        with all employee names containing that string
        """
        print('FIND EMPLOYEE NAME USING TEXT STRING')
        print("Enter the text string to search on")
        input_text = input("> ")
        text_string = input_text
        # load db
        dbm = DBManager()
        employee_names = dbm.view_names_with_text(text_string)
        for i, value in enumerate(employee_names):
            print("{}) {}".format(i + 1, value['name']))
        selected_employee = None
        while selected_employee is None:
            user_input = input("> ")
            # perform input validation
            try:
                user_input = int(user_input) - 1
            except ValueError:
                print("Invalid value, try again")
                continue
            if user_input < 0:
                print("Value out of range. Try again.")
                continue
            try:
                selected_employee = employee_names[user_input]['name']
                print(selected_employee)
            except IndexError:
                print("Value out of range. Try again.")
                continue
            # when an employee is selected, show all the entries with that e'ee
            matching_records = dbm.view_everything(employee=selected_employee)
        self.records = matching_records
        print(self.records)
        self.current_record = 0
        return self.present_next_result

    def search_exact_date(self):
        """This is the menu where the user browses dates and entries and picks
        the date from a list
        """
        print("\nSEARCH EXACT DATE")
        # load the db manager
        dbm = DBManager()
        date_records = dbm.view_dates()
        for i, value in enumerate(date_records):
            value = self.date_to_string(value['date'])
            print("{}) {}".format(i + 1, value))
        selected_date = None
        while selected_date is None:
            user_input = input("> ")
            # perform input validation
            try:
                user_input = int(user_input) - 1
            except ValueError:
                print("Invalid value, try again")
                continue
            if user_input < 0:
                print("Value out of range. Try again.")
                continue
            try:
                selected_date = date_records[user_input]['date']
            except IndexError:
                print("Value out of range. Try again.")
                continue

            # when a date is selected, show all the entries with that date
            matching_records = dbm.view_entries_for_date(selected_date)
        self.records = matching_records
        self.current_record = 0
        return self.present_next_result

    def search_date_range(self):
        """This is the menu where the user can enter a from date and to date
        and get back every entry from within that range
        """
        print('SEARCH DATE RANGE')
        start_date = None
        end_date = None
        # get start_date
        while start_date is None:
            print("Start Date:")
            user_entry = self.date_entry()
            if user_entry[0] is not None:  # error
                print(user_entry[0])
                continue
            else:
                start_date = user_entry[1]
        # get end_date
        while end_date is None:
            print("End Date:")
            user_entry = self.date_entry()
            if user_entry[0] is not None:  # error
                print(user_entry[0])
                continue
            else:
                end_date = user_entry[1]
        # load db
        dbm = DBManager()
        # switch start and end dates if end < start
        if end_date < start_date:
            current_date = end_date
            end_date = start_date
            start_date = end_date
        else:
            current_date = start_date
        # get all records in date range
        matching_records = dbm.view_entries_for_date_range(start_date, end_date)

        print("\nShowing entries:")
        if len(matching_records) == 0:
            print("\nNo matches, returning to search menu")
            return self.search_entries
        self.records = matching_records
        self.current_record = 0
        return self.present_next_result

    def search_time_spent(self):
        """This is the menu where the user enters the number of minutes a task
        took and be able to choose one to see entries from
        """
        print('SEARCH BY TIME SPENT')
        print("Time spent")
        time_spent = None
        while time_spent is None:
            input_text = input("Enter a whole number of minutes (rounded) ")
            try:
                time_spent = int(input_text)
            except ValueError:
                print("Invalid value")
                continue
        # load db
        dbm = DBManager()
        matching_records = dbm.view_entries_for_duration(time_spent)
        if len(matching_records) == 0:
            print("\nNo matches, returning to search menu")
            return self.search_entries
        self.records = matching_records
        self.current_record = 0
        return self.present_next_result

    def search_text_search(self):
        """This is the menu where the user enters a text string and is presented
        with all entries containing that string in the task name or notes
        """
        print('SEARCH USING TEXT STRING')
        print("Enter the text string to search on")
        input_text = input("> ")
        text_string = input_text
        # load db
        dbm = DBManager()
        matching_records = dbm.view_entries_with_text(text_string)
        if len(matching_records) == 0:
            print("\nNo matches, returning to search menu")
            return self.search_entries
        self.records = matching_records
        self.current_record = 0
        return self.present_next_result
    
    # Modification Methods
    # --------------------
    def edit_record(self):
        print("edit record")
        print('enter the record number to edit')
        user_input = input("> ")
        match_index = int(user_input) - 1
        record = self.records[match_index]
        # get the new values for the record
        print("New Username")
        input_text = input("Enter the username > ")
        username = input_text
        date = None
        while date is None:
            print("New date of the Task")
            user_entry = self.date_entry()
            if user_entry[0] is not None:  # error
                print(user_entry[0])
                continue
            else:
                date = user_entry[1]
                date_string = self.date_to_string(date, target='file')
        print("New name of the Task")
        input_text = input("Enter the name of the task > ")
        task_name = input_text
        time_spent = None
        while time_spent is None:
            print("New time spent")
            input_text = input("Enter a whole number of minutes (rounded) ")
            try:
                time_spent = int(input_text)
            except ValueError:
                print("Invalid value")
                continue
        print("New notes")
        input_text = input("(Optional, leave blank for none) ")
        notes = input_text
        # load the csv
        csvm = CsvManager()
        csv_data = csvm.load_csv(self.DATASTORE_FILENAME)
        # find the row that matches record
        for row in csv_data:
            if row == record:
                row[settings.HEADERS['user']] = username
                row[settings.HEADERS['date']] = date_string
                row[settings.HEADERS['task_name']] = task_name
                row[settings.HEADERS['duration']] = time_spent
                row[settings.HEADERS['notes']] = notes
        # save the csv
        csvm.save_csv(csv_data, self.DATASTORE_FILENAME, truncate=True)
        return self.main_menu

    def edit_current_record(self):
        print("edit record")
        match_index = self.current_record
        record = self.records[match_index]
        # get the new values for the record
        print("New Username")
        input_text = input("Enter the username > ")
        username = input_text
        date = None
        while date is None:
            print("New date of the Task")
            user_entry = self.date_entry()
            if user_entry[0] is not None:  # error
                print(user_entry[0])
                continue
            else:
                date = user_entry[1]
                date_string = self.date_to_string(date, target='file')
        print("New name of the Task")
        input_text = input("Enter the name of the task > ")
        task_name = input_text
        time_spent = None
        while time_spent is None:
            print("New time spent")
            input_text = input("Enter a whole number of minutes (rounded) ")
            try:
                time_spent = int(input_text)
            except ValueError:
                print("Invalid value")
                continue
        print("New notes")
        input_text = input("(Optional, leave blank for none) ")
        notes = input_text
        # load the csv
        csvm = CsvManager()
        csv_data = csvm.load_csv(self.DATASTORE_FILENAME)
        # find the row that matches record
        for row in csv_data:
            if row == record:
                row[settings.HEADERS['user']] = username
                row[settings.HEADERS['date']] = date_string
                row[settings.HEADERS['task_name']] = task_name
                row[settings.HEADERS['duration']] = time_spent
                row[settings.HEADERS['notes']] = notes
        # save the csv
        csvm.save_csv(csv_data, self.DATASTORE_FILENAME, truncate=True)
        return self.main_menu

    def select_detail(self):
        print("View record")
        print('enter the record number to view')
        user_input = input("> ")
        match_index = int(user_input) - 1
        self.current_record = match_index
        return self.present_next_result

    def delete_record(self):
        print("delete record")
        print('enter the record number to delete')
        user_input = input("> ")
        match_index = int(user_input) - 1
        record = self.records[match_index]
        # load te csv
        csvm = CsvManager()
        csv_data = csvm.load_csv(self.DATASTORE_FILENAME)
        # find the row that matches record
        for row in csv_data:
            if row == record:
                # delete that reow
                csv_data.remove(row)
                break
        # save the csv
        csvm.save_csv(csv_data, self.DATASTORE_FILENAME, truncate=True)
        return self.main_menu

    def delete_current_record(self):
        print("delete record")
        match_index = self.current_record
        record = self.records[match_index]
        # load te csv
        csvm = CsvManager()
        csv_data = csvm.load_csv(self.DATASTORE_FILENAME)
        # find the row that matches record
        for row in csv_data:
            if row == record:
                # delete that row
                csv_data.remove(row)
                break
        # save the csv
        csvm.save_csv(csv_data, self.DATASTORE_FILENAME, truncate=True)
        return self.main_menu

    # Other UI Methods
    # ----------------
    def display_entry(self, entry, verbose=False, return_only=False):
        """This method displays a selected entry, showing:
        - date (read from file in iso 8601 and displayed in whatever is set in
          options)
        - task name
        - time taken
        - any notes
        """
        username = entry[settings.HEADERS['user']]
        date_object = entry[settings.HEADERS['date']]
        date = self.date_to_string(date_object, target="display")
        task_name = entry[settings.HEADERS['task_name']]
        time_taken = entry[settings.HEADERS['duration']]
        notes = entry[settings.HEADERS['notes']]
        if verbose:
            line0 = username
            print(line0)
            line1 = "{}: {}".format(date, task_name)
            print(line1)
            print("-" * len(line1))
            print("{} minutes".format(time_taken))
            print("{}".format(notes))
        else:
            short_form = "{}: {} ({}m): {} | {}".format(username,
                                                    date,
                                                    time_taken,
                                                    task_name,
                                                    notes)
            if return_only:
                return short_form
            else:
                print(short_form)

    def previous_result(self):
        """load previous result"""
        self.current_record -= 1
        return self.present_next_result

    def next_result(self):
        """load next result"""
        self.current_record += 1
        return self.present_next_result

    def previous_page(self):
        """load previous page of results"""
        self.current_page_start -= self.OPTIONS['entries per page']
        return self.present_results

    def next_page(self):
        """load next page of results"""
        self.current_page_start += self.OPTIONS['entries per page']
        return self.present_results

    # Helper Methods
    # --------------
    def validate_date_entry(self, date_string, date_format):
        """Takes a date_string and date_format and attempts to create
        a valid datetime object with those imports.
        Returns a tuple in the form (error, datetime) where:
        - `error` is None if valid and a description of the error text if
          invalid;
        - `datetime` is a datetime object if valid and None if invalid
        """
        try:
            naive_datetime = datetime.datetime.strptime(
                date_string,
                date_format['datetime format']
            )
        except ValueError:
            error_text = "{date_string} is not valid in format {date_format}"
            error_args = {"date_string": date_string,
                          "date_format": date_format['UI format']}
            return (error_text.format(**error_args), None)
        else:
            if not self.OPTIONS['allow future dates']:
                if naive_datetime > datetime.datetime.now():
                    error_text = "dates in the future are not permitted"
                    error_args = {"date_string": date_string,
                          "date_format": date_format['UI format']}
                    return (error_text.format(**error_args), None)
                if naive_datetime < self.OPTIONS['earliest allowed date']:
                    bad_date = self.OPTIONS['earliest allowed date'].strftime(
                        self.OPTIONS['date format']['datetime format']
                    )
                    error_text = "dates before {} are not permitted".format(
                        bad_date
                    )
                    error_args = {"date_string": date_string,
                          "date_format": date_format['UI format']}
                    return (error_text.format(**error_args), None)
            return (None, naive_datetime)

    def date_entry(self):
        """This helper function asks for a date input in the user's preferred
        format and then returns that date as a naive datetime object
        """
        date_format = self.OPTIONS['date format']
        input_text = "Please use the '{}' date format: "
        user_entry = input(input_text.format(date_format['UI format']))
        # validate date entry
        validated = self.validate_date_entry(user_entry, date_format)
        return validated

    def date_to_string(self, date_object, target='display'):
        """This helper function takes a naive date object and returns a
        string representation in:
        - `target='display'`: the user's preferred display format
        - `target='file': the save format
        """
        if target == 'display':
            option = self.OPTIONS['date format']
            string_format = option['datetime format']
        elif target == 'file':
            option = self.OPTIONS['save format (date)']
            string_format = option['datetime format']
        else:  # unrecognised target, fallback to write mode
            option = self.OPTIONS['save format (date)']
            string_format = option['datetime format']
        return date_object.strftime(string_format)

# ---------------------------

if __name__ == "__main__":

    menu = Menu()
