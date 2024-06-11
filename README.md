# CLI Tool for Drive Scanning and Cleanup

## Overview

This project provides a command-line interface (CLI) tool to perform various operations on your drives, such as scanning directories, viewing scanned data, and cleaning temporary files. The tool is implemented in Python and leverages the `rich` library for a better user interface.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/your-username/your-repo.git
    cd your-repo
    ```
2. Install the required packages:
    ```sh
    pip install rich pyuac msgpack
    ```

## Usage | Users
1. Install Scanner.exe from https://github.com/your-username/your-repo/releases.
2. Run Scanner.exe.
3. Read Instructions on The Availible Commands Bellow

## Usage | Developers

Run the CLI tool:
```sh
python cli.py
```

### Available Commands

1. **Scan Drives**: 
    - Command: `1 "Path"`
    - Example: `1 "C:/"`
    - Description: Scans the specified path or all available drives if `"."` is given as the path.

2. **View Scanned Data**:
    - Command: `2 Drive/CustomPath [--max-line LINE LIMIT] [--size-threshold SIZE LIMIT]`
    - Example: `2 C --max-line 100` or `2 C --size-threshold 100MB`
    - Description: Views data from the specified drive or path with optional limits on line count or file size.

3. **Clean Temp Files**:
    - Command: `3`
    - Description: Cleans temporary files from the system.

4. **Exit**:
    - Command: `4`
    - Description: Exits the CLI tool.

## Examples

- **Scan all available drives**:
    ```sh
    $ 1 "."
    ```
- **View data from drive C with a max of 100 lines**:
    ```sh
    $ 2 C --max-line 100
    ```
- **Clean temporary files**:
    ```sh
    $ 3
    ```

## Features

- **Scan Drives**: Scan a specified path or all available drives for data.
- **View Scan Data**: View data from scanned drives with options to limit by line count or file size.
- **Clean Temp Files**: Clean temporary files from the system.

## Requirements For Developers

- Python 3.6+
- `rich` library
- `pyuac` library
- `msgpack` library

