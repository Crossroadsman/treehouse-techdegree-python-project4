class FileManager:

    def load_file(self, filename):
        file_data = None
        while file_data is None:
            try:
                file_handle = open(filename, 'r')
            except FileNotFoundError:
                print("{} not found.".format(filename))
                print("please try an alternative filename")
                filename = input("> ")
            else:
                file_data = []
                for line in file_handle.readlines():
                    file_data.append(line)
                file_handle.close()
        return file_data

    def save_file(self, file_data, filename):
        file_handle = open(filename, 'a')
        file_handle.write('hello, world')  # trailing newline req'd?
        file_handle.close()


# --------------------------

if __name__ == "__main__":

    print("test1: file read")
    file_manager = FileManager()
    file_data = file_manager.load_file('test.txt')
    for line in file_data:
        print(line)

    print("test2: file write")
    file_manager = FileManager()
    file_manager.save_file("dummy data", 'test.txt')
