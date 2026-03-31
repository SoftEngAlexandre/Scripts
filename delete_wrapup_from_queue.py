import base64
import requests
import sys
import os
import csv
from dotenv import load_dotenv
import json
import datetime
import logging


data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
nome_arquivo_log = rf"C:\Users\alexandre.ferreira\Desktop\Python_v2\log_remocao_{data_atual}.log"
diretorio = os.path.dirname(nome_arquivo_log)
os.makedirs(diretorio, exist_ok=True)
logging.basicConfig(level=logging.INFO, filename=nome_arquivo_log, format="%(asctime)s - %(levelname)s - %(message)s")



env_file = r'C:\Users\alexandre.ferreira\Desktop\Code\ENV\.env'
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
else:
    response = requests.post(auth_url, data=request_body, headers=request_headers)

if response.status_code == 200:
    print('TOKEN com SUCESSO!')
else:
    logging.error(f'Falha na autenticação: {response.status_code} - {response.reason}')
    sys.exit(response.status_code)

token_json = response.json()
requestHeaders = {
    'Authorization': f"{token_json['token_type']} {token_json['access_token']}"
}

def delete_wrapup_code(queue_id, wrapup_code_id):
    url = f"https://api.{ENVIRONMENT}/api/v2/routing/queues/{queue_id}/wrapupcodes/{wrapup_code_id}"
    if proxy == 's':
        response = requests.delete(url, headers=requestHeaders, proxies=proxies)
    else:
        response = requests.delete(url, headers=requestHeaders)
    
    if response.status_code == 204:
        print(f"Wrap-up code {wrapup_code_id} removido da fila {queue_id}.")
    else:
        print(f"Erro ao remover {wrapup_code_id} da fila {queue_id}: {response.status_code} - {response.reason}")
        try:
            logging.error(response.json())
        except ValueError:
            logging.error(f"Resposta não é JSON. Status: {response.status_code} | Conteúdo: {response.text}")

queues_csv_path = r"C:\Users\alexandre.ferreira\Desktop\Code\queue_finalizacao.csv"

wrapups_csv_path = r"C:\Users\alexandre.ferreira\Desktop\Code\wrapup_dm.csv"

wrapup_codes = []
with open(wrapups_csv_path, 'r', encoding='utf-8') as wrap_file:
    reader = csv.DictReader(wrap_file)
    for row in reader:
        wrapup_codes.append(row["id"])

with open(queues_csv_path, 'r', encoding='utf-8') as queue_file:
    reader = csv.DictReader(queue_file)
    for row in reader:
        queue_id = row["id"]

        for wrap_id in wrapup_codes:
            delete_wrapup_code(queue_id, wrap_id)

print(f"Processo concluido com sucesso, caminho do wrapup -> {wrapups_csv_path}")