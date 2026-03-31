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
 
# --Inicio dos logs
# Obter a data atual
data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
 
# Definir o nome do arquivo de log
# nome_arquivo_log = fr"C:\Users\alexandre.ferreira\Desktop\code.send\{data_atual}_Queues.log"
 

#diretorio = os.path.dirname(nome_arquivo_log)
 

#os.makedirs(diretorio, exist_ok=True)
 
 
# Configurar o logging
#logging.basicConfig(level=logging.INFO, filename=nome_arquivo_log, format="%(asctime)s - %(levelname)s - %(message)s")
print('---------------Iniciando Script---------------')
 
print('---------------------------------')
print('- Genesys Cloud Python Client SDK')
print('---------------------------------')
 
# Diretorio para arquivo .env
env_file = r'C:\Users\alexandre.ferreira\Desktop\Code\ENV\.env'
# Diretório para salvar export .csv
output_directory = r'C:\Users\alexandre.ferreira\Desktop\Code\DMCARD\LOGS'
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
 
'''GET para capturar os id's e os nomes das wrap-ups da org'''
 
# Parametros
api_url = f'https://api.{ENVIRONMENT}'
api_wrapup = f'{api_url}/api/v2/routing/wrapupcodes'
pageNumber = 1
pageSize = 100
sortOrder = 'ascending'
wrapup_filename = 'WrapUps'
print(f'URL UTILIZADA: {api_wrapup}')
 
# GERAR JSON retorno para entendimento do mapeamento
def jsonReturn(pageSize):
    url_get = f'{api_wrapup}?pageNumber={pageNumber}&pageSize={pageSize}&sortOrder={sortOrder}'
    if proxy == 's':
        response = requests.get(url_get, headers=requestHeaders, proxies=proxies)
    else:
        response = requests.get(url_get, headers=requestHeaders)
 
    data = response.json()
    with open('ExportJSON.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    print('JSON gerado com sucesso')
    print(response)
 
jsonReturn(pageSize=5)  # inativar quando não precisar do JSON
 
# Função para buscar e salvar Wrap-Ups de todas as páginas
def get_wrapup_codes():
    current_page = 1
    with open(fr'{output_directory}/{data_atual}_{CUSTOMER}_{wrapup_filename}.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Wrap-Up ID', 'Wrap-Up Name'])  # Escreve o cabeçalho
 
        while True:
            url_get = f'{api_wrapup}?pageNumber={current_page}&pageSize={pageSize}&sortOrder={sortOrder}'
            response = requests.get(url_get, headers=requestHeaders, proxies=proxies if proxy == 's' else None)
            if response.status_code == 200:
                data = response.json()
                wrapups = data.get('entities', [])
 
                for wrapup in wrapups:
                    writer.writerow([wrapup.get('id', ''), wrapup.get('name', '')])
 
                print(f'Página {current_page} processada com SUCESSO!')
 
                # Verifica se há mais páginas
                if not data.get('nextUri'):
                    break
 
                current_page += 1
            else:
                print(f'Erro ao buscar Wrap-Ups na página {current_page}: {response.status_code} - {response.text}')
                break
 
# Executar script
get_wrapup_codes()
 
print(f'Arquivo de Wrap-Ups salvo com sucesso!, caminho -> {output_directory}')
