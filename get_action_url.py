import base64
import requests
import sys
import os
import csv
from dotenv import load_dotenv
import json
import datetime
import logging
import shutil
 

data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
 

nome_arquivo_log = fr"C:\Users\alexandre.ferreira\Desktop\Python_v2\logs\{data_atual}_Queues.log"
 

diretorio = os.path.dirname(nome_arquivo_log)
 

os.makedirs(diretorio, exist_ok=True)
 
 

logging.basicConfig(level=logging.INFO, filename=nome_arquivo_log, format="%(asctime)s - %(levelname)s - %(message)s")


env_file = r'C:\Users\alexandre.ferreira\Desktop\Code\ENV\.env'

output_directory = r'C:\Users\alexandre.ferreira\Desktop\Code\EXPORT'

load_dotenv(env_file)
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
ENVIRONMENT = os.getenv('ENVIRONMENT')
CUSTOMER = os.getenv('CUSTOMER')
 

authorization = base64.b64encode(bytes(CLIENT_ID + ':' + CLIENT_SECRET, 'ISO-8859-1')).decode('ascii')
 
auth_url = f'https://login.{ENVIRONMENT}/oauth/token'
request_body = {'grant_type': 'client_credentials'
}
request_headers = {
    'Authorization': f'Basic {authorization}',
    'Content-Type': 'application/x-www-form-urlencoded'
}
 

proxies = {
    'http': 'http://10.104.244.30:8080',
    'https': 'http://10.104.244.30:8080',
}
# proxy = input('Usar proxy? (s/n): ')
proxy = 'n'
# def funProxy():
#     if proxy == 's':
#         return proxies
#     else:
#         return None
 

if proxy == 's':
    response = requests.post(auth_url, data=request_body, headers=request_headers, proxies=proxies)
    print('Proxy definido com sucesso')
else:
    response = requests.post(auth_url, data=request_body, headers=request_headers)
    logging.error(response)

if response.status_code == 200:
    print('TOKEN com SUCESSO!')
    print(f'TOKEN: {response.text[1:104]}')
else:
    logging.error(f'Failure: { str(response.status_code) } - { response.reason }')
    sys.exit(response.status_code)

response_json = response.json()
 

requestHeaders = {
    'Authorization': f"{ response_json['token_type'] } { response_json['access_token']}"
}
 

 
# Parâmetros
ENVIRONMENT = 'sae1.pure.cloud' 
api_url = f'https://api.{ENVIRONMENT}'
api_get = f'{api_url}/api/v2/integrations/actions' 
pageNumber = 1
pageSize = 100
sortOrder = 'ASC'  
filename = 'Actions' 
 

def write_header():
    headers = [
        'ID',
        'Nome',
        'Request URL Template',
        'Consuming Resource ID',
        'Consuming Resource Name',
        'Consuming Resource Version'
    ]
    with open(f'{output_directory}/{filename}_DependencyTracking.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
    print('Cabeçalho CSV foi escrito com sucesso!')
 
write_header()
 

def get_request_url_template(action_config_url):
    response = requests.get(action_config_url, headers=requestHeaders)
    if response.status_code == 200:
        data = response.json()
        return data.get('config', {}).get('request', {}).get('requestUrlTemplate', '')
    else:
        print(f'Erro ao buscar requestUrlTemplate: {response.status_code} - {response.text}')
        return ''
 

def get_dependencytracking(action_id, action_name, request_url_template):

    formatted_name = action_name.replace(' ', '%20')
 
  
    url_dependencytracking = (
        f'{api_url}/api/v2/architect/dependencytracking?pageNumber={pageNumber}'
        f'&pageSize={pageSize}&name={formatted_name}&objectType=DATAACTION'
        f'&consumedResources=true&consumingResources=true'
    )
    response = requests.get(url_dependencytracking, headers=requestHeaders)
 
    if response.status_code == 200:
        data = response.json()
        entities = data.get('entities', [])
 
        with open(f'{output_directory}/{filename}_DependencyTracking.csv', 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for entity in entities:
                for resource in entity.get('consumingResources', []):
                    writer.writerow([
                        action_id,
                        action_name,
                        request_url_template,
                        resource.get('id', ''),
                        resource.get('name', ''),
                        resource.get('version', '')
                    ])
        print(f'Dependency tracking para "{action_name}" foi adicionado ao CSV.')
    else:
        print(f'Erro ao buscar dependency tracking: {response.status_code} - {response.text}')
 
def get_api(pageNumber):
    url_get = f'{api_get}?pageNumber={pageNumber}&pageSize={pageSize}&sortOrder={sortOrder}'
    response = requests.get(url_get, headers=requestHeaders)
 
    if response.status_code == 200:
        data = response.json()
        entities = data.get('entities', [])
        number_of_pages = data.get('pageCount', 1)
 
  
        for action in entities:
            action_id = action['id']
            action_name = action['name']
            action_config_url = f'{api_url}/api/v2/integrations/actions/{action_id}?includeConfig=true'
            request_url_template = get_request_url_template(action_config_url)
 
       
            get_dependencytracking(action_id, action_name, request_url_template)
 
        print(f'Dados da página {pageNumber} foram processados com sucesso.')
 
       
        if pageNumber < number_of_pages:
            get_api(pageNumber + 1)
    else:
        print(f'Erro ao buscar ações: {response.status_code} - {response.text}')
 

get_api(pageNumber)
print('Processamento concluído! CSV gerado com sucesso.')
 