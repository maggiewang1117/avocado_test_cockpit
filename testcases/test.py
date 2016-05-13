#!/usr/bin/evn python
import time

from avocado import main
from avocado import Test
import avocado
print avocado.Test.basedir

from libs import general

class SleepTest(Test):

	default_params = {'timeout': 3}

	def test(self):
		hostname = self.params.get('name', '/*/user1/*')
		self.log.info("get the hostname %s" % hostname)

		ipaddr = self.params.get('ipaddr')
		self.log.info("get the ip address %s" % ipaddr)

		passwd = self.params.get('passwd')
		self.log.info('get the password %s' % passwd)

		version = self.params.get('version')
		self.log.info('Get the version info %s' % version)

		# time.sleep(10)


if __name__ == "__main__":
	main()