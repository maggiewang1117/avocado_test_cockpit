import logging
import time
import paramiko
import re
import sys
import os

class GenerLogger(object):
    def __init__(self, loggername):
        self.loggername = loggername
        f = re.compile(".*/cockpit_test")
        base_folder = f.findall(os.path.abspath(os.path.abspath(os.path.dirname(__file__))))[0]
        self.log_folder = os.path.join(base_folder, "logs")

    def initLogger(self):
        logger = logging.getLogger(self.loggername)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        fileHandler = logging.FileHandler(
            '%s/%s-%s.log' 
            % (self.log_folder, self.loggername, time.strftime("%Y%m%d-%H:%M:%S")))
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)
        return logger


class EstabSSHConnect(object):
    def __init__(self, ipaddr, username, passwd):
        self.ipaddr = ipaddr
        self.username = username
        self.passwd = passwd

    def ssh_connect(self):
        conn = paramiko.SSHClient()
        conn.load_system_host_keys()
        conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        conn.connect(self.ipaddr, 22, self.username, self.passwd)
        return conn

    def get_hostname(self):
        conn = self.ssh_connect()
        stdin, stdout, stderr = conn.exec_command("hostname")
        s_hostname = stdout.read()
        return stdout.read()

    def get_hardware(self):
        conn = self.ssh_connect()
        stdin, stdout, stderr = conn.exec_command()
