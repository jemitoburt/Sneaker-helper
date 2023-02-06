import requests
import json
import time
import datetime

order_number = 'GC994357597JB'

headers = {
    'Host': 'www.chronopost.fr',
    # 'Cookie': 'JSESSIONID_WEBCHR=35827F9D9042B1C55262FDD438B9310F.tc-webchr-NODE2',
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15',
    'Referer': 'https://www.chronopost.fr/tracking-no-cms/suivi-page?listeNumerosLT={}&langue=en'.format(order_number),
    'Accept-Language': 'cs-CZ,cs;q=0.9',
    'X-Requested-With': 'XMLHttpRequest',
}

response = json.loads(requests.get('https://www.chronopost.fr/tracking-no-cms/suivi-colis?&listeNumerosLT={}&langue=en'.format(order_number),headers=headers).text)['top']
print(response.strip())