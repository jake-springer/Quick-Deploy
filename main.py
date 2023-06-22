#---------------------------------------------------------------------------

# Jake Springer
# Quick Deploy
# 6/13/23

app_version = "0.0.4"

#---------------------------------------------------------------------------

import os
from subprocess import call 
import sys
from json_utils import JSON
import shutil
from pathlib import Path

#---------------------------------------------------------------------------

files_dir = "files"
config_file = JSON("config.json")
data = config_file.load_json()
test_mode = data["settings"]["test_mode"]

#---------------------------------------------------------------------------

def clear(): 
    call("clear")


def quit():
    sys.exit()
    
#---------------------------------------------------------------------------
#       ---  Source Machine Functions ---

def new_file_notification(fname):
    clear()
    print("[>] New file found in the deploy directory.")
    print("[>] File name: " + fname)
    print()
    print("[>] Configure file for deploy?")

#TODO
def find_new_deploy_files(): #!WIP
    found = []
    new_files = []
    deploy_files = os.listdir(files_dir)
    registry = config_file.load_json()["registry"]
    for dfile in deploy_files:
        for rfile in registry:
            if dfile == rfile["deploy_fname"]:
                found.append(dfile)
                break
    for dfile in deploy_files:
        if dfile not in found:
            new_files.append(dfile)
    return new_files


def scan_deploy_files():
    clear()
    print("[>] Scanning " + files_dir)
    deploy_files = os.listdir(files_dir)
    if not deploy_files:
        print("[>] No files found .")
        input("[~] Press enter to continue")
    new_files = find_new_deploy_files()
    if new_files:
        print(f"[>] Found {str(len(new_files))} unregistered files.")
        print("\n[1]. Register all now")
        print("[2]. Ignore all and continue")
        while True:
            select = input("\n[?] ")
            if select == '1':
                # --- register new files ---
                data = config_file.load_json()
                for nfile in new_files: #! Register new files here
                    clear()
                    nfile_data = get_file_data(nfile)
                    data["registry"].append(nfile_data)
                config_file.save_json(data)
                break
            elif select == '2':
                break
    print("[>] Number of files: " + str(len(deploy_files)))
    print()
    for dfile in deploy_files:
        print("--> " + dfile)
    print()
    input("[~] Press enter to continue ")
        
    
def create_deploy_file():
    banner = "# Quick Deploy\n"
    clear()
    print("[>] Creating deploy file\n")
    new_file = get_file_data()
    if not new_file: 
        return
    dfile_path = os.path.join(files_dir, new_file["deploy_fname"])
    with open(dfile_path, 'w') as file:
        file.write(banner)
    data = config_file.load_json()
    data["registry"].append(new_file)
    config_file.save_json(data)
    print()
    print("[>] Created -> " + dfile_path)
    print(f"[>] {new_file['deploy_fname']} added to registry.")
    print()
    input("[>] Press enter to continue")


def get_file_data(deploy_file_name=None):
    if deploy_file_name:
        print(f"[>] File name: {deploy_file_name}\n")
    else:
        deploy_file_name = input("[?] Deploy file name: ")
    # --- File/Path data ---
    real_file_name = input("[?] Real file name: ")
    destination_path = input("[?] Destination path (user directory: \"~/\" ): ")
    file_description = input("[?] File summary: ")
    # --- File Write Mode ---
    print()
    print("[W]RITE   ->  write new file, overwrite if exists.")
    print("[A]PPEND  ->  write to the bottom of existing file, create if doesn't exist.")
    write_mode = input("\n[?] Write mode: ").lower()
    if write_mode.lower() == 'a':
        write_mode = "a+"
    print()
    # --- Save backup flag ---
    save_backup = input("[Y/N] Save backup: ").lower()
    while save_backup != 'y' and save_backup != 'n':
        save_backup = input("[Y/N] Save backup: ").lower()
    if save_backup.lower() == 'y':
        save_backup = True
    else:
        save_backup = False
    # --- Confirm Data ---
    clear()
    print("[>] File name    |>   " + deploy_file_name)
    print("[>] Destination  |>   " + os.path.join(destination_path, real_file_name))
    print("[>] Write mode   |>   " + write_mode)
    print("[>] Save backup  |>   " + str(save_backup))
    print("[>] Description  |>   " + file_description)
    print()
    conf = input("[Y/N] ").lower()
    while conf != 'y' and conf != 'n':
        conf = input("[Y/N] ").lower()
    # --- Create File Dict ---
    if conf == 'y':
        return {
            "deploy_fname":deploy_file_name,
            "registry_type":"file",
            "file_name":real_file_name,
            "destination": destination_path,
            "write_mode": write_mode,
            "save_backup": save_backup,
            "desc":file_description
        }
    return None


def add_packages():
    clear()
    packs = []
    print("[>] Adding packages")
    print("[>] Press ENTER after each package, or Q to quit.")
    while True:
        package_name = input("[?] ")
        if package_name.lower() == 'q':
            data = config_file.load_json()
            data["packages"].extend(packs)
            config_file.save_json(data)
            break 
        packs.append(package_name)
        
#---------------------------------------------------------------------------

def create_file_backups():
    data = config_file.load_json()
    backup_dir = data["settings"]["copies_directory"]
    src_paths = []
    print("[>] Gathering files...")
    # --- find files marked as save_copy
    for deploy_file in data["registry"]:
        if deploy_file["save_backup"]:
            destination = deploy_file["destination"]
            # --- get the home user's directory ---
            if destination[0] == '~':
                destination = os.path.expanduser(destination)
            src_paths.append(os.path.join(destination, deploy_file["file_name"]))    
    # --- copy the files ----
    print("[>] Starting file backup...")
    for src in src_paths:
        print(src + " ---> " + backup_dir)
        shutil.copy2(src, backup_dir)
    print("\n[>] Completed backup")


def make_dir_structure(path):
    print('creating path structure')
    Path(path).mkdir(parents=True, exist_ok=True)
    

def transfer_file(deploy_data):
    destination = deploy_data["destination"]
    if destination[0] == '~':
        destination = os.path.expanduser(destination)
    # --- check if dir is there, create it if not ---
    if not os.path.exists(destination):
        make_dir_structure(destination)
    # --- open and write to file --- 
    if test_mode:
        file_path = os.path.join("test_dir", deploy_data["file_name"])
    else:
        file_path = os.path.join(destination, deploy_data["file_name"])
    source_file = os.path.join(files_dir, deploy_data["deploy_fname"])
    with open(file_path, deploy_data["write_mode"]) as file:
        file.write("\n\n\n")
        with open(source_file, 'r') as sfile:
            for line in sfile.readlines():
                file.write(line)


def install_packages():
    data = config_file.load_json()
    if test_mode:
        print("[!] Package installation disabled in test mode.")
        return
    packages = data["packages"]
    clear()
    print("[>] Installing packages...\n")
    print("The following packages are set to be installed:")
    for p in packages:
        print("--> " + p)
    print()
    print("[>] You'll be prompted for your password.")
    print()
    input("[~] Press enter to continue ")
    for package in packages:
        call(["sudo", "apt-get", "install", package])
        
#---------------------------------------------------------------------------

def display_paths():
    clear()
    print("[>] Source files:  " + "")
    print("[>] Backup folder: " + "")
    print()
    input("[~] Press enter to continue")


def display_registry(): #! WIP
    data = config_file.load_json()
    reg = data["registry"]
    for rfile in reg:
        full_path = os.path.join(rfile["destination"], rfile["file_name"])
        print("[~] Registry name: " + rfile["deploy_fname"])
        print("[~] Type: " + rfile["registry_type"])
        print("[~] File: " + full_path)
        print("[~] Write mode: " + reg["write_mode"])
        print("[~] Save backup: " + reg["save_backup"])
        print("[~] Description: " + reg["description"])

#---------------------------------------------------------------------------

def launch():
    data = config_file.load_json()
    clear()
    print("[>] Launching quick deploy...")
    print()
    print("[>] Files: ", len(data["registry"]))
    print("[>] Folders: wip")
    print("[>] Packages: ", len(data["packages"]))
    print()
    print("[>] OS: " + data["settings"]["os"])
    print("[>] Package manager: " + data["settings"]["current_package_manager"]),
    print()
    print("[>] Deploy directory: " + data["settings"]["deploy_files_directory"])
    print("[>] Backups directory: " + data["settings"]["copies_directory"])
    print("[>] Test mode: " + str(data["settings"]["test_mode"]))
    print()
    input("[>] Press enter to start")
    install_packages()
    create_file_backups()
    print("[>] Deploying files...\n")
    for dfile in data["registry"]:
        print("--> " + os.path.join(dfile["destination"], dfile["file_name"]))
        transfer_file(dfile)
    print()
    print("[>] Completed deployment")
    input("[~] Press enter to continue  ")
    


#---------------------------------------------------------------------------


def settings_menu():
    while True:
        clear()
        print(" --->  Settings  <---\n")
        print("[1]. Create new deploy file")
        print("[2]. Scan deploy directory")
        print("[3]. Display paths")
        print("[4]. Display registry")
        print("[5]. Add package")
        print("[Q]. Return")
        print()
        select = input("[?] ")
        if select.lower() == 'q':
            return
        elif select == '1':
            create_deploy_file()
        elif select == '2':
            pass
        elif select == '5':
            add_packages()
        
        
def main():
    while True: 
        clear() 
        print(" --->  Quick Deploy  <---")
        print(f"  ->  Version: {app_version}  <-  \n")
        print("[1]. Launch")
        print("[2]. Host mode")
        print("[3]. Settings")
        print("[Q]. Exit")
        select = input("\n[?] ")
        if select.lower() == 'q':
            quit()
        elif select == '1':
            launch()
        elif select == '2':
            pass
        elif select == '3':
            settings_menu()
        
#---------------------------------------------------------------------------

main()

#---------------------------------------------------------------------------


