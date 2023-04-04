# esse3-student

Esse3 command line utility for student!

**esse3-student** is an API developed to provide an alternative to the web version of the Esse3 university system. 
This system offers a wide range of services that students often use during exam sessions, but using them is often 
inconvenient due to the repetitiveness of the process and the large number of clicks required by the user.

**esse3-student** automates the most commonly used tasks in order to simplify their use. Through this automation, 
the user can benefit from greater convenience and speed in performing these operations.

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
$ git clone https://github.com/palla98/esse3-student.git
```

after downloading:
```bash
$ cd esse3-student

$ poetry install
```

After that, **esse3-student** can be run with
```bash
$ poetry run ./esse3_student_cli.py 
Usage: esse3_student_cli.py [OPTIONS] COMMAND [ARGS]...
Try 'esse3_student_cli.py --help' for help.
╭─ Error ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Missing command.                                                                                                                            │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
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

## Usage

The CLI can be run in several ways.
The simplest is likely via `poetry run ./esse3_student_cli.py`.

Have a look at the help by adding the flag `--help`:

```bash
$ poetry run ./esse3_student_cli.py --help

 Usage: esse3_student_cli.py [OPTIONS] COMMAND [ARGS]...                                                        
                                                                                                          
 Esse3 command line utility 💻                                                                            
                                                                                                          
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --username        TEXT  [env var: CLI_STUDENT_USERNAME] [default: None] [required]                  │
│ *  --password        TEXT  [env var: CLI_STUDENT_PASSWORD] [default: None] [required]                  │
│    --debug                 To show browser operations                                                  │
│    --help                  Show this message and exit.                                                 │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────────────────────────────────╮
│ add                 Operation that allows the booking of examinations 📘                               │
│ booklet             shows all the student's activities 📑                                              │
│ exams               Show available exams list 📑                                                       │
│ remove              Operation that allows the deletion of booked examinations 🗑                        │
│ reservations        Show exams booked list 📑                                                          │
│ taxes               Show all taxes 📑                                                                  │
│ tui                 Run text-user-interface                                                            │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

Run one of the provided commands by adding it to the command-line:

```bash
$ poetry run ./esse3_student_cli exams
─────────────────────────────────────────────────────────────── EXAMS SHOWCASE ────────────────────────────────────────────────────────────────
                                                                                                                                               
               #               Name                  Date            Signing up                       Description                              
              ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────               
               1          BUSINESS GAME           08/02/2023   18/01/2023 - 06/02/2023                MDCS 6 ECTS                              
                                                                                                                                               
               2          DATA ANALYTICS          06/02/2023   23/12/2022 - 04/02/2023              Secondo appello                            
                                                                                                                                               
               3         NETWORK SECURITY         07/02/2023   05/01/2023 - 06/02/2023      Oral exam and project discussion                   
                                                                                                                                               
               4   THEORETICAL COMPUTER SCIENCE   28/01/2023   13/01/2023 - 27/01/2023   Prova orale con alcune domande scritte                
                                                                                                                                               
───────────────────────────────────────────────────────────────── STATISTICS ──────────────────────────────────────────────────────────────────
                                                                                                                                               
                                                                clicks saved: 7                                                                

```

Read the dedicated help of a command of interest by adding the flag `--help` after the command:

```bash
$ poetry run ./esse3_student-cli booklet --help
                                                                                                                                               
 Usage: esse3_student_cli.py booklet [OPTIONS]                                                                                                 
                                                                                                                                               
 shows all the student's activities 📑                                                                                                         
                                                                                                                                               
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --academic-year          INTEGER            Academic year (1 to 3) [default: (dynamic)]                                                     │
│ --exam-status            TEXT               'Superata' like 'Passed' or 'Frequenza attribuita d'ufficio' like 'To do' [default: (dynamic)]  │
│ --exam-grade             INTEGER            Grade of the exam [default: (dynamic)]                                                          │
│ --new-average            <INTEGER TEXT>...  calculate new average with grade: (grade cfu); ex: '25 12'  [default: None, None]               │
│ --statistics     -s                         show statistics on the average                                                                  │
│ --help                                      Show this message and exit.                                                                     │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```


Add options and arguments to obtain what you want, with no (or minimal) further interaction:

```bash
$ poetry run ./esse3_student-cli booklet --exam-grade 27 --academic-year 1
────────────────────────────────────────────────────────────── BOOKLET SHOWCASE ───────────────────────────────────────────────────────────────
                                                                                                                                               
                                   #   Name               Academic Year   CFU   Status   Grade      Date                                       
                                  ──────────────────────────────────────────────────────────────────────────                                   
                                   4   DATA ANALYTICS           1         12    Passed    27     26/07/2021                                    
                                   5   NETWORK SECURITY         1          6    Passed    27     19/01/2021                                    
                                                                                                                                               
───────────────────────────────────────────────────────────────── STATISTICS ──────────────────────────────────────────────────────────────────
                                                                                                                                               
                                                                clicks saved: 7                                                                
```