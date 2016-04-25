import cloudconnect, argparse, json, time
from urlparse import urlparse

parser = argparse.ArgumentParser()
parser.add_argument('--key', help='CF API Key')
parser.add_argument('--email', help='CF API Email')
parser.add_argument('--zone', help='Only lookup one zones settings')
parser.add_argument('--dest-zone', dest='destZone', help='Copy pagerules to zone')
parser.add_argument('--delete-all', dest='deleteAll', help='Delete all pagerules', action='store_true')
parser.add_argument('--delete-id', dest='deleteID', help='Delete only a single pagerule')
parser.add_argument('--force', help='Force a pagerule to override an already existing rule')
parser.add_argument('--import', help='import from a file')
parser.add_argument('--export', help='export to file, same output of --zone, but added to a file')
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
      return apiResponse['errors'][0]['code']
      try:
        print apiResponse['messages'][0]['message'], '\n'
      except:
        pass
      return False
    except(KeyError):
      return 'There was a failure, but no message'
  else:
    return apiResponse

def copy_all_pagerules(zoneID, destZoneID):
  zonePRs = cc.list_pagerules(zoneID)
  destZonePRs = cc.list_pagerules(zoneID)
  zonePagerulesResults = zonePRs['result']
  for zonePagerulesResult in reversed(zonePagerulesResults):
    print zonePagerulesResult['priority'], zonePagerulesResult['targets'][0]['constraint']['value']
    mpr = modify_url_pattern(zonePagerulesResult, zone, destZone)
    for z in mpr:
      targets = mpr['targets']
      actions = transform_actions(mpr['actions'])
      priority = mpr['priority']
      status = mpr['status']
    print 'creating page rule priority {}'.format(priority)
    pageruleAttempt = 1
    time.sleep(2)
    createPagerule = cc.create_pagerule(destZoneID, targets=targets, actions=actions, priority=priority, status=status)
    if check_success(createPagerule) == True:
      print 'Pagerule successfully copied'
    elif check_success(createPagerule) == 1004:
      pass
    else:
      pass

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

def modify_url_pattern(zonePageruleJson, zone, destZone):
  ''' If matchFirst is on, ignore any other matchs in the pattern. '''
  uri = zonePageruleJson['targets'][0]['constraint']['value']
  uri = uri.replace(zone, destZone)
  zonePageruleJson['targets'][0]['constraint']['value'] = uri
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

if __name__ == '__main__':
  if args.deleteAll:
    delete_all_pagerule(zoneID)
  elif args.deleteID:
    try: 
      print check_success(cc.delete_pagerule(zoneID, args.deleteID))['success']
    except:
      'Something went wrong'
  elif args.destZone:
    copy_all_pagerules(zoneID, destZoneID)
  elif args.zone:
    list_all_pagerules(zoneID)

