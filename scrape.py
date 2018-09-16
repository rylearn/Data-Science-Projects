
import urllib2
import re
import os

base_url = raw_input()
website = urllib2.urlopen(base_url)
html = website.read()
links = re.findall(".*href=.*", html)

dir_name = "cs145"
if not os.path.exists(dir_name):
	os.mkdir(dir_name)

for link in links:
	# print(link)
	res = re.search(r'"(.*?)"', link)
	res2 = re.search(r'http', link)
	if res2 != None:
		continue

	full_url = base_url + res.group(1)	
	print(base_url)
	print(full_url)

	split_url_slash = full_url.split("/")
	last_elem = len(split_url_slash) - 1

	is_file = None
	full_path = None
	if "." in split_url_slash[last_elem]:
		len1 = len(split_url_slash) - 2
		len2 = len(split_url_slash) - 3

		str1 = split_url_slash[len1]
		str2 = split_url_slash[len2]

		# print(str2)
		# print(str1)
		# full_path = dir_name + '/' + str2 + '/' + str1
		
		# if not os.path.exists(full_path):
		# 	try:
		# 		os.makedirs(full_path)
		# 	except OSError:
		# 		print("Error in producing directory")
		
		is_file = True

	# print("Path" + str(full_path))
	# if is_file:
	# 	filename = split_url_slash[last_elem]
	# 	full_path = full_path + '/' + filename
	# 	print(full_path)
	# 	if not os.path.exists(full_path):
	# 		response = urllib2.urlopen(full_url)
	# 		file = open(full_path, 'wb')
	# 		file.write(response.read())
	# 		file.close()


