import requests, json, time
from bs4 import BeautifulSoup
from datetime import datetime

current_year = datetime.now().year

headers = {
    'Host': 'www.chronopost.fr',
    # 'Cookie': 'JSESSIONID_WEBCHR=032284136164ED414A64E603E846EBBD.tc-webchr-NODE7',
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15',
    'Referer': 'https://www.chronopost.fr/tracking-no-cms/suivi-page?listeNumerosLT=GC994370898JB&langue=en',
    'Accept-Language': 'cs-CZ,cs;q=0.9',
    'X-Requested-With': 'XMLHttpRequest',
}

response = json.loads(requests.get('https://www.chronopost.fr/tracking-no-cms/suivi-colis?&listeNumerosLT=GC994370898JB&langue=en',headers=headers).content.decode('utf-8').strip())['tab']
soup = BeautifulSoup(response, 'html.parser')
date_time = soup.find('td').text.strip().split('/2022')
date_time = date_time[0] + '/' + str(current_year) + ' ' + date_time[1]
service = soup.find_all('td')[1].text.strip()

try:
    datetime_object = datetime.strptime(date_time, "%m/%d/%Y %I:%M %p")
    timestamp = datetime.timestamp(datetime_object)
except:
    print(date_time)
    date_time = date_time[0] + '/2022 ' + date_time[1]
    datetime_object = datetime.strptime(date_time, "%m/%d/%Y %I:%M %p")
    timestamp = datetime.timestamp(datetime_object)

print(timestamp)
print(service)
