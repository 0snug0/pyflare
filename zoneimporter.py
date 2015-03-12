#! /usr/bin/python
# zoneimporter.py works and tested for A, AAAA, TXT, MX, and NS records to be upload to CloudFlare using APIv4
# MUST be in bind format
# Make sure you have added your api key and email address to this file
# This is not a CloudFlare supported script, but happy to help out, send bug reports or request to eric@cloudflare.com

# USEAGE:
#	python zoneimporter.py file.txt zone
#	python zoneimporter.py foobar.com.txt foobar.com

import requests, json
from sys import argv

###### CONFIG ######
cf_api = ''
cf_email = ''
cf_zone_name = argv[2]
cf_endpoint = 'https://api.cloudflare.com/client/v4/zones/'

headers = {'X-Auth-Email': cf_email, 'X-Auth-Key': cf_api, 'Content-Type': 'application/json'}


def getZoneID(zone_name):
	url = cf_endpoint + '?name=' +zone_name
	r = requests.get(url, headers=headers)
	return json.loads(r.text)

def recList():
	bind_file = f = open(argv[1])
	rec_list = []
	for line in bind_file:
		if 'IN\t' in line:
			rec_list.append(line.split())
	return rec_list

def buildDNSDict(rec_type, rec_name, rec_content, rec_ttl, priority=0):
	if rec_type.lower() == 'mx':
	 	data = {"type": rec_type, "name": rec_name, "content": rec_content, "ttl": rec_ttl, 'priority': priority}
	else:
		data = {"type": rec_type, "name": rec_name, "content": rec_content, "ttl": rec_ttl}
	return data

def postToCF(dns_dict):
	cf_zone_id = getZoneID(cf_zone_name)['result'][0]['id']
	url = cf_endpoint + cf_zone_id + '/dns_records'
	r = requests.post(url, data=dns_dict, headers=headers)
	response = json.loads(r.text)
	if response['success']:
		print 'Completed \n'
	else:
		print 'ERROR:', response['errors'][0]['message'], '\n'

for rec in recList():
	print rec[0], rec[3], ''.join(rec[4:])
	if rec[3].lower() == 'mx':
		dns_dict = buildDNSDict(rec[3], rec[0], rec[5], rec[1], priority = rec[4])
	elif rec[3].lower() == 'txt':
		dns_dict = buildDNSDict(rec[3], rec[0], ''.join(rec[4:]), rec[1])
	else:
		dns_dict = buildDNSDict(rec[3], rec[0], rec[4], rec[1])
	postToCF(json.dumps(dns_dict))