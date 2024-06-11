from os import path, getpid, cpu_count, remove, scandir, getcwd, mkdir, getenv, listdir
import tempfile
from rich.progress import track
from rich.console import Console
from rich.table import Table
from shutil import rmtree
import winshell
import string
import numpy as np
import msgpack
from concurrent.futures import ThreadPoolExecutor
from psutil import Process, REALTIME_PRIORITY_CLASS, disk_usage
from gc import disable as gcDisable, enable as gcEnable
import subprocess
import shlex

FILEBROWSER_PATH = path.join(getenv('WINDIR'), 'explorer.exe')

def explore(path_):
    _path_ = path.normpath(path_)
    subprocess.run([FILEBROWSER_PATH, '/select,', _path_])

gcDisable()
process = Process(getpid()).nice(REALTIME_PRIORITY_CLASS)

#-  -   -   -   -   -   -  -   -   -   -   -    -  -   -   -   -   -    -  -   -   -   -   -

def read_msgpack(file_:str):
    with open(file_, "rb") as f:
        data_ = msgpack.unpackb(f.read())
    return data_

#-  -   -   -   -   -   -  -   -   -   -   -    -  -   -   -   -   -    -  -   -   -   -   -

def preprocess_input(input_str):
    parts = shlex.split(input_str, posix=False)
    cleaned_parts = []
    for part in parts:
        if part.endswith('\\'):
            part = part[:-1]
        cleaned_parts.append(part)
    return ' '.join(cleaned_parts)

#-  -   -   -   -   -   -  -   -   -   -   -    -  -   -   -   -   -    -  -   -   -   -   -

def convert_bytes(num:bytes):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024

#-  -   -   -   -   -   -  -   -   -   -   -    -  -   -   -   -   -    -  -   -   -   -   -

def convert_to_bytes(size_str:str):
    if isinstance(size_str, int):  # Check if input is already an integer
        return size_str

    size = float(size_str.split()[0])  # Extract numerical part and convert to float
    unit = size_str.split()[1]  # Extract unit part
    units = ['bytes', 'KB', 'MB', 'GB', 'TB']
    unit_index = units.index(unit)
    bytes_size = size
    for i in range(unit_index):
        bytes_size *= 1024
    return bytes_size


#-  -   -   -   -   -   -  -   -   -   -   -    -  -   -   -   -   -    -  -   -   -   -   -

def get_folder_size_bytes(folder_path:str) -> int:
    directory_size:int = 0
    for files_folders in scandir(folder_path):
        try:
            if files_folders.is_file():
                directory_size += files_folders.stat().st_size
            else:
                directory_size += get_folder_size_bytes(files_folders.path)
        except:
            continue

    return directory_size

#-  -   -   -   -   -   -  -   -   -   -   -    -  -   -   -   -   -    -  -   -   -   -   -

def clean_temp_files():
    temp_dir = tempfile.gettempdir()
    windows_temp_dir = "C:\\Windows\\Temp"
    temp_files = scandir(temp_dir)
    windows_temp_files = scandir(windows_temp_dir)
    console = Console(style="bold")
    try:
        data_removed:int = 0
        for file_f in track(temp_files, description="\n[yellow]#[/yellow]> [bold violet]Cleaning Temp Folder[/bold violet]"):
            try:
                if not path.exists(file_f.path): continue
                
                if file_f.is_dir():
                    data_removed += int(get_folder_size_bytes(file_f.path))
                    rmtree(file_f.path, ignore_errors=True)
                else: 
                    file_size:int = int(file_f.stat().st_size)
                    remove(file_f.path)
                    data_removed += file_size
            except:
                continue

        for file_f in track(windows_temp_files, description="\n[yellow]#[/yellow]> [bold violet]Cleaning Windows Temp Folder[/bold violet]"):
            try:
                if not path.exists(file_f.path): continue
                
                if file_f.is_dir():
                    data_removed += int(get_folder_size_bytes(file_f.path))
                    rmtree(file_f.path, ignore_errors=True)
                else: 
                    file_size:int = int(file_f.stat().st_size)
                    remove(file_f.path)
                    data_removed += file_size
            except:
                continue
        
        console.print(f"\n[yellow]#[/yellow]> [purple4]Removed[/purple4] [deep_pink4][{convert_bytes(data_removed)}][/deep_pink4]")
        clear_recyclebin = str(console.input(f"[yellow]#[/yellow]> [bold cyan]Recycle Bin[/bold cyan] [deep_pink4][{len(list(winshell.recycle_bin()))}][/deep_pink4] [bold cyan]Items Found[/bold cyan] | [red]Roughly [{convert_bytes(get_folder_size_bytes("C:\\$RECYCLE.BIN"))}] Found[/red]\n[yellow]#[/yellow]> [white]Clear[/white] [bold cyan]Recycle Bin?[/bold cyan][bold white](Y/N)[/bold white]\n[yellow]$[/yellow]> "))
        if clear_recyclebin.lower() == "y":
            winshell.recycle_bin().empty(confirm=False, sound=True, show_progress=False)
        else:
            console.print("[yellow]#[/yellow]> [bold red]Aborted[/bold red]")
    except: 
        pass

#-  -   -   -   -   -   -  -   -   -   -   -    -  -   -   -   -   -    -  -   -   -   -   -

def availible_drives():
    data_path = getcwd()+"\\Drives"
    if not path.exists(data_path): mkdir(data_path)
    drivers_ = string.ascii_uppercase
    valid_drivers = []
    for drive in drivers_:
        if path.exists(drive+":\\"):
            valid_drivers.append(f"{drive}")
    return valid_drivers

#-  -   -   -   -   -   -  -   -   -   -   -    -  -   -   -   -   -    -  -   -   -   -   -

def save_msgpack(data:str, filename:str, drive_:str, folder_name:str):
    try:
        data = sorted(data[drive_], key=lambda item: item['size'], reverse=True)
        serialized_data = msgpack.packb(data)

        with open(getcwd()+f"\\{folder_name}\\{filename}", "wb") as f:
            f.write(serialized_data)
    except:
        Console().print_exception(show_locals=True)

#-  -   -   -   -   -   -  -   -   -   -   -    -  -   -   -   -   -    -  -   -   -   -   -

def convert_bytes(num:bytes):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024

#-  -   -   -   -   -   -  -   -   -   -   -    -  -   -   -   -   -    -  -   -   -   -   -

def scan_dir(path_argument:str):
    
    gcDisable()

    func_console = Console()

    try:
        data_path = getcwd()+"\\Drives"
        if not path.exists(data_path): mkdir(data_path)
    except:
        func_console.print_exception(show_locals=True)

    if not path.exists(data_path):
        func_console.print(f"[bold red]Error[/bold red]: [red]Unable to find [bold green]{data_path}[/bold green][/red]")

    json_data_path_size = {}
    driver:np.bytes_[bytes] = ""

    bytes_used_files:np.int32[int] = 0

    folders_found:np.int32[int] = 0
    files_found:np.int32[int] = 0

#-  -   -   -   -   -   -  -   -   -   -   -    -  -   -   -   -   -    -  -   -   -   -   -

    def read_root_dir_threadpool(path_):
        nonlocal driver, bytes_used_files, json_data_path_size, files_found, folders_found
        try:
            folders_found += 1
            with ThreadPoolExecutor(max_workers=cpu_count()) as executor:  # Adjust max_workers as needed

                root_:list = list(scandir(path_))
                for child in root_:
                    if child.is_dir():
                        executor.submit(read_root_dir_threadpool, child.path)
                    else:
                        file_size = child.stat().st_size
                        json_data_path_size[driver].append({"path": child.path.encode('ascii', 'replace').decode(), "size": file_size})
                        #deque_data[driver].append({"path": child.path.encode('ascii', 'replace').decode(), "size": file_size})
                        files_found += 1
                        bytes_used_files += file_size
            
        except:
            pass
    
#-  -   -   -   -   -   -  -   -   -   -   -    -  -   -   -   -   -    -  -   -   -   -   -

    def load_driver_(driver_):
        nonlocal json_data_path_size, folders_found, files_found, bytes_used_files


        json_data_path_size = {driver_: []}

        read_root_dir_threadpool(driver_)

        func_console.print(f"\n[yellow]#[/yellow]> [[green]'{driver_}'[/green]] PATH | Used: [{convert_bytes(bytes_used_files)}]\n[{folders_found}] Folders | [{files_found}] Files | CPU Count: [{cpu_count()}]]")

        if path_argument == "" or path_argument == "." or (path_argument.split(":")[0] in availible_drives() and path_argument.split(":")[1] == "/"):
            save_msgpack(json_data_path_size, f"{driver_.split(":")[0]}.msgpack", driver_, "Drives")

        bytes_used_files = 0
        folders_found = 0
        files_found = 0

#-  -   -   -   -   -   -  -   -   -   -   -    -  -   -   -   -   -    -  -   -   -   -   -

    if path_argument == "" or path_argument == ".":
        func_console.print(f"\n[yellow]#[/yellow]> [bold red]Scanning All Drives, Please Be Patient.[/bold red]")
        import time
        t1 = time.perf_counter()
        for _driver_ in availible_drives()[::-1]:
            _driver_ = f"{_driver_}:/"
            driver = _driver_
            load_driver_(driver)
        func_console.print(f"\n[yellow]#[/yellow]> {availible_drives()} | Total Time: [{(time.perf_counter()-t1):.3f}s]")
    elif path_argument.split(":")[0] in availible_drives() and path_argument.split(":")[1] == "/":
        import time
        t1 = time.perf_counter()
        driver = path_argument
        load_driver_(path_argument)
        func_console.print(f"\n[yellow]#[/yellow]> {path_argument} | Total Time: [{(time.perf_counter()-t1):.3f}s]")
    else:
        import time
        t1 = time.perf_counter()
        driver = path_argument
        load_driver_(path_argument)
        func_console.print(f"\n[yellow]#[/yellow]> {path_argument} | Total Time: [{(time.perf_counter()-t1):.3f}s]")

        save_data_ = func_console.input("[bold yellow]Save Data? [bold white](Y/N)[/bold white]: [/bold yellow]")
        if save_data_.strip().lower() == "y":
            file_name = func_console.input("[bold green]Enter File Name: [/bold green]")
            data_path = getcwd()+"\\CustomPaths"
            if not path.exists(data_path): mkdir(data_path)
            save_msgpack(json_data_path_size, f"{file_name}.msgpack", path_argument, "CustomPaths")

    gcEnable()

#-  -   -   -   -   -   -  -   -   -   -   -    -  -   -   -   -   -    -  -   -   -   -   -

def scan_all_msgfiles():
    _console_ = Console()
    availible_msg_files = []
    try:
        for file_ in scandir(getcwd()+"\\Drives"):
            availible_msg_files.append(file_)
    except:
        _console_.print(f"[yellow]#[/yellow]> [red]No Data Found For Drives[Ensure Drives Folder Exists with Drive Data/s]. OR Developer Error?[/red]")        
    
    try:
        for file_ in scandir(getcwd()+"\\CustomPaths"):
            availible_msg_files.append(file_)
    except:
        _console_.print(f"[yellow]#[/yellow]> [red]No Data Found In CustomPaths Saved[Ensure CustomPaths Folder Exists with Data Files From Past Scanned and Saved Data]. OR Developer Error?[/red]")            
    return availible_msg_files

#-  -   -   -   -   -   -  -   -   -   -   -    -  -   -   -   -   -    -  -   -   -   -   -

def table_data(argument = "--max-line 150"):

    availible_msg_files = scan_all_msgfiles()

    command = argument.split(" ")[0]

    console = Console(style="bold")

    arg_arg = ""
    if command == "--max-line":
        arg_arg = argument.split(" ")[1]
    else:
        arg_arg = argument.split(" ")[1]+" "+argument.split(" ")[2]
        try:
            convert_to_bytes(arg_arg)
        except ValueError:
            return console.print(f"[bold yellow]$[/bold yellow]> [red]Invalid Value. [num] [unit][/red]")

    for i, file_ in enumerate(availible_msg_files):
        console.print(f"{i}: {file_.name}")

    while True:
        file_chosen = console.input("\n[bold yellow]$[/bold yellow]> ", markup=True)
        if file_chosen.isnumeric():
            if int(file_chosen) < len(availible_msg_files) and int(file_chosen) > -1:
                break
            else:
                console.print(f"[bold yellow]$[/bold yellow]> [red]Invalid Number[/red]")
                continue
        else:
            if file_chosen.strip().lower() == "exit":
                return
            else:
                console.print(f"[bold yellow]$[/bold yellow]> [red]Invalid Input[/red]")
                continue

    path = availible_msg_files[int(file_chosen)].path
    data = read_msgpack(path)

    max_size_ = 100
    size_threshold = "100 MB"

    if command == "--max-line":
        max_size_ = int(arg_arg)
    elif command == "--max-size":
        size_threshold = str(arg_arg)

    try:
        table = Table(title = f"{path}", title_justify="center", title_style="white")

        table.add_column(".", style="white", justify="center", max_width=4)
        table.add_column("Path", style="white", justify="left")
        table.add_column("Size", style="yellow", justify="left")
        table.add_column("Table Size", style="red", justify="left")


        table_size:bytes = 0
        lines_:int = 0
        for i, entry in enumerate(data):
            if command == "--max-line":
                if i == max_size_: break
            elif command == "--max-size":
                if convert_to_bytes(entry['size']) < convert_to_bytes(size_threshold): break
            table_size += entry['size']
            table.add_row(str(i+1), entry['path'], convert_bytes(entry['size']))
            lines_ += 1

        table.add_row(".", "", "", str(convert_bytes(table_size)))

        console.print(table)

    except Exception:
        console.print_exception()

#-  -   -   -   -   -   -  -   -   -   -   -    -  -   -   -   -   -    -  -   -   -   -   -
