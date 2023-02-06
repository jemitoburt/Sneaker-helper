import requests, os, json

def validate_key():
    path = os.getcwd()
    json_data = open(path + '/config.json').read()
    config = json.loads(json_data)

    url = "https://api.whop.com/api/v2/memberships/{}/validate_license".format(config['license_key'])

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer dbleCu3LptyDy1CTbvRq7ik4uzs91AFA4OrGISQbt6A",
        "content-type": "application/json"
    }
    payload = {"metadata": {}}

    try:
        validation = json.loads(requests.post(url, headers=headers, json=payload).text)['valid']
        return validation
    
    except:
        validation = False
        return validation