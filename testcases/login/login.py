import sys
import os
import re
f = re.compile(".*/avocado-cockpit")
sys.path.append(f.findall(os.path.abspath(
    os.path.abspath(os.path.dirname(__file__))))[0])
import time
from avocado import Test
from avocado import main
from libs import general
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys


class TestLogin(Test):
    """
    : avocado: enable
    """
    default_params = {'timeout': 30}

    def setUp(self):
        self.ipaddr = self.params.get('ipaddr', "/*/ipaddr1/")
        self.port = self.params.get('port', '/*/ipaddr1/')
        self.testurl = "http://%s:%s" % (self.ipaddr, self.port)
        self.username = self.params.get('name', "/*/user1/")
        self.passwd = self.params.get('passwd', "/*/user1/")
        self.rhevh_version = self.params.get('version', "/*/version36/")
        self.result = 0

    def init_webdriver(self):
        self.log.info("Inital Firefox as the testing webdriver!")
        driver = Firefox()
        driver.implicitly_wait(20)
        driver.get(self.testurl)
        return driver

    def login(self, web_driver):
        web_driver = web_driver
        username_field = web_driver.find_element_by_id("login-user-input")
        username_field.send_keys(self.username)
        passwd_field = web_driver.find_element_by_id("login-password-input")
        passwd_field.send_keys(self.passwd)

        login_btn = web_driver.find_element_by_id("login-button")
        login_btn.send_keys(Keys.ENTER)
        result = self.check_login_status(web_driver)
        return result

    def check_login_status(self, web_driver):
        web_driver = web_driver
        web_driver.implicitly_wait(10)
        time.sleep(2)
        current_user = web_driver.find_element_by_id("content-user-name").text

        if current_user.strip() == self.username:
            self.log.info("Login with '%s' succeed!" % self.username)
            self.result += 0
        else:
            self.log.error("Login with '%s' failed!" % self.username)
            self.result += 1
        return self.result

    def get_all_infos_in_server(self):
        self.ssh_login = general.EstabSSHConnect(
            self.ipaddr, self.username, self.passwd)
        self.ssh_conn = self.ssh_login.ssh_connect()
        stdin, stdout, stderr = self.ssh_conn.exec_command("hostname")
        s_hostname = stdout.read()
        return s_hostname

    def check_server_name_in_login_page(self, web_driver):
        web_driver = web_driver
        server_name = str(web_driver.find_element_by_id('server-name').text)
        s_hostname = self.get_all_infos_in_server().strip()
        f = re.compile(s_hostname)

        if f.findall(server_name):
            self.log.info("Login page shows '%s'" % server_name)
            self.log.info("Hostname in host is '%s'" % s_hostname)
            self.result += 0
        else:
            self.log.error("Login page shows '%s'" % server_name)
            self.log.error("Hostname in host is '%s'" % s_hostname)
            self.result += 1
        return self.result

    def check_version_in_login_page(self, web_driver, verion_name):
        web_driver = web_driver
        version_in_login = str(web_driver.find_element_by_id("brand").text)
        verion_name = verion_name.upper()
        f = re.compile(verion_name)

        if f.findall(version_in_login):
            self.log.info("Login Page shows '%s'" % version_in_login)
            self.result += 0
        else:
            self.log.error("Login Page shows '%s'" % version_in_login)
            self.log.error("Version should be '%s'" % verion_name)
            self.result += 1
        return self.result

    def test(self):
        f_driver = self.init_webdriver()
        total_result = self.check_version_in_login_page(
            f_driver, self.rhevh_version)
        total_result += self.check_server_name_in_login_page(f_driver)
        total_result += self.login(f_driver)
        f_driver.close()
        self.assertEqual(0, total_result, "Login test failed!")


if __name__ == "__main__":
    main()