from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python import run_python_file


def run_tests():
    # get_files_info
    print("Test 1: get_files_info('calculator', '.')")
    print(get_files_info("calculator", "."), "\n")

    print("Test 2: get_files_info('calculator', 'pkg')")
    print(get_files_info("calculator", "pkg"), "\n")

    print("Test 3: get_files_info('calculator', '/bin')")
    print(get_files_info("calculator", "/bin"), "\n")

    print("Test 4: get_files_info('calculator', '../')")
    print(get_files_info("calculator", "../"), "\n")

    # get_file_content    
    print("Test 1: main.py")
    print(get_file_content("calculator", "main.py"))
    print()
    
    print("Test 2: pkg/calculator.py")
    print(get_file_content("calculator", "pkg/calculator.py"))
    print()
    
    print("Test 3: invalid file outside scope")
    print(get_file_content("calculator", "/bin/cat"))
    print()

    # write_file
    print("Test 1: Overwrite lorem.txt")
    print(write_file("calculator", "lorem.txt", "wait, this isn't lorem ipsum"))
    print()

    print("Test 2: Write to pkg/morelorem.txt")
    print(write_file("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet"))
    print()

    print("Test 3: Write outside working directory")
    print(write_file("calculator", "/tmp/temp.txt", "this should not be allowed"))
    print()

    # run_python_file
    print("Test 1: run main.py")
    print(run_python_file("calculator", "main.py"))
    print()

    print("Test 2: run tests.py")
    print(run_python_file("calculator", "tests.py"))
    print()

    print("Test 3: run ../main.py (should fail)")
    print(run_python_file("calculator", "../main.py"))
    print()

    print("Test 4: run nonexistent.py (should fail)")
    print(run_python_file("calculator", "nonexistent.py"))
    print()


if __name__ == "__main__":
    run_tests()
