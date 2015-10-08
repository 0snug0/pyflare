import json, cloudconnect, requests, argparse, time, sys

parser = argparse.ArgumentParser()
parser.add_argument('--key', help='API key', required=True)
parser.add_argument('--email', help='API email', required=True)
parser.add_argument('--content', help='Replace with this IP')
parser.add_argument('--record_name', help='If not defined root will be chosen, other wise only provide subdoamain name')
# example --record_name www
parser.add_argument('--record_type', help='Only A records will be changed by default')
# example --record_type CNAME
parser.add_argument('--proxy', help='Orange all records', dest='proxy', action='store_true')
parser.add_argument('--no-proxy', help='Grey all records', dest='proxy', action='store_false')
parser.set_defaults(proxy=True)
parser.add_argument('--new', help='Create new DNS records', action='store_true')
parser.add_argument('--delete', help='delete DNS records', action='store_true')
args = parser.parse_args()


cc = cloudconnect.CloudConnect(args.email, args.key)
page = 1

while True:
  listZones = cc.list_zones(page=page, per_page=20)

  for zone in listZones['result']:
    zid = zone['id']
    zName = zone['name']
    content = args.content

    # Defaults
    recType = 'A'
    proxied = args.proxy

    recName = zName
    if args.record_name:
      recName = '{}.{}'.format(args.record_name, recName)

    if args.record_type:
      recType = args.record_type

    if args.proxy:
      proxied = args.proxy

    if args.new:
      createDNS = cc.create_dns_record(zid, recType, recName, content=content, proxied=proxied)
      if createDNS['success']:
        print 'Created {} to {}'.format(recName, content)
      else:
        print >> sys.stderr, createDNS
    else:
      dnsRecs = cc.list_dns_records(zid, name=recName, type=recType)

      for dnsRec in dnsRecs['result']:
        recID = dnsRec['id']

        if args.delete:
          deleteDNS = cc.delete_dns_record(zid, recID)

          if deleteDNS['success']:
            print 'deleted {} {}'.format(recType, recName)
          else:
            print >> sys.stderr, 'Tried deleting {} and Failed'.format(recName)
            print >> sys.stderr, updateDNS

        else:
          updateDNS = cc.update_dns_record(zid, recID, content=content, type=recType, name=recName, proxied=proxied)

          if updateDNS['success']:
            print 'updated {} to {}'.format(recName, content)
          else:
            print >> sys.stderr, 'Tried modifying {} and Failed'.format(recName)
            print >> sys.stderr, updateDNS
  page = page + 1
  if listZones['result_info']['count'] == 0:
    break

