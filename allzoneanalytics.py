import json, cloudconnect, requests, argparse, time, sys, os
from collections import OrderedDict
from operator import itemgetter


parser = argparse.ArgumentParser()
parser.add_argument('--key', help='API key', required=True)
parser.add_argument('--email', help='API email', required=True)
parser.add_argument('-t', '--time', help='default is 1h=-1440 1month=-43200', default=-1440)
args = parser.parse_args()

cc = cloudconnect.CloudConnect(args.email, args.key)

def get_all_zids():
  zoneList = []
  pages = cc.list_zones()['result_info']['total_pages']
  for x in range(0, pages):
    x = x + 1 
    for zid in cc.list_zones(page=x)['result']:
      zoneList.append(zid['id'])
  return zoneList

total_req_acct = 0
total_bw_acct = 0 

for zid in get_all_zids():
  zoneName = cc.zone_details(zid)['result']['name']
  analytics = cc.analytics_dashboard(zid, since=args.time)
  total_req_zone = analytics['result']['totals']['requests']['all']
  total_bw_zone = analytics['result']['totals']['bandwidth']['all']
  print '{} -- {} Request {}MB'.format(zoneName, total_req_zone, total_bw_zone/1024/1024) 
  total_req_acct = total_req_acct + total_req_zone
  total_bw_acct = total_bw_acct + total_bw_zone

print 'Total Request: {}'.format(total_req_acct)
print 'Total BW: {}MB'.format(total_bw_acct/1024/1024)
