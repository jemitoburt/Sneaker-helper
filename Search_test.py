import os

current_directory = os.getcwd()
folder_name = os.path.basename(current_directory)
print(f"Current folder name: {folder_name}")