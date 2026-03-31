import PureCloudPlatformClientV2
from PureCloudPlatformClientV2.rest import ApiException
from dotenv import load_dotenv
import json
import csv
import os

print('validando PROXY')
PureCloudPlatformClientV2.configuration.proxy = 'http://10.104.244.30:8080'

# load credentials in file .env
load_dotenv()

# client = PureCloudPlatformClientV2.ApiClient
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

# client.login_client_credentials_grant(client_id, client_secret)
client = PureCloudPlatformClientV2.api_client.ApiClient().get_client_credentials_token(client_id,client_secret)


# create an instance of the API class
api_instance = PureCloudPlatformClientV2.IntegrationsApi(client)
page_size = 25 # int | Page size. The max that will be returned is 100. (optional) (default to 25)
page = 1 # int | Page number (optional) (default to 1)

# return json
api_response = api_instance.get_integrations(
        page_size=page_size,
        page_number=page).to_json()
with open('integrations_json.txt', 'w', encoding='utf-8') as file:
  file.write(str(api_response))
  
print('JSON gerado com sucesso')

# function of header
def write_csv_header():
    headers = ['id',
                'name',
                'intended_state'
                'integration_type',
                'config',
                'reported_state_code',
                'reported_state_effective',
                'last_update',
                'integration_type',
                'localizable_message_code',
                'message'
                ]
        
    with open('integrations.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)

    print('Cabeçalho CSV foi escrito com sucesso.')

# execute function of header
write_csv_header()

# count number of pages in the return API
page_count = json.loads(api_response)['page_count']
page = 1

# function of write the body
def write_csv_data(api_response, page): 

    data = json.loads(api_response)
    integrations = data['entities']

    with open('integrations.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        for integration in integrations:
            id = integration['id'] if 'id' in integration else ''
            name = integration['name'] if 'name' in integration else ''
            intended_state = integration['intended_state'] if 'intended_state' in integration else ''
            config = integration['config']['current']['id'] if 'config' in integration else ''
            reported_state_code = integration['reported_state']['code'] if 'reported_state' in integration else ''
            reported_state_effective = integration['reported_state']['effective'] if 'reported_state' in integration else ''
            last_update = integration['reported_state']['last_updated'] if 'reported_state' in integration else ''            
            integration_type = integration['integration_type']['id'] if 'integration_type' in integration else ''
            if integration['reported_state']['detail'] is not None:
                localizable_message_code = integration['reported_state']['detail']['localizable_message_code'] if 'localizable_message_code' else ''
                message = integration['reported_state']['detail']['message'] if 'message' else ''
            else:
                localizable_message_code = ' '
                message = ' '

            writer.writerow([id,
                            name,
                            intended_state,
                            integration_type,
                            config,
                            reported_state_code,
                            reported_state_effective,
                            last_update,
                            integration_type,
                            localizable_message_code,
                            message
                            ])

    print('Dados CSV da página', page,'foram escritos com sucesso.')

    if page_count > page:
        next_page = page + 1
        # Recursively call the function for the next page
        write_csv_data(api_response, next_page)


# call the function for the 1st time
write_csv_data(api_response, page)