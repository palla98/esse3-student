
def take_credentials(value: str):
    with open(r"/home/antonio/Scrivania/cred.txt", 'r') as fp:
        for index, line in enumerate(fp):
            if index == 0 and value == "username":
                return line.strip()
            if index == 1 and value == "password":
                return line.strip()

