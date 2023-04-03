# esse3-student

Esse3 command line utility for student!

**esse3-student** is an API developed to provide an alternative to the web version of the Esse3 university system. This system offers a wide range of services that students often use during exam sessions, but using them is often inconvenient due to the repetitiveness of the process and the large number of clicks required by the user.
**esse3-student** automates the most commonly used tasks in order to simplify their use. Through this automation, the user can benefit from greater convenience and speed in performing these operations

## Install

As a preliminary requirement, you need to install some utility:
1) **ChromeDriver**. Download and install the most appropriate version from the following link:

https://sites.google.com/chromium.org/driver/downloads?authuser=0

2) **xdotool**. Installs the package via prompt with the command: 'sudo apt-get install xdotool'

After that, you can proceed either via PyPI, or by cloning the repository and install dependencies.
If you opt for PyPI, run the following command:
```bash
$ pip install esse3-student
```

After that, **esse3-student** can be run with
```bash
$ python3 -m esse3_student
Usage: python -m esse3_student [OPTIONS] COMMAND [ARGS]...
Try 'python -m esse3_student --help' for help.
╭─ Error ──────────────────────────────────────────────────────────────────────────────────────╮
│ Missing command.                                                                             │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯
```

If you instead opt for the repository, you also need the [Poetry](https://python-poetry.org/) Python package manager.
On Debian-like OSes it can be installed with the following command:
```bash
$ sudo apt install python3-poetry
```
After that, run the following commands:
```bash
$ git clone git@github.com/palla98/esse3-student.git
```

after downloading:
```bash
$ cd esse3-student

$ poetry install
```

After that, **esse3-student** can be run with
```bash
$ poetry run ./cli_student.py
Usage: python -m esse3-student [OPTIONS] COMMAND [ARGS]...
Try 'python -m esse3-student --help' for help.
╭─ Error ──────────────────────────────────────────────────────────────────────────────────────╮
│ Missing command.                                                                             │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Configuration

You may want to add a few environment variables to save more of your time.
If you use Bash, modify and add the following lines to your `.bashrc`:

```bash
export CLI_STUDENT_USERNAME='YOUR-USERNAME'
export CLI_STUDENT_PASSWORD='YOUR-PASSWORD'
```

Take into account that you are storing your credentials in a configuration file on your home directory.
If you are not sure that you are the only one who can read this file, DO NOT store your password in it.
You can omit one or more lines above, and they will be asked via a prompt if needed.


