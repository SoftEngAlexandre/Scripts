import os
import csv
import time
import requests
import logging
from dotenv import load_dotenv

# Carrega ENV
load_dotenv(dotenv_path=r"C:\Users\alexandre.ferreira\Desktop\Code\ENV\.env")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ENVIRONMENT = os.getenv("ENVIRONMENT")  # ex: sae1.pure.cloud

QUEUES_CSV = r"C:\Users\alexandre.ferreira\Desktop\Code\TRIGG\LOGS\queue_canned.csv"
LIBS_CSV = r"C:\Users\alexandre.ferreira\Desktop\Code\canned.csv"

LOG_FILE = r"C:\Users\alexandre.ferreira\Desktop\Code\TRIGG\apply_canned_responses.log"

DELAY_BETWEEN_REQUESTS = 0.2  # segurança pra não pegar rate limit

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logging.getLogger().addHandler(logging.StreamHandler())


# =========================
# TOKEN
# =========================
def get_token():
    url = f"https://login.{ENVIRONMENT}/oauth/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    response = requests.post(url, headers=headers, data=data, timeout=15)
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        logging.info("Token obtido com sucesso.")
        return token

    logging.error(f"Erro ao autenticar: {response.status_code} - {response.text}")
    raise Exception("Falha na autenticação.")


# =========================
# CSVs
# =========================
def read_queues(csv_file):
    queues = []
    with open(csv_file, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            queue_id = row.get("queue_id")
            if queue_id:
                queues.append(queue_id.strip())
    logging.info(f"{len(queues)} filas lidas do arquivo CSV.")
    return queues


def read_libraries(csv_file):
    libs = []
    with open(csv_file, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            lib_id = row.get("library_id")
            if lib_id:
                libs.append(lib_id.strip())
    logging.info(f"{len(libs)} bibliotecas lidas do arquivo CSV.")
    return libs


# =========================
# APLICA BIBLIOTECAS NA FILA
# =========================
def update_queue_libraries(session, token, queue_id, libraries):
    url = f"https://api.{ENVIRONMENT}/api/v2/routing/queues/{queue_id}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "cannedResponseLibraries": [{"id": lib} for lib in libraries]
    }

    response = session.patch(url, json=payload, headers=headers)

    if response.status_code in (200, 204):
        logging.info(f"[OK] Fila {queue_id} atualizada com {len(libraries)} bibliotecas.")
        return True
    else:
        logging.error(f"[ERRO] Fila {queue_id}: {response.status_code} - {response.text}")
        return False


# =========================
# MAIN
# =========================
def main():
    try:
        token = get_token()

        queues = read_queues(QUEUES_CSV)
        libraries = read_libraries(LIBS_CSV)

        if not queues:
            logging.warning("Nenhuma fila encontrada no CSV.")
            return

        if not libraries:
            logging.warning("Nenhuma biblioteca encontrada no CSV.")
            return

        session = requests.Session()

        logging.info(f"Aplicando {len(libraries)} bibliotecas em {len(queues)} filas...")
        logging.info("-------------------------------------------------------------")

        for queue_id in queues:
            update_queue_libraries(session, token, queue_id, libraries)
            time.sleep(DELAY_BETWEEN_REQUESTS)

        logging.info("Processo concluído com sucesso.")

    except Exception as e:
        logging.error(f"Erro durante a execução: {str(e)}")


if __name__ == "__main__":
    main()
