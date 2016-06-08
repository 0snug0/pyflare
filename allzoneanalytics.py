import json, cloudconnect, requests, argparse, datetime, sys, os, collections
from collections import OrderedDict
from operator import itemgetter
try: 
  from hurry.filesize import size
except(ImportError):
  print >> sys.stderr, 'Missing hurry.filesize module, you will not be able to use -H, --human. Fix by running:\nsudo pip install hurry.filesize'

now = datetime.datetime.now()
parser = argparse.ArgumentParser()
parser.add_argument('--key', help='API key')
parser.add_argument('--email', help='API email')
parser.add_argument('-t', '--time', help='default is 1h=-1440 1month=-43200', default=-1440)
parser.add_argument('--monthly', help='Get last year of analytics, agg monthly', action='store_true')
parser.add_argument('-H', '--human', help='Human Readable Format', action='store_true')
args = parser.parse_args()
cc = cloudconnect.CloudConnect(args.email, args.key)

def all_zones_zid_dict():
  zoneDict = {}
  pages = cc.list_zones()['result_info']['total_pages']
  for x in range(0, pages):
    x = x + 1 
    for zoneInfo in cc.list_zones(page=x)['result']:
      zoneDict[zoneInfo['name']] = zoneInfo['id']
  return zoneDict

def aggergate_month(zid, year, month):
  month = str(month).zfill(2)
  since = '{}-{}-01T00:00:00Z'.format(year, month)
  if int(month) == 12:
    month = 0
    year = year + 1
  until = '{}-{}-01T00:00:00Z'.format(year, str(int(month)+1).zfill(2))
  oneMonthAnalytics = cc.analytics_dashboard(zid, since=since, until=until)
  return oneMonthAnalytics

def monthly_aggregated(zone):
  zid = cc.get_zone_id(zone)
  month = now.month+1 
  year = now.year-1
  print zone
  for i in range(1, 12):
    monthly = aggergate_month(zid, year, month)
    bw = monthly['result']['totals']['bandwidth']
    req = monthly['result']['totals']['requests']
    if args.human:
      try:
        print '{}-{},{},{},{},{},{},{}'.format(month, year, size(bw['cached']), size(bw['uncached']), size(bw['all']), 
                                                          size(req['cached']), size(req['uncached']), size(req['all']))
      except(ImportError):
        print 'Missing hurry.filesize Module'
    else:
      print '{}-{},{},{},{},{},{},{}'.format(month, year, bw['cached'], bw['uncached'], bw['all'], req['cached'], req['uncached'], req['all'])
    if month == 12:
      month = 0
      year = year + 1
    month = month + 1

def get_all_zone_analytics(zoneDict):
  if type(zoneDict) != dict:
    print 'Function requires dict type, you provided {}'.format(type(zoneDict))
    exit()
  total_req_acct = 0
  total_bw_acct = 0 
  total_uncache_acct = 0
  for z in zoneDict:
    zid = zoneDict[z]
    zoneName = cc.zone_details(zid)['result']['name']
    analytics = cc.analytics_dashboard(zid, since=args.time)
    total_req_zone = analytics['result']['totals']['requests']['all']
    total_bw_zone = analytics['result']['totals']['bandwidth']['all']
    total_uncache_zone = analytics['result']['totals']['bandwidth']['uncached']
    print '\n\n{}: {} Request {}MB Total {}MB Uncached\nRequest:'.format(zoneName, total_req_zone, total_bw_zone/1024/1024, total_uncache_zone/1024/1024)
    for countryReq in analytics['result']['totals']['requests']['country']:
      print countryReq+':', analytics['result']['totals']['requests']['country'][countryReq],
    print '\nBandwidth:'
    for countryBw in analytics['result']['totals']['bandwidth']['country']:
      print countryBw+':', analytics['result']['totals']['bandwidth']['country'][countryBw],
    total_req_acct = total_req_acct + total_req_zone
    total_bw_acct = total_bw_acct + total_bw_zone
    total_uncached_acct = total_uncache_acct + total_uncache_zone

if args.monthly:
  print 'date, cached bw, uncached bw, total bw, cached req, uncached req, total req'
  for zone in all_zones_zid_dict():
    monthly_aggregated(zone)