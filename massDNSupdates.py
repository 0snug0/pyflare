#! /usr/bin/python
import json, cloudconnect, requests, argparse, time, sys

''' 
Examples:
# Create www CNAME pointed to root and Orange Cloud
python massDNSupdates.py --key xxxx --email me@you.com --new --proxy --record-name www --record-type CNAME --content @

# Delete www CNAME
python massDNSupdates.py --key xxxx --email me@you.com --delete --record-name www --record-type CNAME

# Modify www CNAME records and Grey cloud
python massDNSupdates.py --key xxxx --email me@you.com --edit --no-proxy --record-name www --record-type CNAME --content sub.domain.com

'''

parser = argparse.ArgumentParser()

# Authentication
parser.add_argument('--key', help='API key', required=True)
parser.add_argument('--email', help='API email', required=True)
parser.add_argument('--identity', help='Use this instead of key and email if you have keyrings') # Future Dev with keyrings

# Actions
parser.add_argument('--new', help='Create new DNS records', action='store_true')
parser.add_argument('--delete', help='Delete DNS records', action='store_true')
parser.add_argument('--edit', help='Modify DNS records', action='store_true')
parser.add_argument('--view', help='View DNS records', action='store_true')
parser.add_argument('--exclude', help='Exclude domains') # Future Dev

# DNS parameters
parser.add_argument('--content', help='Where the record will resolve to')
parser.add_argument('--record-name', dest='recordName', help='If not defined root will be chosen, other wise only provide subdoamain name')
# example --record-name www
parser.add_argument('--record-type', dest='recordType' , help='Only A records will be changed by default. You can use @ point to root domain')
# example --record-type CNAME

# Orange/Grey Cloud
parser.add_argument('--proxy', help='Orange Cloud all records', dest='proxy', action='store_true')
parser.add_argument('--no-proxy', help='Grey Cloudall records', dest='proxy', action='store_false')
parser.set_defaults(proxy=True)

args = parser.parse_args()


cc = cloudconnect.CloudConnect(args.email, args.key)
page = 1

while True:
  listZones = cc.list_zones(page=page, per_page=20)
  for zone in listZones['result']:
    zid = zone['id']
    zName = zone['name']
    content = args.content

    # Point cname record to root
    if args.content == '@':
      content = zName

    # Defaults
    recType = []
    proxied = args.proxy

    # Record Name
    if args.recordName == '@':
      recName = zName
    elif args.recordName:
      recName = '{}.{}'.format(args.recordName, zName)
    else:
      # Default to root
      recName = zName


    if args.recordType:
      recType = args.recordType.upper()

    if args.proxy:
      proxied = args.proxy

    # View DNS records
    if args.view:
      listDNSRecs = cc.list_dns_records(zid, type=recType, name=recName)
      if listDNSRecs['success']:
        for dnsRecs in listDNSRecs['result']:
          did = dnsRecs['id']
          dName = dnsRecs['name']
          dType = dnsRecs['type']
          dContent = dnsRecs['content']
          if dnsRecs['proxied']:
            dProxy = '+'
          else:
            dProxy = '-'
          print '{} {} {} {} {}'.format(dProxy, did, dName, dType, dContent)

    # Create New DNS Records
    if args.new:
      createDNS = cc.create_dns_record(zid, recType, recName, content=content, proxied=proxied)
      if createDNS['success']:
        print 'Created {} to {}'.format(recName, content)
      else:
        print 'Tried creating {} and failed'.format(recName)
        print >> sys.stderr, 'Failure: {} Message: {}'.format(recName, createDNS)
    else:
      dnsRecs = cc.list_dns_records(zid, name=recName, type=recType)

      for dnsRec in dnsRecs['result']:
        recID = dnsRec['id']

        # Delete DNS records
        if args.delete:
          deleteDNS = cc.delete_dns_record(zid, recID)

          if deleteDNS['success']:
            print 'deleted {} {}'.format(recType, recName)
          else:
            print 'Tried deleting {} and Failed'.format(recName)
            print >> sys.stderr, 'Failure: {} Message: {}'.format(recName, deleteDNS)

        # Modify DNS records 
        if args.edit:
          updateDNS = cc.update_dns_record(zid, recID, content=content, type=recType, name=recName, proxied=proxied)

          if updateDNS['success']:
            print 'updated {} to {}'.format(recName, content)
          else:
            print 'Tried modifying {} and Failed'.format(recName)
            print >> sys.stderr, 'Failure: {} Message: {}'.format(recName, updateDNS)
  page = page + 1
  if listZones['result_info']['count'] == 0:
    break

