#!/usr/bin/env python

from freebox import freebox

import sys, os
from ConfigParser import ConfigParser
from datetime import datetime, timedelta, time

class WifiParam(object):
    _cfg = ConfigParser()
    _filename = '.wifi'
    _section = 'freebox'

    def __init__(self):
        self._filename =  os.path.dirname(os.path.realpath(sys.argv[0])) + '/' + self._filename
        self._cfg.read(self. _filename)
        if not self._cfg.has_section(self._section):
            self._cfg.add_section(self._section)
        print('Config file name: ' + self._filename)

    def set(self, param, value):
        self._cfg.set(self._section, param, value)
        self._cfg.write(file(self._filename,'w'))

    def get(self, param):
        if not self._cfg.has_option(self._section, param):
            return None
        return self._cfg.get(self._section, param)

    def wifi_datetime():
        def fget(self):
            dt = self.get('wifi_datetime')
            if not dt:
                return None
            return datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
        def fset(self, value):
            if value is None:
                self.set('wifi_datetime', '')
            else:
                self.set('wifi_datetime', value.strftime('%Y-%m-%d %H:%M:%S'))
        #return locals() but don't like name
        return dict(fget=fget, fset=fset)

    wifi_datetime = property(**wifi_datetime())

    def wifi_keep():
        """Delta time in seconds to keep information"""
        def fget(self):
            td = self.get('wifi_keep')
            if td is None:
                return timedelta(30*60) # 30 min
            return timedelta(seconds=int(td))
        def fset(self, value):
            self.set('wifi_keep', value)
        return locals()

    wifi_keep = property(**wifi_keep())

    def __getattr__(self, name):
        # don't get 'private' attr nor special one with __
        if name.startswith("_"):
            return object.__getattr__(self, name)
        return self.get(name)

    def __setattr__(self, name, value):
        # properties are not handle here but by object class
        if name in dir(self):
            object.__setattr__(self,name,value)
            return
        self.set(name, value)

cfg = WifiParam()

if (len(sys.argv)>1):
    freebox.activateWifi(True)
    cfg.wifi_datetime = datetime.combine(datetime.now(),time(int(sys.argv[1])))
    print 'Activate until',cfg.wifi_datetime
    exit(0)

if not freebox.isWifiActive():
    # nothing to do
    print('Nothing to do')
    exit(0)

# wifi is active

if cfg.wifi_datetime is None:
    # wifi just started
    print('Wifi just started')
    cfg.wifi_datetime = datetime.now()
    exit(0)

# wifi is actived fro msome time

# check
if datetime.now()>cfg.wifi_datetime+cfg.wifi_keep:
    print('Wifi started from too long time')
    # too many time
    # desactivate
    freebox.activateWifi(False)
    # and reset time
    cfg.wifi_datetime = None
    exit(0)

print('Wifi started')
