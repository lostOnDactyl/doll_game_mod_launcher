import os

def find_dwrg_exe():
    possible_dirs = [
        "C:\\Program Files\\IdentityV\\",
        "C:\\Program Files\\IdentityV2\\",
        os.path.expanduser("~\\Program Files\\IdentityV2\\"),
    ]
    for directory in possible_dirs:
        file_path = os.path.join(directory, "dwrg.exe")
        if os.path.exists(file_path):
            return file_path
    return None
