import cloudconnect, argparse, json
from urlparse import urlparse

parser = argparse.ArgumentParser()
parser.add_argument('--key', help='CF API Key')
parser.add_argument('--email', help='CF API Email')
parser.add_argument('--zone', help='Only lookup one zones settings')
parser.add_argument('--dest-zone', dest='destZone', help='Copy pagerules to zone')
parser.add_argument('--delete-all', dest='deleteAll', help='Delete all pagerules', action='store_true')
args = parser.parse_args()

cc = cloudconnect.CloudConnect(args.email, args.key)

zone = args.zone
zoneID = cc.get_zone_id(zone)
destZone = args.destZone
destZoneID = cc.get_zone_id(destZone)

def check_success(apiResponse):
  if apiResponse['success'] == False:
    try:
      print apiResponse['errors'][0]['message']
      try:
        print apiResponse['messages'][0]['message'], '\n'
      except:
        pass
      return False
    except(KeyError):
      print apiResponse
      return 'There was a failure, but no message'
  else:
    return apiResponse

def copy_all_pagerules(zoneID, destZoneID):
  zonePRs = cc.list_pagerules(zoneID)
  destZonePRs = cc.list_pagerules(zoneID)
  zonePagerulesResults = zonePRs['result']
  for zonePagerulesResult in zonePagerulesResults:
    mpr = modify_url_pattern(zonePagerulesResult, destZone)
    for z in mpr:
      targets = mpr['targets']
      actions = transform_actions(mpr['actions'])
      priority = mpr['priority']
      status = mpr['status']
    createPagerule = cc.create_pagerule(destZoneID, targets=targets, actions=actions, priority=priority, status=status)
    if check_success(createPagerule):
      print 'Pagerule succesfully copied'

def delete_all_pagerule(zoneID):
  pagerules = cc.list_pagerules(zoneID)
  for pagerule in pagerules['result']:
    deletePagerule = cc.delete_pagerule(zoneID, pagerule['id'])
    checkSuccess = check_success(deletePagerule)
    if checkSuccess == False:
      checkSuccess
    else:
      print 'Pagerule {} successfully deleted'.format(checkSuccess['result']['id'])

def list_all_pagerules(zoneID):
  pagerules = cc.list_pagerules(zoneID)
  for pagerule in pagerules['result']:
    print json.dumps(pagerule)

def modify_url_pattern(zonePageruleJson, destZone, matchFirst=1):
  ''' If matchFirst is on, ignore any other matchs in the pattern. '''
  uri = zonePageruleJson['targets'][0]['constraint']['value']
  parsedUri = urlparse(uri)
  domain = parsedUri.netloc
  if parsedUri.scheme == '':
    # When the scheme is not present, urlparse will ignore
    uriScheme = 'http://' + uri
    parsedUri = urlparse(uriScheme)
    domain = parsedUri.netloc
    zonePageruleJson['targets'][0]['constraint']['value'] = '{}{}'.format(destZone, parsedUri.path)
    return zonePageruleJson
  else:
    zonePageruleJson['targets'][0]['constraint']['value'] = '{}://{}{}'.format(parsedUri.scheme, destZone, parsedUri.path)
    return zonePageruleJson

def modify_host(actions, zone, destZone):
  newActions = []
  for action in actions:
    try:
      if zone in str(action['value']):
        action['value'] = action['value'].replace(zone, destZone)
      else:
        pass
    except(KeyError):
      pass
  return actions

def remove_railgun_option(actions):
  ''' Right now you can't have railgun options set if railgun is not available for that zone'''
  newActions = []
  for action in actions:
    if action['id'] == 'railgun':
      pass
    else:
      newActions.append(action)
  return newActions

def transform_actions(actions):
  newActions = modify_host(actions, zone, destZone)
  newActions = remove_railgun_option(actions)
  return newActions

if args.deleteAll:
  delete_all_pagerule(destZoneID)
if args.destZone:
  copy_all_pagerules(zoneID, destZoneID)
elif args.zone:
  list_all_pagerules(zoneID)