import rich
from rich.console import Console
from function import clean_temp_files, availible_drives, scan_dir, table_data, preprocess_input
from os import path
import shlex
import pyuac

_LOGO_ ="""
 ██████╗██╗   ██╗██████╗ ███████╗██████╗             ██████╗██╗     ██╗
██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗           ██╔════╝██║     ██║
██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝           ██║     ██║     ██║
██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗           ██║     ██║     ██║
╚██████╗   ██║   ██████╔╝███████╗██║  ██║    ██╗    ╚██████╗███████╗██║
 ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝    ╚═╝     ╚═════╝╚══════╝╚═╝
"""

console = Console()

_01_INFO = '1: Scan Drives | arg = Path[Argument Can Also be Drives Themselvs eg. "C:/"][yellow](if "." is given as an argument it will scan all availible drives.)[/yellow] | example usage: 1 "C:/..."'
_02_INFO = f'2: View Scanned Data | arg = Drive/CustomPathScanned{availible_drives()} ||| OPTIONAL(USE ONLY ONE) -> args[--max-line [LINE LIMIT], --size-threshold [100 KB, 1 MB, 10 GB, 1 TB] | Example Usage: 2 [green]C[/green] --max-line 100 OR --size-threshold 100 MB'

commands = {
    "0": "Gives you Detailed Information About a Command | example usage: 0 1",
    "1": 'Scan Drives | arg = Path or Drive| example usage: 1 "C:/..." | More Information In 0',
    "2": f'View Scan Data | arg = {availible_drives()}/CustomPath | Example Usage: 2 [green]C[/green] --max-line 100 OR --size-threshold 100MB',
    "3": "Clean Temp Files",
    "4": "Exit"
}

while True:
    console.clear()
    if not pyuac.isUserAdmin():
        console.print("[bold red]Without Administrative Privileges, The Program Might bypass certain files during scanning or deletion processes due to insufficient permissions granted by Windows.[/bold red]\n")
    console.print(_LOGO_)

    for key, value in commands.items():
        console.print(f"{key}: {value}")

    command_written = console.input("\n[bold yellow]$[/bold yellow]> ", markup=True)
    if command_written.strip() == "":
        continue

    if len(command_written.split(' ')) > 0 and command_written.split(' ') != int:
        parsed_command = shlex.split(preprocess_input(command_written), posix=False)

    command = int(parsed_command[0])
    argument = ""

    try: 
        if command_written.split(' ')[1] != int:
            argument = ' '.join(parsed_command[1:])
            if argument.endswith('\\'):
                argument = argument[:-1]

            argument = argument.replace('"', '')
    except: 
        pass

    if command == 0:
        if int(argument) == 1:
            console.print(_01_INFO)
        elif int(argument) == 2:
            console.print(_02_INFO)
        else:
            console.print(f"[yellow]#[/yellow]> [red]{argument} Doesn't Have Detailed Information Or Argument is Invalid.[/red]")

    elif command == 1:
        if argument == "." or argument == "":
            scan_dir(argument)
        elif not path.exists(argument):
            console.print("[yellow]#[/yellow]> [red]Path Not Found![/red]")

    elif command == 2:
        table_data(argument)
        pass

    elif command == 3:
        clean_temp_files()
        
    elif command == 4:
        console.clear()
        raise SystemExit()
    else:
        continue
    
    console.input("\n[bright_white][Enter][/bright_white] [bold orange3]To Continue[/bold orange3]")