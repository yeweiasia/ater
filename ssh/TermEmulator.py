import socket
import paramiko
import base64
from binascii import hexlify
import getpass
import os
import select
import socket
import sys
import traceback
from paramiko.py3compat import u
import wx


class TermEmulator():
    def __init__(self, output_call, auth_info):
        self.system = self.sysDetect()
        self.auth_info = auth_info
        self.trans = None
        self.chan = None
        self.output_call = output_call
        self.init_shell(auth_info)

    def sysDetect(self):
        system = "posix"
        try:
            import termios
            import tty
        except ImportError:
            system = "windows"
        return system

    def sendToTerminalUI(self, data):
        wx.CallAfter(self.output_call, data)

    def sendChar(self, char):
        try:
            self.chan.send(char)
        except EOFError:
            # user hit ^Z or F6
            pass

    def agent_auth(self, transport, username):
        """
        Attempt to authenticate to the given transport using any of the private
        keys available from an SSH agent.
        """

        agent = paramiko.Agent()
        agent_keys = agent.get_keys()
        if len(agent_keys) == 0:
            return

        for key in agent_keys:
            print("Trying ssh-agent key %s" % hexlify(key.get_fingerprint()))
            try:
                transport.auth_publickey(username, key)
                print("... success!")
                return
            except paramiko.SSHException:
                print("... nope.")

    def manual_auth(self, username, hostname):
        default_auth = "p"
        auth = raw_input(
            "Auth by (p)assword, (r)sa key, or (d)ss key? [%s] " % default_auth
        )
        if len(auth) == 0:
            auth = default_auth

        if auth == "r":
            default_path = os.path.join(os.environ["HOME"], ".ssh", "id_rsa")
            path = raw_input("RSA key [%s]: " % default_path)
            if len(path) == 0:
                path = default_path
            try:
                key = paramiko.RSAKey.from_private_key_file(path)
            except paramiko.PasswordRequiredException:
                password = getpass.getpass("RSA key password: ")
                key = paramiko.RSAKey.from_private_key_file(path, password)
            self.trans.auth_publickey(username, key)
        elif auth == "d":
            default_path = os.path.join(os.environ["HOME"], ".ssh", "id_dsa")
            path = raw_input("DSS key [%s]: " % default_path)
            if len(path) == 0:
                path = default_path
            try:
                key = paramiko.DSSKey.from_private_key_file(path)
            except paramiko.PasswordRequiredException:
                password = getpass.getpass("DSS key password: ")
                key = paramiko.DSSKey.from_private_key_file(path, password)
            self.trans.auth_publickey(username, key)
        else:
            pw = getpass.getpass("Password for %s@%s: " % (username, hostname))
            self.trans.auth_password(username, pw)

    def login_auth(self):
        if self.auth_info.is_psw:
            self.trans.auth_password(self.auth_info.username, self.auth_info.password)

    def posix_shell(self, chan):
        try:
            import termios
            import tty
        except ImportError:
            pass

        oldtty = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            tty.setcbreak(sys.stdin.fileno())
            chan.settimeout(0.0)

            while True:
                r, w, e = select.select([chan, sys.stdin], [], [])
                if chan in r:
                    try:
                        x = u(chan.recv(1024))
                        if len(x) == 0:
                            sys.stdout.write("\r\n*** EOF\r\n")
                            break
                        sys.stdout.write(x)
                        sys.stdout.flush()
                    except socket.timeout:
                        pass
                if sys.stdin in r:
                    x = sys.stdin.read(1)
                    if len(x) == 0:
                        break
                    chan.send(x)

        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)

    # thanks to Mike Looijmans for this code
    def windows_shell(self, chan):
        import threading

        def writeall(sock, output):
            while True:
                data = sock.recv(256)
                if not data:
                    output("\r\n*** EOF ***\r\n\r\n")
                    break
                output(data)

        writer = threading.Thread(target=writeall, args=(chan, self.sendToTerminalUI))
        writer.start()

    def init_shell(self, auth_info):
        paramiko.util.log_to_file("demo.log")
        if auth_info.hostname.find("@") >= 0:
            auth_info.username, auth_info.hostname = auth_info.hostname.split("@")
        if len(auth_info.hostname) == 0:
            self.output_call("*** Hostname required.")
            sys.exit(1)
        if auth_info.hostname.find(":") >= 0:
            auth_info.hostname, auth_info.port = auth_info.hostname.split(":")
            auth_info.port = int(auth_info.port)

        # now connect
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((auth_info.hostname, auth_info.port))
        except Exception as e:
            self.output_call("*** Connect failed: " + str(e))
            traceback.print_exc()
            sys.exit(1)

        try:
            self.trans = paramiko.Transport(sock)
            try:
                self.trans.start_client()
            except paramiko.SSHException:
                self.output_call("*** SSH negotiation failed.")
                sys.exit(1)

            try:
                keys = paramiko.util.load_host_keys(
                    os.path.expanduser("~/.ssh/known_hosts")
                )
            except IOError:
                try:
                    keys = paramiko.util.load_host_keys(
                        os.path.expanduser("~/ssh/known_hosts")
                    )
                except IOError:
                    self.output_call("*** Unable to open host keys file")
                    keys = {}

            # check server's host key -- this is important.
            key = self.trans.get_remote_server_key()
            if auth_info.hostname not in keys:
                self.output_call("*** WARNING: Unknown host key!")
            elif key.get_name() not in keys[auth_info.hostname]:
                self.output_call("*** WARNING: Unknown host key!")
            elif keys[auth_info.hostname][key.get_name()] != key:
                self.output_call("*** WARNING: Host key has changed!!!")
                sys.exit(1)
            else:
                self.output_call("*** Host key OK.")

            # get username
            if auth_info.username == "":
                default_username = getpass.getuser()
                self.output_call("Username [%s]: " % default_username)
                if len(auth_info.username) == 0:
                    auth_info.username = default_username

            self.agent_auth(self.trans, auth_info.username)
            if not self.trans.is_authenticated():
                # self.manual_auth(auth_info.username, auth_info.hostname)
                self.login_auth()
            if not self.trans.is_authenticated():
                print("*** Authentication failed. :(")
                self.trans.close()
                sys.exit(1)

            self.chan = self.trans.open_session()
            self.chan.get_pty()
            self.chan.invoke_shell()

            if self.system == "posix":
                self.posix_shell(self.chan)
            elif self.system == "windows":
                self.windows_shell(self.chan)

        except Exception as e:
            print("*** Caught exception: " + str(e.__class__) + ": " + str(e))
            traceback.print_exc()
            try:
                self.trans.close()
            except:
                pass
            sys.exit(1)

    def close(self):
        self.chan.close()
        self.trans.close()
