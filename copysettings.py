import cloudconnect, json

email = 
key = 
srczone = #Source zone settings
destzone =  #Copy to zone settings

cc = cloudconnect.CloudConnect(email, key)
srczid = cc.get_zone_id(srczone)
srcCertCheck = cc.custom_cert(srczid)
destzid = cc.get_zone_id(destzone)
destCertCheck = cc.custom_cert(destzid)
# Check if destination has custom certificate
print 'Copying settings from {} to {}'.format(srczone, destzone)
if destCertCheck['result_info']['count']:
  cCert = True
  print 'Custom certificate installed. Will attempt to copy TLSv1.2 only settings from source\n'
else:
  cCert = False
  print 'Custom certificate not installed. TLSv1.2 only settings will be ignored\n'

srczsettings = cc.zone_settings(srczid)['result']
for srczset in srczsettings:
  srczsetid, srczsetvalue = srczset['id'], srczset['value']
  # TLS1.2 only works if Custom Certificate is installed
  if cCert == False and srczsetid == 'tls_1_2_only':
    continue
  # There is no advanced ddos api call since it's always on for biz/ent and always off for free/pro
  if srczsetid == 'advanced_ddos':
    continue
  # If mobile redirect is turned off from src ignore check dest mobile settings. To turn off
  # you must have a valid subdomain set.
  if srczsetid == 'mobile_redirect' and srczsetvalue['status'] == 'off':
    destmobilesetting = cc.get_zone_settings(destzid, srczsetid)['result']
    if destmobilesetting['value']['status'] == 'off':
      continue
    else:
      srczsetvalue['mobile_subdomain'] == destmobilesetting['value']['mobile_subdomain']
  destzset = cc.edit_zone_settings(destzid, srczsetid, value=srczsetvalue)
  for i in destzset['errors']:
    print srczsetid, srczsetvalue, i['code'], i['message']
  if destzset['success']:
    print 'Setting for {} set to {}'.format(srczsetid, srczsetvalue)