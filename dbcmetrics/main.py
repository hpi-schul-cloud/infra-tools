from prometheus_client import start_http_server, Summary, Info
import random
import time
import requests, json

i = Info('Brandenburg', 'Version Information')
REQUEST_TIME = Summary('request_my_processing_seconds', 'Time spent processing request')
@REQUEST_TIME.time()
def process_request(t):
    time.sleep(t)

def getVersions(instance):
    url = requests.get("https://brandenburg.cloud/version")
    text = url.text
    data = json.loads(text)
    #manifest = data[0]
    print("Client verison of Brandenburg is: {}".format(data['version']))
    return (data['version'])

if __name__ == '__main__':
    start_http_server(9000)
    i.info({'Server': '1.0.0', 'Client': '{}'.format(getVersions('Brandenburg')), 'Nuxt': '1.0.0'})

    while True:
        process_request(random.random())