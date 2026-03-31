import os
import sys
import base64
import requests
import json
import datetime
import logging
import pandas as pd
from dotenv import load_dotenv
from time import sleep
import csv

# ------------------- CONFIGURAÇÃO DE LOGS ------------------- #
data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
nome_arquivo_log = r"C:\Users\alexandre.ferreira\Desktop\Code\DELETE\add_skills.log"
os.makedirs(os.path.dirname(nome_arquivo_log), exist_ok=True)

logging.basicConfig(level=logging.INFO, filename=nome_arquivo_log, format="%(asctime)s - %(levelname)s - %(message)s")
print('--------------- Iniciando Script ---------------')

# ------------------- CARREGAMENTO DO .ENV ------------------- #
env_file = r'C:\Users\alexandre.ferreira\Desktop\Code\ENV\.env'
load_dotenv(env_file)

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
ENVIRONMENT = os.getenv('ENVIRONMENT')
CUSTOMER = os.getenv('CUSTOMER')

if not all([CLIENT_ID, CLIENT_SECRET, ENVIRONMENT]):
    print("❌ Variáveis de ambiente ausentes. Verifique o .env")
    sys.exit(1)

# ------------------- AUTENTICAÇÃO ------------------- #
authorization = base64.b64encode(bytes(f"{CLIENT_ID}:{CLIENT_SECRET}", 'ISO-8859-1')).decode('ascii')
auth_url = f'https://login.{ENVIRONMENT}/oauth/token'
request_body = {'grant_type': 'client_credentials'}
request_headers = {'Authorization': f'Basic {authorization}', 'Content-Type': 'application/x-www-form-urlencoded'}

# Proxy opcional
proxies = {'http': 'http://10.104.244.30:8080', 'https': 'http://10.104.244.30:8080'}
proxy = 'n'  # 's' = usar proxy, 'n' = não usar proxy

if proxy == 's':
    response = requests.post(auth_url, data=request_body, headers=request_headers, proxies=proxies)
else:
    response = requests.post(auth_url, data=request_body, headers=request_headers)

if response.status_code != 200:
    print(f"❌ Falha ao obter token: {response.status_code} - {response.reason}")
    try:
        print(response.json())
    except:
        print(response.text)
    sys.exit(1)

token_data = response.json()
requestHeaders = {'Authorization': f"{token_data['token_type']} {token_data['access_token']}"}

# ------------------- LEITURA DO CSV DE SKILLS ------------------- #
csv_skills_path = r"C:\Users\alexandre.ferreira\Desktop\Code\DELETE\CSV\Assignar_Skills\skills.csv"
df_skills = pd.read_csv(csv_skills_path)
if "skill_id" not in df_skills.columns:
    print("❌ O CSV de skills não contém a coluna 'skill_id'")
    sys.exit(1)
fixed_skills = df_skills['skill_id'].dropna().astype(str).tolist()
print(f"✅ {len(fixed_skills)} skills carregadas do CSV")

# ------------------- LEITURA DO CSV DE USUÁRIOS ------------------- #
csv_users_path = r"C:\Users\alexandre.ferreira\Desktop\Code\DELETE\CSV\Assignar_Skills\users.csv"
user_ids = []
with open(csv_users_path, 'r', encoding='utf-8') as f:
    csv_reader = csv.DictReader(f)
    for row in csv_reader:
        user_ids.append(row['id'] if 'id' in row else row['user_id'])

if not user_ids:
    print("❌ Nenhum usuário encontrado no CSV")
    sys.exit(1)

print(f"✅ {len(user_ids)} usuários carregados do CSV")

# ------------------- FUNÇÃO USANDO A NOVA API ------------------- #
# Agora usando /api/v2/users/{userId}/routingskills/{skillId} (PUT)
def post_skill(user_id, skill_id, proficiency=4): ## define proeficiencia
    url = f"https://api.{ENVIRONMENT}/api/v2/users/{user_id}/routingskills"
    payload = {"id": skill_id, "proficiency": proficiency}
    if proxy == 's':
        resp = requests.post(url, headers=requestHeaders, json=payload, proxies=proxies)
    else:
        resp = requests.post(url, headers=requestHeaders, json=payload)
    return resp

# ------------------- FUNÇÃO PARA DIVIDIR EM BLOCO ------------------- #
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

# ------------------- PROCESSAR EM BLOCO ------------------- #
chunk_size = 1
for idx, user_chunk in enumerate(chunks(user_ids, chunk_size), start=1):
    print(f"\n📦 Processando bloco {idx} com {len(user_chunk)} usuários")
    for user_id in user_chunk:
        print(f"\nAdicionando skills para o usuário {user_id}")
        for skill_id in fixed_skills:
            response = post_skill(user_id, skill_id)
            if response.status_code in [200, 201, 204]:
                print(f"✓ Skill {skill_id} adicionada/atualizada com sucesso.")
                logging.info(f"Usuário {user_id}: Skill {skill_id} aplicada")
            else:
                print(f"✖ Erro ao adicionar skill {skill_id} para {user_id}.")
                try:
                    logging.error(f"{user_id} - {skill_id} - {response.text}")
                except:
                    logging.error(f"{user_id} - {skill_id}")
    sleep(1)

print("\nTodos os PUTs finalizados.")
