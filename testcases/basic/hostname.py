import sys
import os
import re
f = re.compile(".*/avocado-cockpit")
sys.path.append(f.findall(os.path.abspath(
    os.path.abspath(os.path.dirname(__file__))))[0])
from avocado import Test
from avocado import main
from libs import general


class TestHostname(Test):
    """
    : avocado: enable
    """
    default_params = {'timeout': 30}

    def setUp(self):
        self.pretty_name = self.params.get('pretty')
        self.real_name = self.params.get('real')
        self.ipaddr = self.params.get('ipaddr')
        self.port = self.params.get('port')
        self.testurl = "http://%s:%s" % (self.ipaddr, self.port)
        self.username = self.params.get('name', "/*/user1/")
        self.passwd = self.params.get('passwd', "/*/user1/")
        web_driver_obj = general.LoginCockpit(
            self.ipaddr, self.username, self.passwd, self.port)
        self.web_driver = web_driver_obj.run()
        self.ssh_conn_obj = general.EstabSSHConnect(self.ipaddr, self.username, self.passwd)

    def display_hostname_in_cockpit(self):
        web_driver = self.web_driver
        web_driver.switch_to.parent_frame()
        web_driver.implicitly_wait(10)
        web_driver.switch_to.frame("cockpit1:localhost/system")
        display_hostname = web_driver.find_element_by_id(
            "system_information_hostname_button").text
        return display_hostname

    def _test_default_hostname(self):
        display_hostname = self.display_hostname_in_cockpit()
        self.log.info("The hostname shown in cockpit page is: %s" % display_hostname)
        current_hostname = self.ssh_conn_obj.get_hostname()
        if display_hostname.strip() == current_hostname.strip():
            self.log.info("The hostname shown in cockpit page[%s] is the same as system[%s]!" % (display_hostname, current_hostname))
            result = 0
        else:
            self.log.error("The hostname shown in cockpit page[%s] is not the same as system[%s]!" % (display_hostname, current_hostname))
            result = 1
        return result


    def change_hostname(self):
        web_driver = self.web_driver
        web_driver.implicitly_wait(10)
        web_driver.switch_to.parent_frame()
        web_driver.switch_to_frame("cockpit1:localhost/system")
        web_driver.implicitly_wait(10)
        web_driver.find_element_by_id("system_information_hostname_button").click()
        web_driver.find_element_by_id("sich-pretty-hostname").clear()
        web_driver.find_element_by_id("sich-pretty-hostname").send_keys(self.pretty_name)
        web_driver.find_element_by_id("sich-hostname").clear()
        web_driver.find_element_by_id("sich-hostname").send_keys(self.real_name)
        web_driver.find_element_by_id("sich-apply-button").click()

    def check_hostname_after_change(self):
        display_hostname = self.display_hostname_in_cockpit()
        self.log.info("The hostname shown in cockpit page is: %s" % display_hostname)
        current_hostname = self.ssh_conn_obj.get_hostname()
        self.log.info("The hostname in system is: %s" % current_hostname)
        aimed_hostname = "%s (%s)" % (self.pretty_name, self.real_name)
        result = 0
        if current_hostname == aimed_hostname:
            self.log.info("Setup hostname in system succeed!")
            self.log.info("Aimed hostname is: %s" % aimed_hostname)
            self.log.info("Actually hostname in system is: %s" % current_hostname)
            result += 0
        else:
            self.log.error("Setup hostname in cockpit failed!")
            self.log.error("Aimed hostname is: %s" % aimed_hostname)
            self.log.error("Actually hostname in system is: %s" % current_hostname)
            result += 1

        if display_hostname == aimed_hostname:
            result += 0
            self.log.info("Cockpit display the right hostname as setup!")
            self.log.info("Aimed hostname is: %s" % aimed_hostname)
            self.log.info("Actually hostname in system is: %s" % display_hostname)
        else:
            self.log.error("Cockpit display the hostname different from setup!")
            self.log.error("Aimed hostname is: %s" % aimed_hostname)
            self.log.error("Cockpit display the hostname is: %s" % display_hostname)
            result += 1
        return result

    def _test_change_hostname_in_cockpit(self):
        self.change_hostname()
        result = self.check_hostname_after_change()
        return result

    def test(self):
        t_result = self._test_default_hostname()
        t_result += self._test_change_hostname_in_cockpit()
        self.assertEqual(0, t_result, 'Hostname test failed!')

    def tearDown(self):
        self.web_driver.close()


if __name__ == "__main__":
    main()
