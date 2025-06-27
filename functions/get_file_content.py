import os

def get_file_content(working_directory, file_path):
    try:
        abs_working_dir = os.path.abspath(working_directory)
        target_file = os.path.abspath(os.path.join(working_directory, file_path))
        if not target_file.startswith(abs_working_dir):
            return f'Error: Cannot access "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(target_file):
            return f'Error: "{file_path}" is not a file'
        with open(target_file, 'r') as file:
            content = file.read()
            if len(content) > 10000:
                content = content[:10000] + f'\n[...File "{file_path}" truncated at 10000 characters]'
            return content
    except Exception as e:
        return f"Error: {e}"