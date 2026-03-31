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
nome_arquivo_log = fr"C:\Users\alexandre.ferreira\Desktop\Code\LOGS\{data_atual}_Groups.log"

# Obter o diretório da pasta
diretorio = os.path.dirname(nome_arquivo_log)

# Criar o diretório, se não existir
os.makedirs(diretorio, exist_ok=True)


# Configurar o logging
logging.basicConfig(level=logging.INFO, filename=nome_arquivo_log, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info('---------------Iniciando Script---------------')

logging.info('---------------------------------')
logging.info('- Genesys Cloud Python Client SDK')
logging.info('---------------------------------')

# Diretorio para arquivo .env
env_file = r'C:\Users\alexandre.ferreira\Desktop\Code\ENV\.env'
# Diretório para salvar export .csv
output_directory = r'C:\Users\alexandre.ferreira\Desktop\Code\GET\Folder'

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
    logging.info('Proxy definido com sucesso')
else:
    response = requests.post(auth_url, data=request_body, headers=request_headers)
    logging.error(response)
# token = response.text.split()
# Check response
if response.status_code == 200:
    logging.info('TOKEN com SUCESSO!')
    logging.info(f'TOKEN: {response.text[1:104]}')
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
# ----------------- ALTERAÇÕES PARA O GET ------------------ #
# ---------------------------------------------------------- #
 
 
group_id = "5bfce8f1-fc41-4900-ad24-84e96dc80ad7"  # <-- Substituir pelo ID real
 
# Parâmetros
api_url = f'https://api.{ENVIRONMENT}'
api_get = f'{api_url}/api/v2/groups/{group_id}/members'  # ALTERAR URL DO GET
pageNumber = 1
pageSize = 100
filename = 'Usuarios_Grupo'  # Nome do arquivo (ajustado para grupo)
 
print(f'URL UTILIZADA: {api_get}')
 
 
 
# GERAR JSON retorno para entendimento do mapeamento
def jsonReturn(pageSize):
    url_get = f'{api_get}?pageNumber={pageNumber}&pageSize={pageSize}'
    if proxy == 's':
        response = requests.get(url_get, headers=requestHeaders, proxies=proxies)
    else:
        response = requests.get(url_get, headers=requestHeaders)
   
    data = response.json()
    with open('ExportJSON.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    print('JSON gerado com sucesso')
    print(response)
 
jsonReturn(pageSize=5)  # Inativar quando não precisar do JSON
 
# Função para escrever o cabeçalho
def write_header():
    headers = ["ID_Group",'ID', 'Nome', 'Email']
    with open(fr'{output_directory}/{data_atual}_{CUSTOMER}_{filename}.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
    print('Cabeçalho CSV foi escrito com SUCESSO!')
 
write_header()
 
def get_api(pageNumber):
    url_get = f'{api_get}?pageNumber={pageNumber}&pageSize={pageSize}'
   
    if proxy == 's':
        response = requests.get(url_get, headers=requestHeaders, proxies=proxies)
    else:
        response = requests.get(url_get, headers=requestHeaders)
 
    if response.status_code == 200:
        data = response.json()
        number_of_pages = data["pageCount"]
        entities = data['entities']
 
        with open(fr'{output_directory}/{data_atual}_{CUSTOMER}_{filename}.csv', 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
 
            for user in entities:
                get_user_group = group_id
                get_user_id = user.get('id', '')
                get_user_name = user.get('name', '')
                get_user_email = user.get('email', '')
 
                writer.writerow([get_user_group, get_user_id, get_user_name, get_user_email])
 
        print(f'Dados CSV da página {pageNumber} foram escritos com SUCESSO.')
 
        if number_of_pages > pageNumber:
            next_page = pageNumber + 1
            get_api(next_page)
    else:
        logging.error(f'Failure: {str(response.status_code)} - {response.reason}')
        sys.exit(response.status_code)
 
get_api(pageNumber)
 
print('Arquivo Salvo')