import os
import json
import hashlib

HASH_TABLE_FILE = "hash_table.json"
CHUNK_SIZE = 1024 * 1024  # 1MB


def hash_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def traverse_directory(directory):
    files_list = []
    for root, _, files in os.walk(directory):
        for name in files:
            full_path = os.path.join(root, name)

            # don't hash our own json table if it's inside the folder
            if os.path.basename(full_path) == HASH_TABLE_FILE:
                continue

            files_list.append(os.path.abspath(full_path))
    return files_list


def generate_table():
    directory = input("Enter directory path to hash: ").strip().strip('"')
    directory = os.path.abspath(directory)

    if not os.path.isdir(directory):
        print("Invalid directory.")
        return

    filepaths = traverse_directory(directory)

    table = {"root_directory": directory, "files": []}

    for fp in filepaths:
        try:
            table["files"].append({"filepath": fp, "hash": hash_file(fp)})
        except Exception:
            print(f"Skipped: {fp}")

    out_path = os.path.join(directory, HASH_TABLE_FILE)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(table, f, indent=2)

    print("Hash table generated")


def verify_hashes():
    json_path = input("Enter path to hash table (.json): ").strip().strip('"')
    json_path = os.path.abspath(json_path)

    if not os.path.isfile(json_path):
        print("Invalid hash table path.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        table = json.load(f)

    root_dir = table["root_directory"]
    stored = table["files"]

    stored_paths = {x["filepath"] for x in stored}
    stored_hash_by_path = {x["filepath"]: x["hash"] for x in stored}

    current_files = set(traverse_directory(root_dir))

    deleted_files = sorted(list(stored_paths - current_files))
    new_files = sorted(list(current_files - stored_paths))

    for fp in deleted_files:
        print(f"{fp} file deleted")

    for fp in new_files:
        print(f"{fp} new file added")

    # validate same-path files
    for fp in sorted(list(current_files & stored_paths)):
        try:
            current_hash = hash_file(fp)
            if current_hash == stored_hash_by_path[fp]:
                print(f"{fp} hash is valid")
            else:
                print(f"{fp} hash is invalid")
        except Exception:
            print(f"{fp} hash is invalid")

    # BONUS: rename detection (deleted path + new path, same hash)
    updated = False
    if deleted_files and new_files:
        new_hashes = {}
        for fp in new_files:
            try:
                new_hashes[fp] = hash_file(fp)
            except Exception:
                pass

        for old_fp in deleted_files:
            old_hash = stored_hash_by_path.get(old_fp)
            if not old_hash:
                continue

            match_new = None
            for new_fp, new_h in new_hashes.items():
                if new_h == old_hash:
                    match_new = new_fp
                    break

            if match_new:
                for entry in stored:
                    if entry["filepath"] == old_fp:
                        entry["filepath"] = match_new
                        updated = True
                        break

                print(f"Renamed file detected: {old_fp} -> {match_new}")
                new_hashes.pop(match_new, None)

    if updated:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(table, f, indent=2)
        print("Hash table updated (rename fix)")

    print("Verification complete")


def main():
    print("Lab02HashingProgram")
    print("1) Generate a new hash table")
    print("2) Verify hashes")

    choice = input("Select an option (1 or 2): ").strip()

    if choice == "1":
        generate_table()
    elif choice == "2":
        verify_hashes()
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()
