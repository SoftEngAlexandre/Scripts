import base64
import pandas as pd
import requests
import sys
import os
import csv
from dotenv import load_dotenv
import json
import datetime
import logging


data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
nome_arquivo_log = r"C:\Users\alexandre.ferreira\Desktop\ARQUIVOS\Python_v2\export\autoanswer_usuarios.log"
diretorio = os.path.dirname(nome_arquivo_log)
os.makedirs(diretorio, exist_ok=True)

logging.basicConfig(level=logging.INFO, filename=nome_arquivo_log, format="%(asctime)s - %(levelname)s - %(message)s")
print('--------------- Iniciando Script Auto Answer ---------------')


env_file = r'C:\Users\alexandre.ferreira\Desktop\Scripts\.env'
load_dotenv(env_file)

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
ENVIRONMENT = os.getenv('ENVIRONMENT')
CUSTOMER = os.getenv('CUSTOMER')


authorization = base64.b64encode(bytes(CLIENT_ID + ':' + CLIENT_SECRET, 'ISO-8859-1')).decode('ascii')
auth_url = f'https://login.{ENVIRONMENT}/oauth/token'
request_body = {'grant_type': 'client_credentials'}
request_headers = {
    'Authorization': f'Basic {authorization}',
    'Content-Type': 'application/x-www-form-urlencoded'
}


proxies = {
    'http': 'http://10.104.244.30:8080',
    'https': 'http://10.104.244.30:8080',
}
proxy = 'n'  


if proxy == 's':
    response = requests.post(auth_url, data=request_body, headers=request_headers, proxies=proxies)
    print('Proxy definido com sucesso')
else:
    response = requests.post(auth_url, data=request_body, headers=request_headers)

if response.status_code == 200:
    print('TOKEN com SUCESSO!')
else:
    logging.error(f'Failure: {response.status_code} - {response.reason}')
    sys.exit(response.status_code)

response_json = response.json()
requestHeaders = {
    'Authorization': f"{response_json['token_type']} {response_json['access_token']}",
    'Content-Type': 'application/json'
}


csv_path = r"C:\Users\alexandre.ferreira\Desktop\Scripts\user_id.csv"


auto_answer_body = {
    "settings": {
        "callback": {"enabled": True},
        "sms": {"enabled": True},
        "whatsapp": {"enabled": True},
        "facebook": {"enabled": True},
        "instagram": {"enabled": True},
        "twitter": {"enabled": True},
        "webMessaging": {"enabled": True},
        "open": {"enabled": True}
    }
}


def aplicar_auto_answer(user_id):
    url = f"https://api.{ENVIRONMENT}/api/v2/users/agentui/agents/autoanswer/{user_id}/settings"
    if proxy == 's':
        return requests.put(url, headers=requestHeaders, json=auto_answer_body, proxies=proxies)
    else:
        return requests.put(url, headers=requestHeaders, json=auto_answer_body)


with open(csv_path, 'r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        user_id = row["user_id"]
        print(f"Aplicando Auto Answer para o usuário {user_id}...")
        resposta = aplicar_auto_answer(user_id)
        
        if resposta.status_code in [200, 204]:
            print(f"Auto Answer aplicado com sucesso para {user_id}.")
            logging.info(f"Auto Answer aplicado com sucesso para o usuário {user_id}.")
        else:
            print(f"Erro ao aplicar Auto Answer para {user_id}: {resposta.status_code} - {resposta.text}")
            logging.error(f"Erro ao aplicar Auto Answer para {user_id}: {resposta.status_code} - {resposta.text}")

print("Processo concluído.")
 