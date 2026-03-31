import base64
import requests
import sys
import os
import csv
from dotenv import load_dotenv
import json
from datetime import datetime

print('---------------------------------')
print('- Genesys Cloud Python Client SDK')
print('---------------------------------')

# Diretorio para arquivo .env
env_file = r'C:\Users\alexandre.ferreira\Desktop\Code\PY\_env\.env'
# Diretório para salvar export .csv
output_directory = r'C:\Users\alexandre.ferreira\Desktop\Code\Users'

# Carregar as credenciais do arquivo .env
load_dotenv(env_file)
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
ENVIRONMENT = os.getenv('ENVIRONMENT')
CUSTOMER = os.getenv('CUSTOMER')
dataAtual = datetime.now().strftime('%Y%m%d')
filename = 'UsersByRoles' # Nome do arquivo
pageNumber = 1
all_users = []
# Base64 encode the client ID and client secret
authorization = base64.b64encode(bytes(CLIENT_ID + ':' + CLIENT_SECRET, 'ISO-8859-1')).decode('ascii')

# Prepara o POST /oauth/token request
auth_url = f'https://login.{ENVIRONMENT}/oauth/token'
request_body = {'grant_type': 'client_credentials'
}
request_headers = {
    'Authorization': f'Basic {authorization}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Define a configuração do proxy
proxies = {
    'http': 'http://10.104.244.30:8080',
    'https': 'http://10.104.244.30:8080',
}
# proxy = input('Usar proxy? (s/n): ')
proxy = 's'

# Get token
if proxy == 's':
    response = requests.post(auth_url, data=request_body, headers=request_headers, proxies=proxies)
    print('Proxy definido com sucesso')
    
else:
    response = requests.post(auth_url, data=request_body, headers=request_headers)

# Check response
if response.status_code == 200:
    print('TOKEN com SUCESSO!')
else:
    print(f'Failure: { str(response.status_code) } - { response.reason }')
    sys.exit(response.status_code)

# Get JSON response body
response_json = response.json()

# Prepara o GET /api/v2/authorization/roles request
requestHeaders = {
    'Authorization': f"{ response_json['token_type'] } { response_json['access_token']}"
}

# ---------------------------------------------------------- #
# ----------------- ALTERACOES PARA O GET ------------------ #
# ---------------------------------------------------------- #

# Parametros
role_id = '86f6e66c-7593-4ca2-82d0-1b7553d211b9'
pageSize=100
api_url = f'https://api.{ENVIRONMENT}'
api_get = f'{api_url}/api/v2/authorization/roles/{role_id}/users?pageSize={pageSize}' # ALTERAR URL DO GET
api_get_users = f'{api_url}/api/v2/locations'

# GERAR JSON retorno para entendimento do mapeamento
def jsonReturn(pageSize):
    url_get = f'{api_url}/api/v2/authorization/roles/{role_id}/users?pageSize={pageSize}' # ALTERAR URL DO GET
    if proxy == 's':
        response = requests.get(url_get, headers=requestHeaders, proxies=proxies)

    else:
        response = requests.get(url_get, headers=requestHeaders)
    
    data = response.json()
    with open('ExportJSON.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    print('JSON gerado com sucesso')

# jsonReturn(pageSize=5) # inativar quando não precisar do JSON

def write_header():
    headers = [
            '_id', 
            '_name',
            ]

    with open(f'{output_directory}/{CUSTOMER}_{filename}_{dataAtual}.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
    print('Cabeçalho CSV foi escrito com SUCESSO!')

def get_api(pageNumber):

    url_get = f'{api_url}/api/v2/authorization/roles/{role_id}/users?pageSize={pageSize}' # ALTERAR URL DO GET
    if proxy == 's':
        response = requests.get(url_get, headers=requestHeaders, proxies=proxies)

    else:
        response = requests.get(url_get, headers=requestHeaders)
    
    # Check response
    if response.status_code == 200:
        data = response.json()
        number_of_pages = data["pageCount"]
        entities = data['entities']

        with open(fr'{output_directory}/{dataAtual}_{CUSTOMER}_{filename}.csv', 'a', newline='', encoding='utf-8') as csvfile:

            for roles in entities:
                id = roles['id']
                all_users[roles] = id
                # all_users = ', '.join(all_users)
        print(f'Dados CSV da pagina {pageNumber} foram escritos com SUCESSO.')

        

    if number_of_pages > pageNumber:
        next_page = pageNumber + 1
        # Recursively call the function for the next page
        get_api(next_page)

# GET
def write_csv_data(all_users):
    with open(f'{output_directory}/{CUSTOMER}_{filename}_{dataAtual}.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        for user in all_users:
            get_id = user[1]
                
            writer.writerow(get_id)
            print('Dados do usuário foram escritos com sucesso.')

get_api(pageNumber)
write_header()
write_csv_data()