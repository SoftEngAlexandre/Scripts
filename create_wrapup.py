import base64
import requests
import sys
import os
import csv
import json
import datetime
import logging
from dotenv import load_dotenv

# -- Configuração de log
data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
nome_arquivo_log = fr"C:\Users\alexandre.ferreira\Desktop\Scripts\logs\wrapup\{data_atual}_WrapupCodes.log"
os.makedirs(os.path.dirname(nome_arquivo_log), exist_ok=True)
logging.basicConfig(level=logging.INFO, filename=nome_arquivo_log, format="%(asctime)s - %(levelname)s - %(message)s")

print('---------------Iniciando Script de Criação de Wrap-up Codes---------------')

# -- Carregar variáveis do .env
env_file = r'C:\Users\alexandre.ferreira\Desktop\Code\ENV\.env'
load_dotenv(env_file)
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
ENVIRONMENT = os.getenv('ENVIRONMENT')

# -- Autenticação com base64
authorization = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode('ISO-8859-1')).decode('ascii')
auth_url = f'https://login.{ENVIRONMENT}/oauth/token'
request_body = {'grant_type': 'client_credentials'}
request_headers = {
    'Authorization': f'Basic {authorization}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

# -- Solicitar token
response = requests.post(auth_url, data=request_body, headers=request_headers)
if response.status_code == 200:
    print('TOKEN gerado com sucesso!')
    response_json = response.json()
else:
    logging.error(f"Erro ao obter token: {response.status_code} - {response.text}")
    sys.exit(1)

# -- Cabeçalhos para requisições futuras
requestHeaders = {
    'Authorization': f"{response_json['token_type']} {response_json['access_token']}",
    'Content-Type': 'application/json'
}

# -- Endpoint de criação de wrap-up codes
api_url = f"https://api.{ENVIRONMENT}/api/v2/routing/wrapupcodes"

# -- Função para criar wrap-up code
def create_wrapup_code(wrapup_code):
    response = requests.post(api_url, headers=requestHeaders, json=wrapup_code)
    return response

# -- Caminho do CSV com os wrap-up codes
csv_path = r"C:\Users\alexandre.ferreira\Desktop\Code\POST\wrapup.csv"

# -- Lista para armazenar os wrap-up codes criados
wrapup_created = []

# -- Ler o CSV e criar os códigos
with open(csv_path, 'r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    
    for row in csv_reader:
        try:
            wrapup_code = {
                "name": row["name"].strip(),
                # Não enviar o campo division
            }

            post_response = create_wrapup_code(wrapup_code)

            # Logar a resposta completa da API para diagnosticar
            logging.info(f"Resposta da API para '{wrapup_code['name']}': {post_response.status_code} - {post_response.text}")
            
            if post_response.status_code == 201:
                msg = f"Wrap-up code '{wrapup_code['name']}' criado com sucesso!"
                print(msg)
                logging.info(msg)

                # Armazenando o nome e o ID do wrap-up code criado
                wrapup_created.append({
                    "name": wrapup_code["name"],
                    "id": post_response.json().get('id', 'ID não retornado')  # Garantir que o ID seja obtido
                })
            else:
                msg = f"Erro ao criar '{wrapup_code['name']}': {post_response.status_code} - {post_response.reason}"
                print(msg)
                logging.error(msg)
                logging.error(post_response.text)

        except KeyError as e:
            print(f"Erro: coluna faltando no CSV -> {e}")
            logging.error(f"Erro ao processar linha do CSV: coluna ausente -> {e}")
            continue

# Verificando se a lista wrapup_created foi preenchida corretamente
if wrapup_created:
    print(f"Total de wrap-ups criados: {len(wrapup_created)}")
    logging.info(f"Total de wrap-ups criados: {len(wrapup_created)}")

    # Caminho onde o CSV será salvo
    resultado_csv_path = r"C:\Users\alexandre.ferreira\Desktop\Code\LOCAL\LOGS\wrapups_criados_{data_atual}.csv"

    # Verificar se o diretório existe
    if not os.path.exists(os.path.dirname(resultado_csv_path)):
        os.makedirs(os.path.dirname(resultado_csv_path))

    try:
        # Abrir o arquivo CSV para gravação
        with open(resultado_csv_path, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.DictWriter(file, fieldnames=["name", "id"])
            writer.writeheader()
            for wrapup in wrapup_created:
                writer.writerow(wrapup)

        print(f"Processo concluído. Resultado salvo em: {resultado_csv_path}")
        logging.info(f"Processo concluído. Resultado salvo em: {resultado_csv_path}")
    
    except Exception as e:
        print(f"Erro ao salvar o arquivo CSV: {e}")
        logging.error(f"Erro ao salvar o arquivo CSV: {e}")
else:
    print("Nenhum wrap-up code foi criado.")
    logging.info("Nenhum wrap-up code foi criado.")
