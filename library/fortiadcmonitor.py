from ansible.module_utils.basic import *
from ansible.module_utils.FortiADCAPI import FortiADCAPI
import json
from argparse import Namespace
import logging
import difflib
import re

api = FortiADCAPI()
formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger('fortiadcapi')
hdlr = logging.FileHandler('/var/tmp/ansible-fortiadcapi.log')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

def fortiadc_monitor(data):
    logger.debug(data)
    api.login(data)

    status_code, output = api.monitor(data)
    api.logout()

    meta = {"status": status_code, 'http_status': 200 if status_code == 200 else 500, 'output': json.loads(output)}
    if status_code == 200:
        return False, True, meta
    else:
        return True, False, meta

def fortiadc_ssh(data):
    from netmiko import ConnectHandler

    adc1 = {
        "device_type": "generic",
        "host": data['host'],
        "username": data['username'],
        "password": data['password'],
        "session_log": "/tmp/netmiko-adc.log"
    }
    try:
        with ConnectHandler(**adc1) as net_connect:
            output = net_connect.send_command_timing("config vdom\nedit %s" % data['vdom'])
            output = net_connect.send_command(data['commands'])
            meta = {"status_code": 200, "out": output}
    except Exception as e:
        meta = {"status_code": 500,"exception": e}
    if meta['status_code'] == 200:
        return False, True, meta
    else:
        return True, False, meta

# def fortiadc_logs(data):
#     api.login(data)
#     status_code, output = api.get_logs(data['action'], data['vdom'])
#     api.logout()
#
#     meta = {"status": status_code, 'http_status': 200 if status_code == 200 else 500, 'output': json.loads(output)}
#     if status_code == 200:
#         return False, True, meta
#     else:
#         return True, False, meta

def main():
    fields = {
        "host": {"required": True, "type": "str"},
        "password": {"required": False, "type": "str", "no_log": True},
        "username": {"required": True, "type": "str"},
        "vdom": {"required": False, "type": "str", "default": "root"},
        "method": {"required": False, "type": "str", "default": "monitor", "choices": ["monitor", "ssh"]},
        "action": {"required": False, "choices": FortiADCAPI.MONITOR_ACTIONS, "type": "str"},
        "log_search_filter": {"required": False, "type": "str"},
        "log_type": {"required": False, "type": "str"},
        "log_subtype": {"required": False, "type": "str"},
        "https": {"required": False, "type": "bool", "default": "True"},
        "ssl_verify": {"required": False, "type": "bool", "default": "True"},
        "config_parameters": {"required": False, "type": "dict"},
        "commands": {"required": False, "type": "str"}
    }

    choice_map = {
        "monitor": fortiadc_monitor,
        "ssh": fortiadc_ssh
    }

    module = AnsibleModule(argument_spec=fields,
                           supports_check_mode=False)

    module.params['diff'] = False
    try:
        module.params['diff'] = module._diff
    except:
        logger.warning("Diff mode is only available on Ansible 2.1 and later versions")
        pass

    is_error, has_changed, result = choice_map.get(module.params['method'])(module.params)

    if not is_error:
        if module.params['diff']:
            module.exit_json(changed=has_changed, meta=result, diff={'prepared': result['diff']})
        else:
            module.exit_json(changed=has_changed, meta=result)
    else:
        module.fail_json(msg="Error", meta=result)


if __name__ == '__main__':
    main()
