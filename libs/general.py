import logging
import time
import paramiko
import re
import sys
import os
import re
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

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
        stdin, stdout, stderr = conn.exec_command("hostnamectl")
        hostname_output = stdout.read().strip()
        f1 = re.compile("Static.*\n")
        s_hostname = f1.findall(hostname_output)[0].split(":")[1].strip()
        f2 = re.compile("Pretty.*\n")
        try:
            p_hostname = f2.findall(hostname_output)[0].split(":")[1].strip()
        except Exception:
            p_hostname = ""
        f3 = re.compile("Transient.*\n")
        try:
            t_hostname = f3.findall(hostname_output)[0].split(":")[1].strip()
        except Exception:
            t_hostname = ""

        if t_hostname == "" and p_hostname == "":
            return s_hostname
        elif p_hostname != "":
            return "%s (%s)" % (p_hostname, s_hostname)
        else:
            return s_hostname

    def get_hardware(self):
        conn = self.ssh_connect()
        stdin, stdout, stderr = conn.exec_command()

    def get_profile(self):
        conn = self.ssh_connect()
        stdin, stdout, stderr = conn.exec_command("tuned-adm active")
        profile_output = stdout.read()
        try:
            current_profile = profile_output.split(":")[1].strip()
        except Exception:
            current_profile = "none"
        return current_profile

class LoginCockpit(object):
    def __init__(self, ipaddr, username, passwd, port=9090):
        self.ipaddr = ipaddr
        self.username = username
        self.passwd = passwd
        self.port = port

    def init_webdriver(self):
        driver = Firefox()
        driver.implicitly_wait(20)
        test_url = "http://%s:%s" % (self.ipaddr, self.port)
        driver.get(test_url)
        return driver

    def login(self, webdriver):
        web_driver = webdriver
        username_field = web_driver.find_element_by_id("login-user-input")
        username_field.send_keys(self.username)
        passwd_field = web_driver.find_element_by_id("login-password-input")
        passwd_field.send_keys(self.passwd)

        login_btn = web_driver.find_element_by_id("login-button")
        login_btn.send_keys(Keys.ENTER)
        

    def run(self):
        web_driver = self.init_webdriver()
        self.login(web_driver)
        return web_driver