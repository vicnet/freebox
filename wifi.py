#!/usr/bin/env python

from freebox import freebox

import sys

def startWifi():
	freebox.activateWifi(True)
	sys.exit(0)

def stopWifi():
	freebox.activateWifi(False)
	sys.exit(1)

def statusWifi():
	if freebox.isWifiActive():
		print('Wifi is active')
		sys.exit(0)
	else:
		print('Wifi is inactive')
		sys.exit(1)

commands = {
	'on': startWifi,
	'off': stopWifi,
	'status': statusWifi
	}

commands[sys.argv[1]]();
