# Print Queue Manager

The print queue manager is a part of the enhancement project to compliment existing systems implemented in-house

## Platform

Windows 10, 11

## Installation

### Using A Binary

Simple, [download](https://drive.google.com/drive/folders/1RbxVsU7_ZX3GrUc1PV7qdY9JAz0DaPBt?usp=sharing) the binaries, unzip the .zip file and run it

Note that the binaries are only available for Windows running on the AMD64 (x86-64) architecture

### Compile from source code

You may also compile the code from your machine. If your CPU is different and not using the x86 architecture, please use this option

Ensure that Python 3.11.x or later is installed and run the following commands in the directory where the source code is located:
    
1. `py -m venv venv`

2. `venv/Scripts/activate.bat`

3. `pip install -r requirements.txt`

4. `compile.bat`

## Usage

The print queue manager works based on these assumptions:

1. If the **file can be seen** and the **app** used to open the file is **closed**, the file has **not been printed**

2. If the **file cannot be seen** and the **app** used to open the file is **open**, the file is currently **printing**

3. If the **file cannot be seen** and the **app** used to open the file is **closed**, the file has been **successfully printed**

## Contributing

Contributions to the print queue manager are welcome through pull requests. Please open an issue if you would like to make a major change

## License

The print queue manager uses the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0.txt)