import ninjapanel, os, json, requests, argparse
from collections import OrderedDict
from operator import itemgetter

#### Use client API and Email here
api_key = ''
api_email = ''

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--time', help='default is 1h=1440 1month=43200')
args = parser.parse_args()

class clientV4:
  client_v4_url = 'https://api.cloudflare.com/client/v4/'

  def _get(self, uri, auth_key, auth_email, query=None):
    self.endpoint = self.client_v4_url + uri
    self.headers = {'X-Auth-Email': auth_email, 'X-Auth-Key': auth_key, 'Content-Type': 'application/json'}
    try:
      self.params = query
      self.r = requests.get(self.endpoint, params=self.params, headers=self.headers)
    except(AttributeError):
      self.r = requests.get(self.endpoint, headers=self.headers)
    return self.r.text

  def search(self, page, auth_key, auth_email, query=None):
    return self._get(self, page, auth_key, auth_email, query)

  def details(self, page, identifier, details, auth_key, auth_email, query=None):
    '''
    page + identifier + details is just building the URI.
    https://api.cloudflare.com/client/v4/PAGE/IDENTIFIER/details
    zones + 123456789 + dns_records
    https://api.cloudflare.com/client/v4/zones/123456789/dns_records
    '''
    self.pagedetails = page +'/'+ identifier +'/'+ details
    return self._get(self, self.pagedetails, auth_key, auth_email, query)

  def analytics(self, identifier, auth_key, auth_email, t_range=1440):
    self.uri = 'zones/{}/analytics/dashboard?continuous=true&since=-{}'.format(identifier,t_range)
    return self._get(self.uri, auth_key, auth_email)

  def zones(self, auth_key, auth_email, query=None):
    self.uri = 'zones'
    self.params = query
    return self._get(self.uri, auth_key, auth_email, query=self.params)

zones = json.loads(clientV4().zones(api_key, api_email, {'page': 1}))
z_info = zones['result_info']
total_bw_acct = 0
total_req_acct = 0
for page in range(z_info['total_pages']):
  for zone in json.loads(clientV4().zones(api_key, api_email, {'page': page}))['result']:
    # print zone['name']
    zid = zone['id']
    if args.time:
      a = clientV4().analytics(zid, api_key, api_email, t_range=args.time)
    else:
      a = clientV4().analytics(zid, api_key, api_email)
    total_req_zone = json.loads(a)['result']['totals']['requests']['all']
    total_bw_zone = json.loads(a)['result']['totals']['bandwidth']['all']
    print '{} -- {} Request {}MB'.format(zone['name'], total_req_zone, total_bw_zone/1024/1024) 
    total_req_acct = total_req_acct + total_req_zone
    total_bw_acct = total_bw_acct + total_bw_zone
print 'Total Request: {}'.format(total_req_acct)
print 'Total BW: {}MB'.format(total_bw_acct/1024/1024)
  
