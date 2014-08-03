#coding: utf-8
import os, re
from shutil import copy
cpath = "D:/Downloads/collection"
spath = "D:/Downloads/rosi_selection"
copycollector = []
for path, dirs, files in os.walk(cpath):
	for picfile in files:
		if picfile.endswith(".jpg"):
			cnum = re.search(r"(\d+)$", path, re.U).group(1)
			sp, tp = os.path.join(path, picfile), os.path.join(spath, cnum + "-" + picfile)
			print sp, tp
			copy(sp, tp)
