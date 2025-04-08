import os
import shutil
import subprocess

UI_FILE_ROOT_DIRECTORY = "ui"
GENERATED_OUTPUT_DIRECTORY = "ui_generated"  # Relative path from this script

def clear_ui_generated_directory(output_directory: str):
    if os.path.exists(output_directory):
        # Demolish everything within the current output directory
        shutil.rmtree(output_directory)

    # Make directory for output of UI compiler
    os.makedirs(output_directory)


def find_and_generate_ui(input_directory: str, output_directory: str):
    """
    Walks through the "input_directory" (and all subdirectories) and finds all .ui files
    pyside6-uic compiler generates the .py file for each .ui file found
    Outputs to the "output_directory" location
    """
    if not os.path.exists(input_directory):
        print(f"Error: Directory holding .ui files does not exist. Directory checked: {input_directory}. Exiting now.")
        exit(1)

    errors = []
    for dirpath, _, filenames in os.walk(input_directory):  # Walk through all subdirectories
        for filename in filenames:
            if filename.endswith(".ui"):
                ui_path = os.path.join(dirpath, filename)
                output_path = os.path.join(output_directory, filename)
                py_path = os.path.splitext(output_path)[0] + ".py"  # Replace .ui with .py

                print(f"Compiling: {ui_path} → {py_path}")

                # Run pyside6-uic command
                try:
                    subprocess.run(["pyside6-uic", ui_path, "-o", py_path], check=True)
                    print(f"Successfully compiled: {py_path}")
                except subprocess.CalledProcessError as e:
                    err_str = f"Error compiling {ui_path}: {e}"
                    print(err_str)
                    errors.append(err_str)

    if not errors:
        # No errors, return
        print("\nCompilation Successful")
        return

    # Print errors that occurred during compilation
    print("\nErrors occurred during compilation:")
    for error_str in errors:
        print(error_str)

if __name__ == "__main__":
    cwd = os.getcwd()

    ui_directory = os.path.join(cwd, UI_FILE_ROOT_DIRECTORY)
    output_directory = os.path.join(cwd, GENERATED_OUTPUT_DIRECTORY)

    clear_ui_generated_directory(output_directory)

    try:
        find_and_generate_ui(ui_directory, output_directory)
    except Exception as e:
        print(f"Error: Exception occurred when trying to generate output files: {e}")
