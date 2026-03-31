import base64
import requests
import sys
import os
import csv
import json
import datetime
import logging
from dotenv import load_dotenv
 
# ---------------- LOGS ---------------- #
data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
log_file = fr"C:\Users\alexandre.ferreira\Desktop\Code\LOGS\{data_atual}_UpdateWrapupQueues.log"
os.makedirs(os.path.dirname(log_file), exist_ok=True)
 
logging.basicConfig(
    level=logging.INFO,
    filename=log_file,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
 
print('---- INICIANDO SCRIPT UPDATE WRAPUP QUEUES ----')
 
# ---------------- OBS ---------------- #
#WRAP-UP MODES:
       #MANDATORY_TIMEOUT   (Mandatory, Time-boxed)
       #MANDATORY_FORCED_TIMEOUT   (Mandatory, Time-boxed no early exit)
       #MANDATORY   (Mandatory, Discretionary)
       #OPTIONAL   (Optional)
       #AGENT_REQUESTED   (Agent Requested)
 
#CABEÇALHO CSV:     queueId,modo,minutos,segundos
 
# ---------------- ENV ---------------- #
env_file = r'C:\Users\alexandre.ferreira\Desktop\Code\ENV\.env'
csv_input = r'C:\Users\alexandre.ferreira\Desktop\Code\xxxxxxxxxxxxxxxxxxxxqueue.csv'
 
load_dotenv(env_file)
 
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
ENVIRONMENT = os.getenv('ENVIRONMENT')
 
# ---------------- AUTH ---------------- #
authorization = base64.b64encode(
    f"{CLIENT_ID}:{CLIENT_SECRET}".encode("ISO-8859-1")
).decode("ascii")
 
auth_url = f"https://login.{ENVIRONMENT}/oauth/token"
auth_headers = {
    "Authorization": f"Basic {authorization}",
    "Content-Type": "application/x-www-form-urlencoded"
}
auth_body = {"grant_type": "client_credentials"}
 
response = requests.post(auth_url, headers=auth_headers, data=auth_body)
 
if response.status_code != 200:
    logging.error("Erro ao gerar token")
    sys.exit(1)
 
token = response.json()
headers = {
    "Authorization": f"{token['token_type']} {token['access_token']}",
    "Content-Type": "application/json"
}
 
api_url = f"https://api.{ENVIRONMENT}"
 
# ---------------- FUNÇÕES ---------------- #
 
def clean_payload(payload: dict) -> dict:
    """Remove campos que não podem ser enviados no PUT"""
    read_only_fields = [
        "dateCreated",
        "dateModified",
        "createdBy",
        "modifiedBy",
        "peerId"
    ]
    for field in read_only_fields:
        payload.pop(field, None)
 
    return payload
 
 
def convert_to_milliseconds(minutes, seconds):
    """Converte minutos e segundos para milissegundos"""
    minutes = int(minutes) if minutes else 0
    seconds = int(seconds) if seconds else 0
 
    total_seconds = (minutes * 60) + seconds
 
    if total_seconds > 0 and total_seconds < 1:
        raise ValueError("Timeout não pode ser menor que 1 segundo.")
 
    return total_seconds * 1000
 
 
def update_wrapup_settings(queue_payload: dict, modo: str, minutes: str, seconds: str) -> dict:
    """
    Altera SOMENTE:
    - acwSettings.wrapupPrompt
    - acwSettings.timeoutMs (quando aplicável)
    """
 
    # Garante que o campo exista
    if "acwSettings" not in queue_payload:
        queue_payload["acwSettings"] = {}
 
    timeout_modes = [
        "MANDATORY_TIMEOUT",
        "MANDATORY_FORCED_TIMEOUT",
        "AGENT_REQUESTED"
    ]
 
    new_acw = {
        "wrapupPrompt": modo
    }
 
    if modo in timeout_modes:
        timeout_ms = convert_to_milliseconds(minutes, seconds)
 
        if timeout_ms < 1000:
            raise ValueError("Timeout deve ser no mínimo 1 segundo (1000 ms).")
 
        new_acw["timeoutMs"] = timeout_ms
 
    queue_payload["acwSettings"] = new_acw
 
    return queue_payload
 
 
def process_queue(queue_id: str, modo: str, minutes: str, seconds: str):
    try:
        # GET fila
        get_url = f"{api_url}/api/v2/routing/queues/{queue_id}"
        response = requests.get(get_url, headers=headers)
 
        if response.status_code != 200:
            logging.error(f"GET falhou | Fila {queue_id} | {response.text}")
            return
 
        queue_data = response.json()
 
        # Remove campos read-only
        queue_data = clean_payload(queue_data)
 
        # Aplica alteração do Wrapup
        queue_data = update_wrapup_settings(queue_data, modo, minutes, seconds)
 
        # PUT fila
        put_url = f"{api_url}/api/v2/routing/queues/{queue_id}"
        put_response = requests.put(
            put_url,
            headers=headers,
            data=json.dumps(queue_data)
        )
 
        if put_response.status_code == 200:
            logging.info(f"Fila atualizada com sucesso | {queue_id}")
            print(f"✔ Fila atualizada: {queue_id}")
        else:
            logging.error(
                f"PUT falhou | Fila {queue_id} | "
                f"{put_response.status_code} | {put_response.text}"
            )
 
    except Exception as e:
        logging.error(f"Erro inesperado | Fila {queue_id} | {str(e)}")
 
 
# ---------------- EXECUÇÃO ---------------- #
 
with open(csv_input, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        queue_id = row.get("queueId")
        modo = row.get("modo")
        minutes = row.get("minutos")
        seconds = row.get("segundos")
 
        if queue_id and modo:
            process_queue(queue_id, modo, minutes, seconds)
 
print("---- SCRIPT FINALIZADO ----")