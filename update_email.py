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
from time import sleep

# -- Início dos logs
data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
nome_arquivo_log = r"C:\Users\alexandre.ferreira\Desktop\ARQUIVOS\Python_v2\export\atualiza_emails.log"
diretorio = os.path.dirname(nome_arquivo_log)
os.makedirs(diretorio, exist_ok=True)

logging.basicConfig(level=logging.INFO, filename=nome_arquivo_log, format="%(asctime)s - %(levelname)s - %(message)s")


# Carregar variáveis de ambiente
env_file = r'C:\Users\alexandre.ferreira\Desktop\Scripts\.env'
load_dotenv(env_file)
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
ENVIRONMENT = os.getenv('ENVIRONMENT')
CUSTOMER = os.getenv('CUSTOMER')

# Obter token
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
    logging.error(f'Erro ao obter token: {response.status_code} - {response.reason}')
    sys.exit(response.status_code)

response_json = response.json()
requestHeaders = {
    'Authorization': f"{response_json['token_type']} {response_json['access_token']}",
    'Content-Type': 'application/json'
}


usuarios_csv = r"C:\Users\alexandre.ferreira\Desktop\Scripts\zemail.csv"

def atualizar_email(user_id, novo_email):
    url = f"https://api.{ENVIRONMENT}/api/v2/users/{user_id}"
    payload = {'email': novo_email}

    try:
        if proxy == 's':
            response = requests.patch(url, headers=requestHeaders, json=payload, proxies=proxies)
        else:
            response = requests.patch(url, headers=requestHeaders, json=payload)

        if response.status_code == 200:
            logging.info(f"E-mail atualizado com sucesso: {user_id} -> {novo_email}")
            print(f"✔ Sucesso: {user_id}")
        else:
            logging.error(f"Erro ao atualizar {user_id} ({novo_email}): {response.status_code} - {response.text}")
            print(f"✖ Erro: {user_id} - {response.status_code}")

    except Exception as e:
        logging.error(f"Erro inesperado ao atualizar {user_id}: {str(e)}")


try:
    with open(usuarios_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            user_id = row['userId'].strip()
            novo_email = row['newEmail'].strip()
            if user_id and novo_email:
                atualizar_email(user_id, novo_email)
                sleep(0.3)
            else:
                logging.warning(f"Linha inválida no CSV: {row}")
except Exception as e:
    logging.error(f"Erro ao ler arquivo CSV: {str(e)}")
    sys.exit(1)

print("Processo concluído.")
