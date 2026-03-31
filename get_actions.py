import PureCloudPlatformClientV2
from PureCloudPlatformClientV2.rest import ApiException
from dotenv import load_dotenv
import json
import csv
import os

print('validando PROXY')
PureCloudPlatformClientV2.configuration.proxy = 'http://10.104.244.30:8080'


load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')


client = PureCloudPlatformClientV2.api_client.ApiClient().get_client_credentials_token(client_id,client_secret)


api_instance = PureCloudPlatformClientV2.IntegrationsApi(client)
page_size = 25 
page = 1 


api_response = api_instance.get_integrations_actions(
        page_size=page_size,
        page_number=page).to_json()


def write_csv_header():
    headers = ['id',
                'name',
                'integration_id',
                'category',
                'version',
                 'config',
                'secure'
                ]
        
    with open('actions.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)

    print('Cabeçalho CSV foi escrito com sucesso.')


write_csv_header()


page_count = json.loads(api_response)['page_count']


def write_csv_data(api_response, page):
    page_number = page
    
    api_response = api_instance.get_integrations_actions(page_number=page_number).to_json()

    data = json.loads(api_response)
    actions = data['entities']

    with open('actions.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        for action in actions:
            id = action['id'] if 'id' in action else ''
            name = action['name'] if 'name' in action else ''
            integration_id = action['integration_id'] if 'integration_id' in action else ''
            category = action['category'] if 'category' in action else ''
            version = action['version'] if 'version' in action else ''
            # config = action['config'] if 'config' in action else ''
            secure = action['secure'] if 'secure' in action else ''
            

            writer.writerow([id,
                              name,
                              integration_id,
                              category,
                              version,
                              # config,
                              secure
                              ])

    print('Dados CSV da página', page,'foram escritos com sucesso.')

    if page_count > page:
        next_page = page + 1
       
        write_csv_data(api_response, next_page)



write_csv_data(api_response, page)