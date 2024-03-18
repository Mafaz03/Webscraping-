import os 

def delete_files_until_limit(directory, limit):
    size_limit = limit * 1024 * 1024  # 20MB

    def get_file_info(directory):
        file_info = []
        for root, dirs, files in os.walk(directory):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                file_size = os.path.getsize(file_path)
                file_info.append((file_path, file_size))
        file_info.sort(key=lambda x: x[1])
        return file_info

    total_size = sum(file[1] for file in get_file_info(directory))
    files_deleted = 0

    while total_size > size_limit:
        file_info = get_file_info(directory)
        if not file_info:
            print("No more files to delete.")
            break

        file_path, file_size = file_info.pop(0)
        try:
            os.remove(file_path)
            total_size -= file_size
            files_deleted += 1
            print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

    print(f"Total files deleted: {files_deleted}")