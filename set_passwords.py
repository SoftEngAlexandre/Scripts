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
nome_arquivo_log = fr"export\{data_atual}_Queues.log"
 
# Obter o diretório da pasta
diretorio = os.path.dirname(nome_arquivo_log)
 
# Criar o diretório, se não existir
os.makedirs(diretorio, exist_ok=True)
 
 
# Configurar o logging
logging.basicConfig(level=logging.INFO, filename=nome_arquivo_log, format="%(asctime)s - %(levelname)s - %(message)s")
print('---------------Iniciando Script---------------')
 
print('---------------------------------')
print('- Genesys Cloud Python Client SDK')
print('---------------------------------')
 
# Diretorio para arquivo .env
env_file = r'C:\Users\alexandre.ferreira\Desktop\Code\ENV\.env'
# Diretório para salvar export .csv
output_directory = r'C:\Users\alexandre.ferreira\Desktop\Scripts\export'
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
 
 
requestHeaders = {
    'Authorization': f"{ response_json['token_type'] } { response_json['access_token']}"
}
 
# ---------------------------------------------------------- #
# ---------------  ALTERACOES PARA O POST  ----------------- #
# ---------------------------------------------------------- #
 
'''POST para atualizar as senhas dos usuários, faça um GET users
para pegar os id's e colocar no arquivo'''
 
# No arquivo postPassword.csv coloque os IDs dos usuários que deseja desconectar, um ID por linha
# Coloque o lugar onde o arquivo csv está:
input_directory = r'C:\Users\alexandre.ferreira\Desktop\Code\xxxxuser_password.csv'
 
# Define a função para realizar o POST
def post_password(user_id):
    api_url = f'https://api.{ENVIRONMENT}/api/v2/users/{user_id}/password'  # Endpoint de delete
   
    # Coloque a senha padrão para os usuários do csv:
    new_password = "Mud@r123"
 
    # Corpo da requisição
    payload = {"newPassword": new_password}
 
    post_response = requests.post(api_url, headers=requestHeaders, json=payload)
    return post_response
 
 
with open(input_directory, 'r', encoding='utf-8') as file:
   
    for line in file:
        user_id = line.strip()  # Remove espaços em branco e quebras de linha
 
        post_response = post_password(user_id)
       
        # Verificar a resposta para cada POST
        if post_response.status_code == 204:
            print(f'POST para: {user_id} com SUCESSO!')
        else:
            print(f'Falha no POST para: {user_id}: {post_response.status_code} - {post_response.reason}')
            print(post_response.json())
 
print("Todos os POSTs concluídos.")