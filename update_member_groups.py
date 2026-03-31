import base64
import requests
import sys
import os
import csv
from dotenv import load_dotenv
 
print('-----------------------------------')
print('- Adicionar membros ao grupo - POST')
print('-----------------------------------')
 
# ===== CONFIGURAÇÃO =====
env_file = r'C:\Users\alexandre.ferreira\Desktop\Code\ENV\.env'
csv_path = r'C:\Users\alexandre.ferreira\Desktop\Code\members.csv'  # CSV com coluna: memberId
group_id = '767a36c7-c50b-488f-8823-59907d99e75c' # ID do grupo
BATCH_SIZE = 50
# ========================
 
# Carrega variáveis de ambiente
load_dotenv(env_file)
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
ENVIRONMENT = os.getenv('ENVIRONMENT')
 
if not CLIENT_ID or not CLIENT_SECRET or not ENVIRONMENT:
    print('Erro: Verifique se CLIENT_ID, CLIENT_SECRET e ENVIRONMENT estão no .env')
    sys.exit(1)
 
# Autenticação
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
 
# Lê o CSV
member_ids = []
with open(csv_path, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        if row['memberId']:
            member_ids.append(row['memberId'])
 
if not member_ids:
    print('Nenhum memberId encontrado no CSV!')
    sys.exit(1)
 
print(f"Total de IDs encontrados: {len(member_ids)}")
post_url = f'https://api.{ENVIRONMENT}/api/v2/groups/{group_id}/members'
 
# Função para dividir em lotes
def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]
 
# Envia os lotes
total_sucesso = 0
for i, batch in enumerate(chunk_list(member_ids, BATCH_SIZE), start=1):
    body = {"memberIds": batch}
    response = requests.post(post_url, headers=request_headers, json=body)
    if response.status_code in [200, 202, 204]:
        print(f"✅ Lote {i}: {len(batch)} membros adicionados com sucesso.")
        total_sucesso += len(batch)
    else:
        print(f"❌ Erro no lote {i}: {response.status_code} - {response.text}")
 
print(f"\nProcesso concluído. Total adicionados: {total_sucesso}")