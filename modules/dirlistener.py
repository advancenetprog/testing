import os
print "lol"
def run (**args):
	print "in dirlistener module"
	files = os.listdir(".")
	return str(files)