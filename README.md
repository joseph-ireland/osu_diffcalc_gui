### osu! diffcalc gui

osu! diffcalc gui is a small tool which allows the user to map a small part of a beatmap and run a difficulty calculation on the result in real time.



### Basic Setup
#### Install
Requires python 3.4+ and a copy of osu-tools PerformanceCalculator
1. Create a new virtual environment `python -m venv .venv` and activate using `.venv\scripts\activate`
1. Install dependencies with `python -m pip install -r requirements.txt` or optionally install the module as a package by running `pip install .`
#### Run
1. Activate the venv (if not already active) using `.venv\scripts\activate`
2. run `python -m osu_diffcalc_gui -c "dotnet /path/to/PerformanceCalculator.dll"`


### Usage: 
```
python -m osu_diffcalc_gui [-h] [-c COMMAND_PREFIX] [-d DIRECTORY] [-f FILE]

optional arguments:
  -h, --help            show this help message and exit
  -c COMMAND_PREFIX, --command_prefix COMMAND_PREFIX
                        prepended to difficulty calculation command before executing
  -d DIRECTORY, --directory DIRECTORY
                        Working directory of command
  -f FILE, --file FILE  Name of output .osu file (default=test.osu)
```

### TODO
1. Make a binary package that people can just download and run.
