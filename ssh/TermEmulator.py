import socket
import sys
import paramiko
import base64
from binascii import hexlify
import getpass
import os
import select
import socket
import sys
import time
import traceback
from paramiko.py3compat import u


class TermEmulator():
    def __init__(self, output_call):
        self.system = self.sysDetect()
        self.trans = None
        self.chan = None
        self.output_call = output_call
        self.init_shell()

    def sysDetect(self):
        system = "posix"
        try:
            import termios
            import tty
        except ImportError:
            system = "windows"
        return system

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

        self.output_call(
            "Line-buffered terminal emulation. Press F6 or ^Z to send EOF.\r\n\r\n"
        )

        def writeall(sock):
            while True:
                data = sock.recv(256)
                if not data:
                    self.output_call("\r\n*** EOF ***\r\n\r\n")
                    sys.stdout.flush()
                    break
                self.output_call(data)
                #sys.stdout.flush()

        writer = threading.Thread(target=writeall, args=(chan,))
        writer.start()


    def init_shell(self, hostname):
        # setup logging
        paramiko.util.log_to_file("demo.log")

        username = ""
        if hostname.find("@") >= 0:
            username, hostname = hostname.split("@")
        else:
            hostname = self.output_call("Hostname: ")
        if len(hostname) == 0:
            self.output_call("*** Hostname required.")
            sys.exit(1)
        port = 22
        if hostname.find(":") >= 0:
            hostname, portstr = hostname.split(":")
            port = int(portstr)

        # now connect
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((hostname, port))
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
            if hostname not in keys:
                self.output_call("*** WARNING: Unknown host key!")
            elif key.get_name() not in keys[hostname]:
                self.output_call("*** WARNING: Unknown host key!")
            elif keys[hostname][key.get_name()] != key:
                self.output_call("*** WARNING: Host key has changed!!!")
                sys.exit(1)
            else:
                self.output_call("*** Host key OK.")

            # get username
            if username == "":
                default_username = getpass.getuser()
                self.output_call("Username [%s]: " % default_username)
                if len(username) == 0:
                    username = default_username

            self.agent_auth(self.trans, username)
            if not self.trans.is_authenticated():
                self.manual_auth(username, hostname)
            if not self.trans.is_authenticated():
                print("*** Authentication failed. :(")
                self.trans.close()
                sys.exit(1)

            self.chan = self.trans.open_session()
            self.chan.get_pty()
            self.chan.invoke_shell()

            if self.system == "posix":
                self.posix_shell(self.chan)
            elif self.system =="windows":
                self.windows_shell(self.chan)

            self.chan.close()
            self.trans.close()

        except Exception as e:
            print("*** Caught exception: " + str(e.__class__) + ": " + str(e))
            traceback.print_exc()
            try:
                self.trans.close()
            except:
                pass
            sys.exit(1)