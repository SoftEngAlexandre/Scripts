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

print('---------------Iniciando Script---------------')
 
print('---------------------------------')
print('- Genesys Cloud Python Client SDK')
print('---------------------------------')
 
# Diretorio para arquivo .env
env_file = r'C:\Users\alexandre.ferreira\Desktop\Code\ENV\.env'
# Diretório para salvar export .csv
output_directory = r'C:\Users\alexandre.ferreira\Desktop\Code\LOCAL\LOGS'
# Carregar as credenciais do arquivo .env
load_dotenv(env_file)
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
ENVIRONMENT = os.getenv('ENVIRONMENT')
CUSTOMER = os.getenv('CUSTOMER')
 
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
proxy = 'n'
# def funProxy():
#     if proxy == 's':
#         return proxies
#     else:
#         return None
 
# Get token
if proxy == 's':
    response = requests.post(auth_url, data=request_body, headers=request_headers, proxies=proxies)
    print('Proxy definido com sucesso')
else:
    response = requests.post(auth_url, data=request_body, headers=request_headers)
    logging.error(response)
# token = response.text.split()
# Check response
if response.status_code == 200:
    print('TOKEN com SUCESSO!')
    print(f'TOKEN: {response.text[1:104]}')
else:
    logging.error(f'Failure: { str(response.status_code) } - { response.reason }')
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
 
api_url = f'https://api.{ENVIRONMENT}'
agent_ids_file = r'C:\Users\alexandre.ferreira\Desktop\Code\xxUser_deleted.csv'
 
 
# Função para carregar os agent IDs do CSV
def carregar_agentes(filename):
    agent_ids = []
    with open(filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            agent_id = row['agent_id'].strip()  # capturando os valores da coluna "agent_id"
            if agent_id:
                agent_ids.append(agent_id)
    return agent_ids
 
agent_ids = carregar_agentes(agent_ids_file)
 
if not agent_ids:
    print("Nenhum agent_id encontrado no arquivo.")
    sys.exit(1)
 
# Iterar sobre cada agent_id e enviar PATCH individual
for agent_id in agent_ids:
    endpoint = f'{api_url}/api/v2/users/{agent_id}'
 
    if proxy == 's':
        response = requests.delete(endpoint, headers=requestHeaders, proxies=proxies)
    else:
        response = requests.delete(endpoint, headers=requestHeaders)
 
    if response.status_code == 200:
        print(f"Agente deletado com sucesso {agent_id}.")
    else:
        print(f"Erro ao deletar agente {agent_id}: {response.status_code} - {response.reason}")
        try:
            print("Detalhes do erro:", json.dumps(response.json(), indent=2, ensure_ascii=False))
        except ValueError:
            print("Resposta não é um JSON válido.")
 
print("Processo de atualização concluído.")
 