import json, cloudconnect, requests, argparse, time, sys

parser = argparse.ArgumentParser()
parser.add_argument('--key', help='API key', required=True)
parser.add_argument('--email', help='API email', required=True)
parser.add_argument('--newip', help='Replace with this IP')
# parser.add_argument('--record_name', help='If not defined root will be chosen, other wise only provide subdoamain name') # Place holder for future dev
# parser.add_argument('--record_type', help='Only A records will be changed by default') # Place holder for future dev
args = parser.parse_args()



cc = cloudconnect.CloudConnect(args.email, args.key)
page = 1
while True:
  listZones = cc.list_zones(page=page, per_page=20)
  for zone in listZones['result']:
    zid = zone['id']
    zName = zone['name']
    dnsRecs = cc.list_dns_records(zid, name=zName, type='A')
    for dnsRec in dnsRecs['result']:
      dnsRecID = dnsRec['id']
      recName = dnsRec['name']
      updateDNS = cc.update_dns_record(zid, dnsRecID, content=args.newip, type='A', name=recName)
      if updateDNS['success']:
        print 'updated {} to {}'.format(recName, args.newip)
      else:
        print 'Tried {} and Failed'.format(recName)
        print updateDNS
  page = page + 1
  if listZones['result_info']['count'] == 0:
    break

