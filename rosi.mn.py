#!/usr/bin/python
#coding: utf-8
import urllib2, sys, re
from pic_saver import get_download_url

def main(file_path):
	#Get urls from file
	url_list = []
	with open(file_path) as f:
		for line in f.readlines():
			url_list.append(line)

	download_url_list = []
	for u in url_list:
		res = urllib2.urlopen(u)
		#print res.read()
		#raw_link = re.search(r'[<]a href="(http://pan.baidu.com/s/[^"]+)" onclick="trackView\(this\);" target="_blank"[>]', res.read()).group(1)
		raw_link = re.search(r'href="(http://pan.baidu.com/s/[^"]+)"', res.read())
		if raw_link is not None:
			print u
			download_url_list.append(get_download_url(raw_link.group(1)))
	
	output_path = file_path + '.out'
	with open(output_path, 'w') as of:
		for du in download_url_list:
			of.write(du + '\n')


if __name__ == '__main__':
	if len(sys.argv) < 2:
		file_path = 'C:/Users/tiden/Desktop/download_list.txt'
	else:
		file_path = sys.argv[1]
	main(file_path)