import requests

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import sys

# from fadcos_utils import *

BASE_HEADERS = {
    'Content-Type': 'application/json',
}

class FortiADCConfigAPI:

    auth_json = {}
    ip = None

    def login(self, ip, username, password):

        self.ip = ip
        payload = {'username': str(username), 'password': str(password)}
        url = 'api/user/login'

        response = requests.post('https://{}/{}'.format(str(self.ip), url), json=payload, verify=False)
        if response.status_code == 200:
            resp_json = response.json()
            cookie = response.headers.get('Set-Cookie').split(';')[0]
            self.auth_json = {'Authorization':'Bearer ' +  resp_json['token'], 'Cookie': cookie}

    def _extend_login(self, url):
        response = requests.post('https://%s/%s' % (self.ip, url), headers=self.auth_json, verify=False)
        print(response.text)
        if response.status_code == 200:
            resp_json = response.json()
            cookie = response.headers.get('Set-Cookie').split(';')[0]
            self.auth_json = {'Authorization':'Bearer ' +  resp_json['token'], 'Cookie': cookie}
        else:
            sys.exit('ERROR: Could not extend login')

    def logout(self):
        url = 'api/user/logout'
        response = requests.get('https://{}/{}'.format(str(self.ip), url), headers=self.auth_json, verify=False)
        return response.status_code

    def get_platform_info(self):
        url = 'api/platform/info'
        response = requests.get('https://{}/{}'.format(str(self.ip), url), headers=self.auth_json, verify=False)
        return response.json()

    def get_black_list(self, vdom):
        if vdom:
            url = 'api/load_balance_reputation_block_list_child_entries?vdom={}'.format(vdom)
            # self._extend_login('/api/load_balance_reputation?vdom=%s' % vdom)
        else:
            url = 'api/load_balance_reputation_block_list_child_entries'
            # self._extend_login('/api/load_balance_reputation')

        response = requests.get('https://{}/{}'.format(str(self.ip), url), headers=self.auth_json, verify=False)
        print(response.text)
        return response.json()

    def is_in_blacklist(self, ip, black_list):
        for entry in black_list['payload']:
            if entry['ip-netmask'] == str(ip):
                return True
        return False

    def get_mkey(self, ip, black_list):
        for entry in black_list['payload']:
            if entry['ip-netmask'] == str(ip):
                return int(entry['mkey'])
        return -1

    def add_black_list_entry(self, vdom, ips):
        if vdom:
            url = 'api/load_balance_reputation_block_list_child_entries?vdom={}'.format(vdom)
            black_list = self.get_black_list(vdom=vdom)
        else:
            url = 'api/load_balance_reputation_block_list_child_entries'
            black_list = self.get_black_list()

        response_codes = []
        for ip in ips:
            if not self.is_in_blacklist(ip=ip, black_list=black_list):
                payload = {
                        "end-ip": "0.0.0.0",
                        "ip-netmask": str(ip),
                        "start-ip": "0.0.0.0",
                        "status": "enable",
                        "type": "ip-netmask"
                        }
                response = requests.post('https://{}/{}'.format(str(self.ip), url), headers=self.auth_json, json=payload, verify=False)
                response_codes.append(response.status_code)
        return response_codes


    def delete_black_list_entry(self, vdom, ips):
        if vdom:
            url = 'api/load_balance_reputation_block_list_child_entries?vdom={}'.format(vdom)
            black_list = self.get_black_list(vdom=vdom)
        else:
            url = 'api/load_balance_reputation_block_list_child_entries'
            black_list = self.get_black_list()

        response_codes = []
        for ip in ips:
            mkey = self.get_mkey(ip=ip, black_list=black_list)
            if mkey != -1:
                print("deleting")
                response = requests.delete('https://{}/{}&mkey={}'.format(str(self.ip), url, mkey), headers=self.auth_json, verify=False)
                response_codes.append(response.status_code)
        return response_codes
