#!/usr/bin/python2.7
import redis
import sys
import os
import time
import paramiko


class ReceiveIpAddr(object):
    def __init__(self):
        self.redis_host = "10.66.9.216"
        self.redis_conn = redis.StrictRedis(host=self.redis_host,port=6379, db=0, password="redhat")
        self.p = self.redis_conn.pubsub(ignore_subscribe_messages=True)
        self.p.subscribe("dell-per510-01.lab.eng.pek2.redhat.com-cockpit")

    def receive_ipaddr(self):
        msg = self.p.parse_response()
        try:
            if "redhat" in msg[-1]:
                ipaddr = msg[-1].split(",")[0]
                return ipaddr
            elif "done" in msg[-1]:
                self.p.unsubscribe()
                return 2
        except Exception:
            return 1

    def test_connection(self, ipaddr):
        conn = paramiko.SSHClient()
        conn.load_system_host_keys()
        conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            conn.connect(ipaddr, 22, "root", "redhat", timeout=10)
            res = 0
        except Exception:
            res = 1
        finally:
            return res



    def run_avocado(self, ipaddress):
        ipaddr_str = "ipaddr: " + ipaddress
        abspath = os.path.abspath(os.path.dirname(__file__))
        comm_file_path = os.path.join(abspath, "comm/comm.yaml")
        run_test_path = os.path.join(abspath, "helper.sh")
        res = os.system("sed -i 's/ipaddr: .*/%s/' %s" % (str(ipaddr_str), str(comm_file_path)))
        if res == 0:
            run_test = os.system("source %s" % run_test_path)
            self.redis_conn.publish("dell-per510-01.lab.eng.pek2.redhat.com-cockpit", "done")
            return 0
        else:
            return 1






if __name__ == "__main__":
    obj1 = ReceiveIpAddr()
    try:
        while True:
            ipaddr = obj1.receive_ipaddr()
            if ipaddr == 1:
                print "break for next test!"
                time.sleep(5)
                continue
            elif ipaddr == 2:
                print "all the test finished!"
                break
            else:
                while True:
                    print "Try to connect %s" % ipaddr
                    res_conn = obj1.test_connection(ipaddr)
                    print res_conn

                    if res_conn == 0:
                        print "Connect succeed! try to run test now!"
                        res_run = obj1.run_avocado(ipaddr)
                        print res_run
                        if res_run == 0:
                            break
                        else:
                            raise Exception("Modify comm.yaml failed!")
                    else:
                        print "can not connect %s" % ipaddr
                        time.sleep(10)
                        print "wait for 10s to try again"
                        continue
    except Exception, e:
        print e
