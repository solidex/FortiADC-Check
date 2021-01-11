import sys
import os
import datetime
import json
import requests

import logging

try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.WARNING)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.WARNING)
requests_log.propagate = True

MONITOR_ACTIONS_TO_API_DICT = {
    'system ha status': 'api/system_ha/status',
    'slb all_vs_info': 'api/all_vs_info/vs_list',
    'platform info': 'api/platform/info'
}


class FortiADCAPI:


    MONITOR_ACTIONS = [
        'system ha status',
        'slb all_vs_info',
        'platform info',
        'logs'
    ]

    def __init__(self):
        requests.packages.urllib3.disable_warnings()
        self.session = requests.Session()
        self.session.verify = False

    def login(self, data):

        payload = { 'username': data['username'], 'password': data['password'] }
        self.host = data['host']
        response = self.session.post('https://%s/api/user/login' % self.host, json = payload )

        if response.status_code == requests.codes.ok:
            json_data = json.loads(response.text)
            self.session.headers.update({'Authorization': 'Bearer ' + json_data['token']})
        else:
            sys.exit('ERROR: Could not login to FortiADC')

    def _extend_login(self, url):
        response = self.session.post('https://%s/%s' % (self.host, url), data = [])

        if not response.status_code == requests.codes.ok:
            sys.exit('ERROR: Could not extend login')

    def monitor(self, data):
        action = data['action']
        vdom = data['vdom']
        if action in self.MONITOR_ACTIONS:
            if action == 'logs':
                return self._logs(data)
            else:
                response = self.session.get('https://%s/%s?vdom=%s' % (self.host, MONITOR_ACTIONS_TO_API_DICT[action], vdom))
                return response.status_code, response.text
        else:
            sys.exit('ERROR: Unknown action')

    def _logs(self, data):
        vdom = data['vdom']
        search_filter = data['log_search_filter']
        if data['log_type']:
            log_type = data['log_type']
        else:
            log_type = "attack"
        if data['log_subtype']:
            log_subtype = data['log_subtype']
        else:
            log_subtype = "ip_reputation"

        try:
            search_filter_json = json.loads(search_filter)
        except:
            search_filter = data['log_search_filter'].replace('\'', '"')
            search_filter_json = json.loads(search_filter)

        self._extend_login('api/log_report/logs?type=attack&subType=%s&vdom=data&refresh=1&action=add&filename=1.%s.alog' % (log_subtype, log_subtype))

        payload = {'draw':1,'columns':[],'order':[],'start':0,'length':100,'search':search_filter_json}

        url = 'https://%s/api/log_report/logs?action=server&type=%s&subType=%s&filename=1.%s.alog&vdom=%s&refresh=1' % (self.host, log_type, log_subtype, log_subtype, vdom)

        response = self.session.post(url, json=payload)
        return response.status_code, response.content

    def logout(self):
        response = self.session.get('https://%s/api/user/logout' % self.host)
