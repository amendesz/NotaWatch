# main.py

from dotenv import load_dotenv
import tkinter as tk
from tkinter import messagebox
import threading
import time
import json
import os
import boto3
import logging
from datetime import datetime, timedelta

# Carregar variáveis do .env
load_dotenv()


# Caminhos e configurações
COUNT_FILE = 'data/count.json'
LOG_FILE_PATH = 'logs/audit_log.txt'
PDF_FOLDER = os.getenv("PDF_FOLDER_PATH", "C:/pdf")
SENT_FILES_LOG = 'logs/sent_files.txt'
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

# Inicializa pastas e arquivos
for folder in ["logs", "data"]:
    os.makedirs(folder, exist_ok=True)
if not os.path.exists(COUNT_FILE):
    with open(COUNT_FILE, "w") as f:
        json.dump({"date": "", "count": 0}, f)

# Logging
logging.basicConfig(filename=LOG_FILE_PATH, level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

# Funções AWS
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

def test_aws_connection():
    try:
        s3.list_buckets()
        return True
    except Exception:
        return False

def send_to_s3(file_path, s3_key):
    try:
        s3.head_object(Bucket=BUCKET_NAME, Key=s3_key)
        logging.info(f'O arquivo {s3_key} já existe no S3.')
    except Exception as e:
        if '404' in str(e):
            s3.upload_file(file_path, BUCKET_NAME, s3_key)
            logging.info(f'O arquivo {s3_key} foi enviado para o S3.')
            return True
        else:
            logging.error(f'Erro ao verificar o arquivo {s3_key} no S3: {str(e)}')
    return False

def read_sent_files():
    try:
        with open(SENT_FILES_LOG, 'r') as f:
            return set(f.read().splitlines())
    except FileNotFoundError:
        return set()

def write_sent_file(file_name):
    try:
        if not os.access("logs", os.W_OK):
            raise PermissionError("Sem permissão de gravação no diretório 'logs'.")
        with open(SENT_FILES_LOG, 'a') as f:
            f.write(file_name + '\n')
    except Exception as e:
        messagebox.showerror("Erro de Log", f"Não foi possível gravar log de arquivos enviados:\n{e}")

def get_daily_count():
    today = datetime.now().strftime('%Y-%m-%d')
    try:
        if not os.access("data", os.W_OK):
            raise PermissionError("Sem permissão de gravação no diretório 'data'.")
        with open(COUNT_FILE, 'r') as f:
            data = json.load(f)
        if data['date'] != today:
            data = {'date': today, 'count': 0}
            with open(COUNT_FILE, 'w') as f:
                json.dump(data, f)
        return data['count']
    except Exception:
        return 0

def increment_daily_count():
    today = datetime.now().strftime('%Y-%m-%d')
    try:
        if not os.access("data", os.W_OK):
            raise PermissionError("Sem permissão de gravação no diretório 'data'.")
        with open(COUNT_FILE, 'r') as f:
            data = json.load(f)
    except:
        data = {"date": today, "count": 0}

    if data['date'] != today:
        data = {'date': today, 'count': 0}

    data['count'] += 1

    with open(COUNT_FILE, 'w') as f:
        json.dump(data, f)

# Watcher
watching = False
watcher_thread = None

def watcher_loop():
    last_check = datetime.now()
    while watching:
        try:
            sent_files = read_sent_files()
            new_files = []

            for file in os.listdir(PDF_FOLDER):
                try:
                    file_path = os.path.join(PDF_FOLDER, file)
                    file_name = os.path.basename(file_path)

                    if not file.lower().endswith('.pdf'):
                        continue

                    if file_name in sent_files:
                        continue

                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_mtime > last_check:
                        new_files.append((file_name, file_path))

                except Exception as e:
                    logging.error(f"Erro ao processar o arquivo '{file}': {str(e)}")

            last_check = datetime.now()

            if new_files:
                for file_name, file_path in new_files:
                    logging.info(f"Novo arquivo detectado: {file_name}")
                    if send_to_s3(file_path, file_name):
                        write_sent_file(file_name)
                        increment_daily_count()

            time.sleep(10)

        except Exception as e:
            logging.error(f"Erro no watcher loop: {str(e)}")
            time.sleep(15)

def start_watching():
    global watching, watcher_thread
    if not watching:
        watching = True
        watcher_thread = threading.Thread(target=watcher_loop, daemon=True)
        watcher_thread.start()

def stop_watching():
    global watching
    watching = False

def is_watching_active():
    return watching

# Interface Gráfica
class App:
    def __init__(self, master):
        self.master = master
        self.master.title("Monitor de Envio de Notas")
        self.master.geometry("400x300")

        self.status_var = tk.StringVar(value="Parado")
        self.count_var = tk.StringVar(value="0")
        self.connection_var = tk.StringVar(value="Desconhecido")

        tk.Label(master, text="Status do Serviço:").pack(pady=5)
        tk.Label(master, textvariable=self.status_var, fg="blue", font=("Arial", 12)).pack()

        tk.Label(master, text="Notas Enviadas Hoje:").pack(pady=5)
        tk.Label(master, textvariable=self.count_var, fg="green", font=("Arial", 12)).pack()

        tk.Label(master, text="Conexão com AWS:").pack(pady=5)
        tk.Label(master, textvariable=self.connection_var, fg="orange", font=("Arial", 12)).pack()

        self.start_button = tk.Button(master, text="Iniciar Envio", command=self.start_service)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(master, text="Parar Envio", command=self.stop_service, state=tk.DISABLED)
        self.stop_button.pack()

        self.test_conn_button = tk.Button(master, text="Testar Conexão AWS", command=self.test_connection)
        self.test_conn_button.pack(pady=10)

        self.update_counter()

    def update_counter(self):
        self.count_var.set(str(get_daily_count()))
        self.master.after(5000, self.update_counter)

    def start_service(self):
        if not is_watching_active():
            start_watching()
            self.status_var.set("Rodando")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.log_action("Serviço iniciado")

    def stop_service(self):
        if is_watching_active():
            stop_watching()
            self.status_var.set("Parado")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.log_action("Serviço parado")

    def test_connection(self):
        ok = test_aws_connection()
        self.connection_var.set("OK" if ok else "Falha")
        self.log_action("Teste de conexão: " + ("Sucesso" if ok else "Falha"))
        messagebox.showinfo("Conexão AWS", "Conexão bem-sucedida!" if ok else "Falha na conexão.")

    def log_action(self, action):
        try:
            if not os.path.exists("logs"):
                os.makedirs("logs")
            if not os.access("logs", os.W_OK):
                raise PermissionError("Sem permissão de gravação no diretório 'logs'.")
            with open(LOG_FILE_PATH, "a") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {action}\n")
        except Exception as e:
            messagebox.showerror("Erro de Log", f"Não foi possível gravar o log:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
