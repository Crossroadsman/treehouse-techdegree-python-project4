import csv


class CsvManager:

    def load_csv(self, filename, mode='d', delimiter=',', quotechar='"'):
        '''Opens the specified file. If the specified file is not found,
        prompts the user for an alternative filename.
        Accepts optional arguments for:
        `delimiter`
        `quotechar`
        In case the CSV is encoded with a different format
        Turns each row of the file into a list (mode='l') where each element
        corresponds to a column in the CSV file; or an OrderDict (mode='d')
        where every field becomes the value in a dictionary entry where the
        key is the column name.
        '''
        csv_data = None
        while csv_data is None:
            try:
                file_handle = open(filename, 'r')
            except FileNotFoundError:
                print("{} not found.".format(filename))
                print("please try an alternative filename")
                filename = input("> ")
            else:
                if mode == 'l':  # list
                    csv_data = []
                    csv_reader = csv.reader(file_handle,
                                            delimiter=delimiter,
                                            quotechar=quotechar)
                    for line in csv_reader:
                        csv_data.append(line)
                else:  # dict
                    csv_reader = csv.DictReader(file_handle,
                                                delimiter=delimiter,
                                                quotechar=quotechar)
                    csv_data = list(csv_reader)
            file_handle.close()
        return csv_data

    def save_csv(self,
                 file_data,
                 filename,
                 field_names=None,
                 mode='d',
                 truncate=False):
        '''If field_names is None uses the first row of file_data as the column
        headings, otherwise uses the values in field_names (which must match
        the keys in the dictionary)

        If mode is 'd', the data in file_data is handled as a list of
        dictionaries. If mode is 'l', the data in file_data is handled as a
        list.

        The method checks whether the file exists, if it doesn't then when in
        'd' mode it will write a header row to the file. If the file doesn't
        exist and is running in 'd' mode, it will not write the header row to
        the file.

        The method has an optional truncate switch. When set to True, the
        whole file will be replaced (useful for arbitrary changes to the file
        where Python can load the whole file, make changes and then write back
        the whole file). Otherwise the file will be created/appended as
        necessary.
        '''
        if truncate:
            file_handle = open(filename, mode='w')
            new_file = True
        else:
            try:
                file_handle = open(filename, mode='x')
            except:
                file_handle = open(filename, mode='a')
                new_file = False
            else:
                new_file = True

        if mode == 'l':
            csv_writer = csv.writer(file_handle)
            if field_names is not None:
                csv_writer.writerow(field_names)
            csv_writer.writerows(file_data)
        else:  # mode == 'd'
            if field_names is None:
                field_names = file_data[0].keys()
            csv_writer = csv.DictWriter(file_handle, fieldnames=field_names)
            if new_file:
                csv_writer.writeheader()
            csv_writer.writerows(file_data)  # where file_data is a dict

        file_handle.close()

# -----------------------------

if __name__ == "__main__":
    print("Tests")

    filename = "test.csv"
    print("\nTest1: output as list")
    csv_manager = CsvManager()
    csv_data = csv_manager.load_csv(filename, mode='l')

    for row in csv_data:
        print(row)

    print("\nTest2: output as dict")
    csv_manager = CsvManager()
    csv_data = csv_manager.load_csv(filename, mode='d')

    for row in csv_data:
        for col, val in row.items():
            print("{}: {}".format(col, val))
