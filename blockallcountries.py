import json, cloudconnect, requests, argparse, time, sys

parser = argparse.ArgumentParser()
parser.add_argument('--key', help='API key', required=True)
parser.add_argument('--email', help='API email', required=True)
parser.add_argument('--domain')
parser.add_argument('--mode', help='block or challenge or js or whitelist or delete', default='block')
parser.add_argument('--allow', help='Allow a Country')
args = parser.parse_args()

if args.mode == 'js':
  args.mode = 'js_challenge'

ABBV = ["AF",  "AX",  "AL",  "DZ",  "AS",  "AD",  "AO",  "AI",  "AQ",  "AG",  "AR",  "AM",  "AW",  "AU",  "AT",  "AZ",  "BS",  "BH",  "BD",  "BB",  "BY",  "BE",  "BZ",  "BJ",  "BM",  "BT",  "BO",  "BQ",  "BA",  "BW",  "BV",  "BR",  "IO",  "BN",  "BG",  "BF",  "BI",  "KH",  "CM",  "CA",  "CV",  "KY",  "CF",  "TD",  "CL",  "CN",  "CX",  "CC",  "CO",  "KM",  "CG",  "CD",  "CK",  "CR",  "CI",  "HR",  "CU",  "CW",  "CY",  "CZ",  "DK",  "DJ",  "DM",  "DO",  "EC",  "EG",  "SV",  "GQ",  "ER",  "EE",  "ET",  "FK",  "FO",  "FJ",  "FI",  "FR",  "GF",  "PF",  "TF",  "GA",  "GM",  "GE",  "DE",  "GH",  "GI",  "GR",  "GL",  "GD",  "GP",  "GU",  "GT",  "GG",  "GN",  "GW",  "GY",  "HT",  "HM",  "VA",  "HN",  "HK",  "HU",  "IS",  "IN",  "ID",  "IR",  "IQ",  "IE",  "IM",  "IL",  "IT",  "JM",  "JP",  "JE",  "JO",  "KZ",  "KE",  "KI",  "KP",  "KR",  "KW",  "KG",  "LA",  "LV",  "LB",  "LS",  "LR",  "LY",  "LI",  "LT",  "LU",  "MO",  "MK",  "MG",  "MW",  "MY",  "MV",  "ML",  "MT",  "MH",  "MQ",  "MR",  "MU",  "YT",  "MX",  "FM",  "MD",  "MC",  "MN",  "ME",  "MS",  "MA",  "MZ",  "MM",  "NA",  "NR",  "NP",  "NL",  "NC",  "NZ",  "NI",  "NE",  "NG",  "NU",  "NF",  "MP",  "NO",  "OM",  "PK",  "PW",  "PS",  "PA",  "PG",  "PY",  "PE",  "PH",  "PN",  "PL",  "PT",  "PR",  "QA",  "RE",  "RO",  "RU",  "RW",  "BL",  "SH",  "KN",  "LC",  "MF",  "PM",  "VC",  "WS",  "SM",  "ST",  "SA",  "SN",  "RS",  "SC",  "SL",  "SG",  "SX",  "SK",  "SI",  "SB",  "SO",  "ZA",  "GS",  "SS",  "ES",  "LK",  "SD",  "SR",  "SJ",  "SZ",  "SE",  "CH",  "SY",  "TW",  "TJ",  "TZ",  "TH",  "TL",  "TG",  "TK",  "TO",  "TT",  "TN",  "TR",  "TM",  "TC",  "TV",  "UG",  "UA",  "AE",  "GB",  "US",  "UM",  "UY",  "UZ",  "VU",  "VE",  "VN",  "VG",  "VI",  "WF",  "EH",  "YE",  "ZM",  "ZW"]
allow = [args.allow]
block_list = [block for block in ABBV if block not in allow]

cc = cloudconnect.CloudConnect(args.email, args.key)
zid = cc.get_zone_id(args.domain)

# Deletes first 100 only, run again if more than 100 need to be deleted
if args.mode == 'delete':
  firewall_list = cc.list_firewall_rules(zid, configuration_target='country', per_page=100)
  for fwl in firewall_list['result']:
    fwID = fwl['id']
    print fwID
    cc.delete_zone_firewall(zid, fwID)

else:
  for b in block_list:
    print b
    print cc.zone_firewall(zid, args.mode, 'country', b)
