import os
import base64
import requests
import pandas as pd
from dotenv import load_dotenv

# Carregar variáveis do .env
env_file = r'C:\Users\alexandre.ferreira\Desktop\Code\ENV\.env'
load_dotenv(env_file)

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
ENVIRONMENT = os.getenv('ENVIRONMENT')  # ex: mypurecloud.com.br

# Autenticação com Client Credentials
auth_url = f'https://login.{ENVIRONMENT}/oauth/token'
auth_headers = {
    'Authorization': 'Basic ' + base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode(),
    'Content-Type': 'application/x-www-form-urlencoded'
}
auth_data = {'grant_type': 'client_credentials'}

auth_response = requests.post(auth_url, headers=auth_headers, data=auth_data)
auth_response.raise_for_status()
access_token = auth_response.json()['access_token']

# Cabeçalhos para chamadas à API do Genesys Cloud
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# Leitura da planilha com filas
df_filas = pd.read_csv(r'C:\Users\alexandre.ferreira\Desktop\Code\DELETE\delete_queues.csv')
wrapup_results = []

# Para cada fila, buscar wrap-up codes paginando resultados
for idx, row in df_filas.iterrows():
    queue_id = row['id']
    page = 1
    page_size = 100  # Máximo suportado

    print(f"Buscando wrap-ups da fila {queue_id}...")

    while True:
        url = f'https://api.{ENVIRONMENT}/api/v2/routing/queues/{queue_id}/wrapupcodes?pageSize={page_size}&pageNumber={page}'
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            entities = data.get('entities', [])

            if not entities:
                break  # Nenhum resultado, fim da paginação

            for wrapup in entities:
                wrapup_results.append({
                    'queue_id': queue_id,
                    'wrapup_code_id': wrapup['id'],
                    'wrapup_code_name': wrapup['name']
                })

            if len(entities) < page_size:
                break  # Última página
            page += 1

        except requests.RequestException as e:
            print(f"Erro na fila {queue_id}: {e}")
            wrapup_results.append({
                'queue_id': queue_id,
                'wrapup_code_id': None,
                'wrapup_code_name': f"Erro: {str(e)}"
            })
            break  # Evita loop infinito em caso de erro

# Salvar em CSV
saida = r'C:\Users\alexandre.ferreira\Desktop\Code\TRIGG\EXPORT\wrapup_queue.csv'
os.makedirs(os.path.dirname(saida), exist_ok=True)  # Garante que o diretório exista
pd.DataFrame(wrapup_results).to_csv(saida, index=False, encoding='utf-8-sig')
print(f"Arquivo gerado: {saida}")
