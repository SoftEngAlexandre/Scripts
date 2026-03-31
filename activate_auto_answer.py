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
 
# -- Início dos logs
data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
nome_arquivo_log = r"C:\Users\nieli.bezerra\Desktop\script\Resultados\Geral.log"
diretorio = os.path.dirname(nome_arquivo_log)
os.makedirs(diretorio, exist_ok=True)
 
logging.basicConfig(level=logging.INFO, filename=nome_arquivo_log, format="%(asctime)s - %(levelname)s - %(message)s")
print('--------------- Iniciando Script Auto Answer ---------------')
 
# Carregar variáveis de ambiente
env_file = r'C:\Users\nieli.bezerra\Desktop\script\S4M_clientes\ENV.env'
load_dotenv(env_file)
 
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
ENVIRONMENT = os.getenv('ENVIRONMENT')
 
# Autenticação (Client Credentials)
authorization = base64.b64encode(bytes(CLIENT_ID + ':' + CLIENT_SECRET, 'ISO-8859-1')).decode('ascii')
auth_url = f'https://login.{ENVIRONMENT}/oauth/token'
request_body = {'grant_type': 'client_credentials'}
request_headers = {
    'Authorization': f'Basic {authorization}',
    'Content-Type': 'application/x-www-form-urlencoded'
}
 
# Proxy
proxies = {
    'http': 'http://10.104.244.30:8080',
    'https': 'http://10.104.244.30:8080',
}
proxy = 'n'  # 's' para usar proxy
 
# Obter token
if proxy == 's':
    response = requests.post(auth_url, data=request_body, headers=request_headers, proxies=proxies)
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
 
csv_path = r"C:\Users\nieli.bezerra\Desktop\script\Resultados\acertonline.csv"
 
# ------------ LER TODOS OS USER IDs -------------
user_ids = []
 
with open(csv_path, 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        user_ids.append(row["user_id"])
 
print(f"Total de IDs carregados: {len(user_ids)}")
logging.info(f"Total de IDs carregados: {len(user_ids)}")
 
# ------------ AUTOANSWER DE VOZ (PRIMEIRO) -------------
def aplicar_auto_answer_voz(lote):
    url = f"https://api.{ENVIRONMENT}/api/v2/users/bulk"
    payload = [{"id": uid, "acdAutoAnswer": True} for uid in lote]
 
    if proxy == 's':
        return requests.patch(url, headers=requestHeaders, json=payload, proxies=proxies)
    else:
        return requests.patch(url, headers=requestHeaders, json=payload)
 
print("\n=========== APLICANDO AUTOANSWER DE VOZ ===========")
 
for i in range(0, len(user_ids), 50):
    batch = user_ids[i:i+50]
    print(f"Processando lote VOZ ({len(batch)} IDs)...")
 
    resp = aplicar_auto_answer_voz(batch)
 
    if resp.status_code in [200, 204]:
        print(f"Lote VOZ aplicado com sucesso.")
        logging.info(f"AutoAnswer VOZ OK - Lote: {batch}")
    else:
        print(f"Erro no lote VOZ: {resp.status_code} - {resp.text}")
        logging.error(f"Erro AutoAnswer VOZ - {resp.status_code} - {resp.text}")
 
print("AutoAnswer de VOZ concluído!\n")
 
 
# ------------ AUTOANSWER DIGITAL (DEPOIS) -------------
auto_answer_body = {
    "settings": {
        "email": {"enabled": True},
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
 
def aplicar_auto_answer_digital(user_id):
    url = f"https://api.{ENVIRONMENT}/api/v2/users/agentui/agents/autoanswer/{user_id}/settings"
    if proxy == 's':
        return requests.put(url, headers=requestHeaders, json=auto_answer_body, proxies=proxies)
    else:
        return requests.put(url, headers=requestHeaders, json=auto_answer_body)
 
print("=========== APLICANDO AUTOANSWER DIGITAL ===========")
 
for user_id in user_ids:
    print(f"Aplicando AutoAnswer Digital para {user_id}...")
    resp = aplicar_auto_answer_digital(user_id)
 
    if resp.status_code in [200, 204]:
        print(f"Digital OK - {user_id}")
        logging.info(f"AutoAnswer Digital OK - {user_id}")
    else:
        print(f"Erro Digital - {user_id}: {resp.status_code} - {resp.text}")
        logging.error(f"Erro Digital {user_id}: {resp.status_code} - {resp.text}")
 
print("\nProcesso concluído com sucesso!")