import base64
import requests
import sys
import os
import csv
from dotenv import load_dotenv
import time

env_file = r'C:\Users\alexandre.ferreira\Desktop\Code\ENV\.env'
csv_path = r'C:\Users\alexandre.ferreira\Desktop\Code\DELETE\delete_groups.csv'  
group_id = 'xxxx' 
BATCH_SIZE = 50



load_dotenv(env_file)
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
ENVIRONMENT = os.getenv('ENVIRONMENT')

if not CLIENT_ID or not CLIENT_SECRET or not ENVIRONMENT:
    print('Erro: Verifique se CLIENT_ID, CLIENT_SECRET e ENVIRONMENT estão no .env')
    sys.exit(1)


authorization = base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode('ISO-8859-1')).decode('ascii')
auth_url = f'https://login.{ENVIRONMENT}/oauth/token'
auth_headers = {
    'Authorization': f'Basic {authorization}',
    'Content-Type': 'application/x-www-form-urlencoded'
}
auth_data = {'grant_type': 'client_credentials'}

auth_response = requests.post(auth_url, data=auth_data, headers=auth_headers)
if auth_response.status_code != 200:
    print(f'Erro ao obter token: {auth_response.status_code} - {auth_response.text}')
    sys.exit(1)

token = auth_response.json()['access_token']
request_headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

member_ids = []
with open(csv_path, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        member_id = row.get('memberId')
        if member_id:
            member_ids.append(member_id.strip())

if not member_ids:
    print('Nenhum memberId encontrado no CSV!')
    sys.exit(1)

print(f"Total de IDs encontrados: {len(member_ids)}")

base_url = f'https://api.{ENVIRONMENT}/api/v2/groups/{group_id}/members'

def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


total_sucesso = 0
for i, batch in enumerate(chunk_list(member_ids, BATCH_SIZE), start=1):
    ids_param = ','.join(batch)
    delete_url = f"{base_url}?ids={ids_param}"

    response = requests.delete(delete_url, headers=request_headers)

    if response.status_code in [200, 202, 204]:
        print(f" Lote {i}: {len(batch)} membros removidos com sucesso.")
        total_sucesso += len(batch)
    else:
        print(f" Lote {i}: {response.status_code} - {response.text}")

    time.sleep(0.2)

print(f"\nProcesso concluído. Total removidos: {total_sucesso}")
