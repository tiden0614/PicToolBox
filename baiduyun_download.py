#!/usr/bin/python
#coding: utf-8
import urllib2, cookielib, sys, re, json
from string import Template
from urllib import urlencode

verify_url_template = Template('http://pan.baidu.com/share/verify?shareid=$shareid&uk=$uk&channel=chunlei&clienttype=0&web=1')
init_url_template = Template('http://pan.baidu.com/share/init?shareid=$shareid&uk=$uk')
link_url_template = Template('http://pan.baidu.com/share/link?shareid=$shareid&uk=$uk')
docrec_url_template = Template('http://pan.baidu.com/share/docrec?channel=chunlei&clienttype=0&web=1&bdstoken=$bdstoken')
count_url_template = Template('http://pan.baidu.com/share/count?channel=chunlei&clienttype=0&web=1&bdstoken=$bdstoken&shareid=$shareid&uk=$uk&sign=$sign&timestamp=$timestamp')
download_url_template = Template('http://pan.baidu.com/share/download?channel=chunlei&clienttype=0&web=1&uk=$uk&shareid=$shareid&timestamp=$timestamp&sign=$sign&bdstoken=$bdstoken')

plantcookie_url = 'http://pcs.baidu.com/rest/2.0/pcs/file?method=plantcookie&type=ett'

class RedirectHandler(urllib2.HTTPRedirectHandler):
	"""Stop when receive code 301 or 302"""
	def http_error_301(self, req, fp, code, msg, headers):
		pass
	def http_error_302(self, req, fp, code, msg, headers):
		pass


def get_non_redirected_response(url, timeout = 10):
	debug_handler = urllib2.HTTPHandler()
	opener = urllib2.build_opener(debug_handler, RedirectHandler)
	res, headers = None, None
	try:
		res = opener.open(url, timeout = timeout)
		headers = res.info()
	except urllib2.URLError as e:
		headers = e.hdrs
		if hasattr(e, 'code'):
			error_info = e.code
		elif hasattr(e, 'reason'):
			error_info = e.reason
	finally:
		if res:
			res.close()
	return headers


def get_download_url(raw_url):
	#分解raw_rul，获得ori_url和password
	splitter = re.search(r'^(http://pan.baidu.com/s/\w+)#(\w+)$', raw_url)
	ori_url, password = splitter.group(1), splitter.group(2)
	print 'ORIGINAL_URL =', ori_url
	print 'PASSWORD     =', password

	#试图通过分享码获得shareId和uk的值
	headers = get_non_redirected_response(ori_url)
	location = headers['Location']
	share_id, uk = re.search(r'shareid=(\d+)', location).group(1), re.search(r'uk=(\d+)', location).group(1)
	print 'GOT SHARE_ID = %s AND UK = %s' % (share_id, uk)

	#构造cookie的opener
	cookiejar = cookielib.CookieJar()
	url_opener_with_cookie = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))

	#验证分享密码
	init_url = init_url_template.substitute({'shareid': share_id, 'uk': uk})
	verify_url = verify_url_template.substitute({'shareid': share_id, 'uk': uk})
	link_url = link_url_template.substitute({'shareid': share_id, 'uk': uk})
	verify_res = url_opener_with_cookie.open(verify_url, 'pwd=' + password + '&vcode=')
	link_res = url_opener_with_cookie.open(link_url)
	link_content = link_res.read()

	#获取bdstoken，fsid等参数
	bdstoken = re.search(r'disk.util.ViewShareUtils.bdstoken="(\w+)";', link_content).group(1)
	fsid = re.search(r'disk.util.ViewShareUtils.fsId="(\w+)";', link_content).group(1)
	file_md5 = re.search(r'disk.util.ViewShareUtils.file_md5="(\w+)";', link_content).group(1)
	sign = re.search(r'disk.util.ViewShareUtils.sign="(\w+)";', link_content).group(1)
	timestamp = re.search(r'disk.util.ViewShareUtils.timestamp="(\w+)";', link_content).group(1)
	viewShareData_raw = re.search(r'disk.util.ViewShareUtils.viewShareData="([^;]+)";', link_content).group(1)
	view_share_data = json.loads(re.sub(r'\\', '', viewShareData_raw))
	server_filename = re.search(r'server_filename="([^;]+)";', link_content).group(1)

	print "FILE_NAME =", server_filename

	url_opener_with_cookie.open(plantcookie_url)
	# docrec_url = docrec_url_template.substitute({'bdstoken': bdstoken})
	# url_opener_with_cookie.open(docrec_url)
	count_url = count_url_template.substitute({'bdstoken': bdstoken, 'shareid': share_id, 'uk': uk, 'sign': sign, 'timestamp': timestamp})
	url_opener_with_cookie.open(count_url)
	download_url = download_url_template.substitute({'bdstoken': bdstoken, 'shareid': share_id, 'uk': uk, 'sign': sign, 'timestamp': timestamp})
	download_info = json.loads(url_opener_with_cookie.open(download_url, 'fid_list=%5B' + fsid + '%5D').read())
	dlink = re.sub(r'\\', '', download_info['dlink'])
	print dlink

	return dlink


if __name__ == '__main__':
	if len(sys.argv) < 2:
		#For test use
		argv = 'http://pan.baidu.com/s/1c0d7ADi#h2qz'
	else:
		argv = sys.argv[1]
	get_download_url(argv)
	return 0