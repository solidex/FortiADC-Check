from FortiADCConfigAPI import *
import sys


if (len(sys.argv)<5):
	print "Usage: %s <host> <vdom> <username> <password> <ip/mask>" % sys.argv[0]
	print "Example: %s 192.168.1.99 data admin password 10.10.10.10/32" % sys.argv[0]
	exit(0)


api = FortiADCConfigAPI()
api.login(sys.argv[1], sys.argv[3], sys.argv[4])
api.add_black_list_entry(vdom=sys.argv[2], ips=[sys.argv[5]])
api.logout()
