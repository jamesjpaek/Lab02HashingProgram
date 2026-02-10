import os
import json
import hashlib

HASH_FILE = "hash_table.json"


def hash_file(path):
    h = hashlib.sha256()
    f = open(path, "rb")
    data = f.read()
    f.close()
    h.update(data)
    return h.hexdigest()


def traverse_directory(directory):
    result = []
    for root, _, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)
            if file != HASH_FILE:
                result.append(os.path.abspath(full_path))
    return result


def generate_hash_table():
    directory = input("Enter directory path to hash: ").strip().strip('"')
    directory = os.path.abspath(directory)

    if not os.path.isdir(directory):
        print("Invalid directory.")
        return

    files = traverse_directory(directory)
    table = {}

    for file in files:
        table[file] = hash_file(file)

    with open(os.path.join(directory, HASH_FILE), "w") as f:
        json.dump(table, f, indent=2)

    print("Hash table generated, proceed")


def verify_hashes():
    path = input("Enter path to hash table (.json): ").strip().strip('"')
    path = os.path.abspath(path)

    if not os.path.isfile(path):
        print("Invalid ht - hash table path.")
        return

    with open(path, "r") as f:
        table = json.load(f)

    directory = os.path.dirname(path)
    current_files = traverse_directory(directory)

    for stored_file in table:
        if stored_file not in current_files:
            print(stored_file + " file deleted")

    for file in current_files:
        if file not in table:
            print(file + " new file added")
        else:
            current_hash = hash_file(file)
            if current_hash == table[file]:
                print(file + " hash is valid")
            else:
                print(file + " hash is invalid")


def main():
    print("Lab02HashingProgram")
    print("1) Generate a new hash table")
    print("2) Verify hashes")

    choice = input("Pick an option (1 or 2): ").strip()

    if choice == "1":
        generate_hash_table()
    elif choice == "2":
        verify_hashes()
    else:
        print("Error, invalid directory, rerun the terminal.")


main()
