import sys
import os
import re
import time
f = re.compile(".*/avocado-cockpit")
sys.path.append(f.findall(os.path.abspath(
    os.path.abspath(os.path.dirname(__file__))))[0])
from avocado import Test
from avocado import main
from libs import general


class PerformanceTest(Test):
    """
    : avocado: enable
    """
    default_params = {'timeout': 50}

    def setUp(self):
        self.profile_name = self.params.get("option", "/*/profiles/*")
        self.ipaddr = self.params.get('ipaddr')
        self.port = self.params.get('port')
        self.testurl = "http://%s:%s" % (self.ipaddr, self.port)
        self.username = self.params.get('name', "/*/user1/")
        self.passwd = self.params.get('passwd', "/*/user1/")
        web_driver_obj = general.LoginCockpit(
            self.ipaddr, self.username, self.passwd, self.port)
        self.web_driver = web_driver_obj.run()

    def profile_css_dict(self):
        profile_dict = {"None": "div.list-group-item.active > p",
                        "balanced": "//div[2]/div/div[2]/p",
                        "desktop": "//div[3]/p",
                        "latency-performance": "//div[4]/p",
                        "network-latency": "//div[5]/p",
                        "network-throughput": "//div[6]/p",
                        "powersave": "//div[7]/p",
                        "throughput-performance": "//div[8]/p",
                        "virtual-guest": "//div[9]/p",
                        "virtual-host": "//div[10]/p"}
        return profile_dict

    def change_performance_from_cockpit(self):
        web_driver = self.web_driver
        web_driver.implicitly_wait(10)
        # web_driver.switch_to.frame("cockpit1:localhost/system")
        web_driver.find_element_by_css_selector(
            "td.button-location > div > button.btn.btn-default").click() # Enter to performance profile page
        web_driver.find_element_by_css_selector(
            "div.list-group-item.active").click()
        profile_dict = self.profile_css_dict()
        xpath_sel = profile_dict.get(self.profile_name)
        web_driver.find_element_by_xpath(xpath_sel).click()
        web_driver.find_element_by_xpath(
            "//div[2]/div/div/div[3]/button[2]").click()

    def performance_check_in_node(self):
        ssh_conn_obj = general.EstabSSHConnect(
            self.ipaddr, self.username, self.passwd)
        node_profile = ssh_conn_obj.get_profile()
        return node_profile

    def _test_default_performance_profile(self):
        web_driver = self.web_driver
        web_driver.implicitly_wait(10)
        web_driver.switch_to.frame("cockpit1:localhost/system")
        time.sleep(2)
        display_profile = web_driver.find_element_by_css_selector(
            "td.button-location > div > button.btn.btn-default").text.strip()
        node_profile = self.performance_check_in_node()
        if display_profile == node_profile:
            result = 0
            self.log.info("The default performance profile is [%s]!" %
                          display_profile)
        else:
            result = 1
            self.log.error(
                "The default performance profile display is [%s] which should be [%s]!"
                % (display_profile, node_profile))
        return result

    def _test_change_performance(self):
        web_driver = self.web_driver
        self.change_performance_from_cockpit()
        time.sleep(2)
        display_profile = web_driver.find_element_by_css_selector(
            "td.button-location > div > button.btn.btn-default").text.strip()
        node_profile = self.performance_check_in_node()
        if display_profile == self.profile_name and self.profile_name == node_profile:
            self.log.info("Cockpit shows performance profile as [%s]" % display_profile)
            self.log.info("Node setup performance profile as [%s]" % node_profile)
            self.log.info("Aimed to setup performance profile as [%s]" % self.profile_name)
            self.log.info("Cockpit setup profile %s succeed!" %
                          self.profile_name)
            result = 0
        else:
            self.log.error("Cockpit setup profile %s failed!" %
                           self.profile_name)
            self.log.error("Cockpit shows profile as [%s] while node shows [%s]!" % (
                display_profile, node_profile))
            result = 1
        return result

    def test(self):
        t_result = self._test_default_performance_profile()
        t_result += self._test_change_performance()
        self.assertEqual(
            0, t_result, "Test setup performance in cockpit failed!")

    def tearDown(self):
        self.web_driver.close()

if __name__ == "__main__":
    main()
