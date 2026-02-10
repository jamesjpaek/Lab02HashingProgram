import os
import json
import hashlib

TABLE_NAME = "hash_table.json"
CHUNK_SIZE = 1024 * 1024  # 1MB


# Hashing
def hash_file(filepath):
    """Return SHA-256 hash of file contents."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def get_all_files(directory):
    """Return a list of full file paths in the directory (including subfolders)."""
    files_list = []
    for root, _, files in os.walk(directory):
        for name in files:
            full_path = os.path.join(root, name)
            # Skip the hash table if it exists in the same folder
            if os.path.basename(full_path) == TABLE_NAME:
                continue
            files_list.append(os.path.abspath(full_path))
    return files_list


# Option 1: Generate Table
def generate_table():
    directory = input("Enter directory path to hash: ").strip().strip('"')
    directory = os.path.abspath(directory)

    if not os.path.isdir(directory):
        print("Invalid directory.")
        return

    filepaths = get_all_files(directory)

    table = {
        "root_directory": directory,
        "files": []
    }

    for fp in filepaths:
        try:
            table["files"].append({
                "filepath": fp,
                "hash": hash_file(fp)
            })
        except Exception:
            print(f"Skipped: {fp}")

    out_path = os.path.join(directory, TABLE_NAME)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(table, f, indent=2)

    print("Hash table generated")


# Option 2: Verify Hashes
# BONUS: Detect rename if hash matches
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

    # stored maps
    stored_paths = {x["filepath"] for x in stored}
    stored_hash_by_path = {x["filepath"]: x["hash"] for x in stored}
    stored_hash_to_path = {x["hash"]: x["filepath"] for x in stored}  # for rename detection

    # current scan
    current_files = set(get_all_files(root_dir))

    # Deleted + New
    deleted_files = sorted(list(stored_paths - current_files))
    new_files = sorted(list(current_files - stored_paths))

    for fp in deleted_files:
        print(f"{fp} file deleted")

    for fp in new_files:
        print(f"{fp} new file added")

    # Validate files that still exist (same path)
    for fp in sorted(list(current_files & stored_paths)):
        try:
            current_hash = hash_file(fp)
            if current_hash == stored_hash_by_path[fp]:
                print(f"{fp} hash is valid")
            else:
                print(f"{fp} hash is invalid")
        except Exception:
            print(f"{fp} hash is invalid")

    # BONUS: Rename detection
    # If a file was "deleted" but a "new" file has the same hash, update the table
    updated = False
    if deleted_files and new_files:
        # hash all new files once
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

            # find new file with same hash
            match_new = None
            for new_fp, new_h in new_hashes.items():
                if new_h == old_hash:
                    match_new = new_fp
                    break

            if match_new:
                # update stored table entry filepath
                for entry in stored:
                    if entry["filepath"] == old_fp:
                        entry["filepath"] = match_new
                        updated = True
                        break
                print(f"Renamed file detected: {old_fp} -> {match_new}")
                new_hashes.pop(match_new, None)

    if updated:
        # write updated table back
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(table, f, indent=2)
        print("Hash table updated (rename fix)")

    print("Verification complete")


# Main
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
