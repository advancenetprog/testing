import os
def run (**args):
	print "in dirlistener module"
	files = os.listdir(".")
	return str(files)