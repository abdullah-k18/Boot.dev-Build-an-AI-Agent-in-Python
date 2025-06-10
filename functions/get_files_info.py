import os

def get_files_info(working_directory, directory=None):
    try:
        # If no directory is provided, use the working_directory
        target_directory = os.path.abspath(os.path.join(working_directory, directory or "."))

        # Restrict access to outside of working_directory
        abs_working_directory = os.path.abspath(working_directory)
        if not target_directory.startswith(abs_working_directory):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        # Check if it's a directory
        if not os.path.isdir(target_directory):
            return f'Error: "{directory}" is not a directory'

        items = []
        for item in os.listdir(target_directory):
            item_path = os.path.join(target_directory, item)
            is_dir = os.path.isdir(item_path)
            size = os.path.getsize(item_path)
            items.append(f"- {item}: file_size={size} bytes, is_dir={is_dir}")

        return "\n".join(items)

    except Exception as e:
        return f"Error: {str(e)}"
