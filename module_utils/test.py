from FortiADCAPI import *

api = FortiADCAPI()
data = {}
data['username'] = 'admin'
data['password'] = ''
data['host'] = ''
data['action'] = 'logs'
data['vdom'] = 'data'
data['log_search_filter'] = """
  [{"property":"src","operator":"equals","value":{"exclude":"0","val1":""}}]
"""
data['log_type'] = "attack"
data['log_subtype'] = "waf"

api.login(data)
print(api.get_black_list(data))
api.logout()
