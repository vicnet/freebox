#!/usr/bin/env python

# Service Monitor for Freebox
# V0.0.5

# api doc: http://dev.freebox.fr/sdk/os/

#import sys,os
#sys.stdout = open(os.path.dirname(os.path.realpath(__file__))+"/freebox.log", "w")

print("Service Monitor Freebox plugin")

from pprint import pprint
import requests
import json
import hmac, hashlib
from requests.auth import AuthBase

class Freebox:

    class Auth(AuthBase):
        """Authorization class specific for freebox API"""

        session_token = None

        def __init__(self, session_token):
            self.session_token = session_token

        def __call__(self, r):
            # modify and return the request
            r.headers['X-Fbx-App-Auth'] = self.session_token
            return r

    localurl = 'http://mafreebox.freebox.fr/'
    url = localurl
    api = None
    auth = None

    def __init__(self, app_token, session_token = None, url = None):
        if not url is None:
            self.url = url
        self.api = self.url + 'api/v1/'
        #print "Url = " + self.url
        if session_token is None:
            session_token = self.sessionFromApp(app_token)
        #print "Session = " + session
        self.auth = self.Auth(session_token)

    def get(self, cmd, useauth=True):
        auth = None
        if useauth:
            auth = self.auth
        #print 'Request: ' + self.api+cmd+'/'
        r = requests.get(self.api+cmd+'/', auth = auth)
        #pprint(r.json())
        return r.json()['result']

    def post(self, cmd, data=None, useauth=True):
        auth = None
        if useauth:
            auth = self.auth
        r = requests.post(self.api+cmd+'/', data=json.dumps(data), auth = auth)
        #pprint(r.json())
        return r.json()['result']

    def put(self, cmd, data=None, useauth=True):
        auth = None
        if useauth:
            auth = self.auth
        r = requests.put(self.api+cmd+'/', data=json.dumps(data), auth = auth)
        #pprint(r.json())
        return r.json()['result']

    def version(self):
        # version is special api because without api/v1
        r = requests.get(self.url+"api_version")
        #pprint(r.json())
        return r.json()['api_version']

    def authorize(self):
        #data = {'app_id': 'servicemonitor.freebox', 'app_name': 'Service Monitor Freebox Plugin', 'app_version': '0.0.1', 'device_name': 'PC Famille' }
        #r = requests.post("http://mafreebox.freebox.fr/api/v1/login/authorize", data=json.dumps(data))
        #pprint(r.json())
        #json.result 'app_token': 'fnvDjHD8zYuymgbs4+Eg7jMLOEb46115zL9WGhNcx5nMAvuG8QfLH0I6Ft2TZCp8', 'track_id': 0}

        # get authorize status (could be long) 
        # r = requests.get("http://mafreebox.freebox.fr/api/v1/login/authorize/0")
        pass

    def challenge(self):
        return self.get('login', useauth=False)['challenge']

    def sessionFromApp(self, app_token):
        challenge = self.challenge()
        #print 'Chalenge = ' + challenge

        h = hmac.new(app_token,challenge,hashlib.sha1)
        password = h.hexdigest()
        #print 'Pass = '+ password

        data = { 'app_id': 'servicemonitor.freebox', 'password': password }
        r = self.post('login/session', data=data, useauth=False)
        return r['session_token']

    def session(self):
        return self.auth.session_token

    def wifiStatus(self):
        #pprint(self.get('wifi'))
        return self.get('wifi')

    def isWifiActive(self):
        return self.wifiStatus()['active']

    def activateWifi(self, active):
        data={ 'ap_params': { 'enabled': active } }
        r = self.put('wifi/config', data=data, useauth=True)


import sys, os
from ConfigParser import ConfigParser
from datetime import datetime, timedelta

class FreeboxParam(object):
    _cfg = ConfigParser()
    _filename = '.freebox'
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

    def session_datetime():
        def fget(self):
            dt = self.get('session_datetime')
            if dt is None:
                return None
            return datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
        def fset(self, value):
            self.set('session_datetime', value.strftime('%Y-%m-%d %H:%M:%S'))
        #return locals() but don't like name
        return dict(fget=fget, fset=fset)

    session_datetime = property(**session_datetime())

    def session_keep():
        """Delta time in seconds to keep information"""
        def fget(self):
            td = self.get('session_keep')
            if td is None:
                return 300 # 5 min
            return timedelta(seconds=int(td))
        def fset(self, value):
            self.set('session_keep', value)
        return locals()

    session_keep = property(**session_keep())

    # default value
    def url():
        """freebox url: local by default"""
        def fget(self):
            url = self.get('url')
            if url is None:
                return 'http://mafreebox.freebox.fr/'
            return url
        def fset(self, value):
            self.set('url', value)
        return locals()

    url = property(**url())

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

cfg = FreeboxParam()

# check expiration time
if not cfg.session_datetime is None:
    if datetime.now()>cfg.session_datetime+cfg.session_keep:
        cfg.session_token = None
else:
    cfg.session_token = None

freebox = Freebox(cfg.app_token, cfg.session_token, url=cfg.url)

# update session token with new one
if cfg.session_token is None:
    cfg.session_token = freebox.session()
    cfg.session_datetime = datetime.now()
