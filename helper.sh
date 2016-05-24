#!/usr/bin/bash

avocado run testcases/login/login.py --multiplex comm/comm.yaml
avocado run testcases/basic/hostname.py --multiplex comm/hostname.yaml
avocado run testcases/basic/performance.py --multiplex comm/performance.yaml