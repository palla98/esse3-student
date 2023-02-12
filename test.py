import subprocess

comando = "esse3-student"
risultato = subprocess.run(
    [comando, "booklet", "--help"],
    capture_output=True,
)

if __name__ == "__main__":
    output = risultato.stdout.decode().split('\n')
    for line in output:
        print(line)
    error = risultato.stderr.decode().split('\n')
    for line in error:
        print(line)
