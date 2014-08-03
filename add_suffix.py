#!/usr/bin/python
#coding: utf-8
import os
suffix = '.zip'
folder = 'D:/Downloads/collection'

def main():
	for p in os.listdir(folder):
		path = os.path.join(folder, p)
		if os.path.isfile(path):
			if not path.endswith(suffix):
				print path
				os.rename(path, path + suffix)

if __name__ == '__main__':
	main()