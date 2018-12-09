class AuthInfo():
    def __init__(self, hostname=None, port=22, username=None, password=None, is_psw = True):
        self.hostname = hostname
        self.port = int(port)
        self.username = username
        self.password = password
        self.is_psw = is_psw
