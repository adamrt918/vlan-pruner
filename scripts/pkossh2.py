import paramiko
import time
import argparse

class SSH(object):
    # Initializes and gets the variables parsed.
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--host", required=True, help="Target switch hostname or IP")
        parser.add_argument("--username", required=True, help="SSH username")
        parser.add_argument("--key_file", required=True, help="Path to SSH private key")
        self.args = parser.parse_args()

    # Connects to the client.
    def connect(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(self.args.host, username=self.args.username, key_filename=self.args.key_file)
            shell = ssh.invoke_shell()
            time.sleep(1)
            shell.recv(1000)
            return ssh, shell
        except Exception as e:
            print(f"Connection failed: {e}")
            return None, None

    # Sends commands to the client
    def send_command(self, shell, command):
        shell.send(command + "\n")
        time.sleep(2)
        output = ""
        while shell.recv_ready():
            output += shell.recv(65535).decode('utf-8')
            time.sleep(0.5)
        return output

    # Closes the ssh connection
    def close(self):
        if self.client:
            self.client.close()