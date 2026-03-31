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
api_instance = PureCloudPlatformClientV2.OAuthApi(client)

# The list of OAuth clients
api_response = api_instance.get_oauth_clients().to_json()

# return json
with open('OAuth_json.txt', 'w', encoding='utf-8') as file:
  file.write(str(api_response))
  
print('JSON gerado com sucesso')

# function of header
def write_csv_header():
    headers = ['id',
                'name',
                'access_token_validity_seconds',
                'description',
                'registered_redirect_uri',
                'secret',
                'date_created',
                'created_by',
                'date_modified',
                'modified_by',
                'scope',
                # 'role_divisions',
                'state',
                # 'date_to_delete',
                # 'role_ids'
                ]
        
    with open('OAuth.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)

    print('Cabeçalho CSV foi escrito com sucesso.')

# execute function of header
write_csv_header()

# function of write the body
def write_csv_data(api_response): 

    data = json.loads(api_response)
    oAuths = data['entities']

    with open('OAuth.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        for oAuth in oAuths:
            id = oAuth['id'] if 'id' in oAuth else ' '
            name = oAuth['name'] if 'name' in oAuth else ' '
            access_token_validity_seconds = oAuth['access_token_validity_seconds'] if 'access_token_validity_seconds' in oAuth else ' '
            description = oAuth['description'] if 'description' in oAuth else ' '
            registered_redirect_uri = ', '.join([registered_redirect_uri for registered_redirect_uri in oAuth['registered_redirect_uri']]) if 'registered_redirect_uri' in oAuth else ' '
            secret = oAuth['secret'] if 'secret' in oAuth else ' '
            date_created = oAuth['date_created'] if 'date_created' in oAuth else ' '
            created_by = oAuth['created_by']['id'] if 'created_by' in oAuth else ' '
            date_modified = oAuth['date_modified'] if 'date_modified' in oAuth else ' '
            modified_by = oAuth['modified_by']['id'] if 'modified_by' in oAuth else ' '
            scope = ', '.join([scope for scope in oAuth['scope']]) if oAuth['scope'] else ' '
            # role_divisions = oAuth['role_divisions'] if 'role_divisions' in oAuth else ' '
            state = oAuth['state'] if 'state' in oAuth else 'no state'
            # date_to_delete = oAuth['date_to_delete'] if oAuth['date_to_delete'] else ' '
            # role_ids = ', '.join([role_ids for role_ids in oAuth['role_ids']]) if 'role_ids' in oAuth else ' '

            writer.writerow([id,
                              name,
                              access_token_validity_seconds,
                              description,
                              registered_redirect_uri,
                              secret,
                              date_created,
                              created_by,
                              date_modified,
                              modified_by,
                              scope,
                            #   role_divisions,
                              state,
                            #   date_to_delete,
                            #   role_ids
                              ])

    print('Dados CSV foram escritos com sucesso.')


# call the function
write_csv_data(api_response)