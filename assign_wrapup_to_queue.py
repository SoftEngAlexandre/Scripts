import os
import csv
import json
import time
import datetime
import logging
import requests
from dotenv import load_dotenv

# ========================================================== #
# ===================== CONFIGURAÇÃO ======================== #
# ========================================================== #

# Caminho do arquivo .env
env_file = r'C:\Users\alexandre.ferreira\Desktop\Code\ENV\.env'
load_dotenv(env_file)

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
ENVIRONMENT = os.getenv('ENVIRONMENT')  # ex: sae1.pure.cloud
CUSTOMER = os.getenv('CUSTOMER')

# ========================================================== #
# ======================= LOGGING =========================== #
# ========================================================== #

data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
nome_arquivo_log = fr"C:\Users\alexandre.ferreira\Desktop\Python_v2\logs\{data_atual}_Queues.log"
os.makedirs(os.path.dirname(nome_arquivo_log), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    filename=nome_arquivo_log,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ========================================================== #
# =================== OBTÉM TOKEN =========================== #
# ========================================================== #
def get_access_token():
    """
    Obtém o token de acesso do Genesys Cloud usando client credentials.
    Usa application/x-www-form-urlencoded (correto para o endpoint OAuth).
    """
    url = f"https://login.{ENVIRONMENT}/oauth/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    response = requests.post(url, data=payload)
    if response.status_code != 200:
        logging.error(f"Erro ao obter token: {response.status_code} - {response.text}")
        raise Exception("Falha na autenticação com o Genesys Cloud")

    token = response.json().get("access_token")
    if not token:
        raise Exception("Token não encontrado na resposta da API")

    logging.info("Token obtido com sucesso.")
    return token

# ========================================================== #
# ================== POST DE WRAPUPS ======================== #
# ========================================================== #
def create_wrapup_codes(queue_id, wrapup_codes, headers):
    api_url = f"https://api.{ENVIRONMENT}/api/v2/routing/queues/{queue_id}/wrapupcodes"
    response = requests.post(api_url, headers=headers, json=wrapup_codes)
    return response

# ========================================================== #
# ======================== MAIN ============================= #
# ========================================================== #
def main():
    logging.info("Iniciando execução do script POST de wrap-ups...")
    access_token = get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Caminhos dos arquivos CSV
    queues_csv_path = r"C:\Users\alexandre.ferreira\Desktop\Code\queue_finalizacao.csv"
    wrapups_csv_path = r"C:\Users\alexandre.ferreira\Desktop\Code\wrapup_dm.csv"


    # Carrega os wrap-ups
    wrapup_codes_list = []
    with open(wrapups_csv_path, 'r', encoding='utf-8') as file:
        for row in csv.DictReader(file):
            wrapup_codes_list.append({"id": row["id"]})

    if not wrapup_codes_list:
        print("Nenhum wrap-up encontrado no CSV.")
        logging.warning("Nenhum wrap-up encontrado no CSV.")
        return

    # Lê as filas e envia os wrap-ups
    with open(queues_csv_path, 'r', encoding='utf-8') as file:
        for row in csv.DictReader(file):
            queue_id = row["queue_id"]
            print(f"\nEnviando wrap-ups para a fila: {queue_id}...")
            logging.info(f"Iniciando envio de wrap-ups para a fila: {queue_id}")

            for i in range(0, len(wrapup_codes_list), 10):  # lotes de 10 wrapups
                batch = wrapup_codes_list[i:i+10]
                response = create_wrapup_codes(queue_id, batch, headers)

                if response.status_code == 200:
                    print(f"Lote {i//10 + 1} enviado com sucesso! ({len(batch)} wrap-ups)")
                    logging.info(f"Fila {queue_id} - Lote {i//10 + 1} enviado com sucesso.")
                else:
                    print(f"Erro no lote {i//10 + 1}: {response.status_code} - {response.reason}")
                    logging.error(f"Erro na fila {queue_id} - Lote {i//10 + 1}: {response.status_code} - {response.text}")

                time.sleep(0)  # pausa de 2 segundos entre lotes

    print("\nProcesso concluído com sucesso.")
    logging.info("Processo concluído com sucesso.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception(f"Erro durante a execução: {e}")
        print(f"Erro: {e}")
