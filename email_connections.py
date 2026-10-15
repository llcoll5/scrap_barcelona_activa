import imaplib
from email import message_from_bytes
from email.header import decode_header
import os
import pandas as pd
import smtplib
from email.mime.text import MIMEText
import re

# Conectem al servidor IMAP
USERNAME = "llcoll@digitalresponse.es"
PASSWORD = "zkbmjuvsenrbmrpy"

mail = imaplib.IMAP4_SSL("imap.gmail.com")

# Iniciem sessió al compte
mail.login(USERNAME, PASSWORD)
mail.select("inbox")

# Busquem els correus amb Email Semanal al assumpte
status, messages = mail.search(None, 'SUBJECT "Email Semanal"')

def process_message():
    pass

# Carpeta temporal para guardar adjuntos
adjuntos_dir = "adjuntos"
os.makedirs(adjuntos_dir, exist_ok=True)


# Procesar cada correo
for msg_num in messages[0].split():
    status, msg_data = mail.fetch(msg_num, "(RFC822)")
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = message_from_bytes(response_part[1])
            if msg.is_multipart():
                for part in msg.walk():
                    # Verificar si es un archivo adjunto
                    if part.get_content_disposition() == "attachment":
                        filename = part.get_filename()
                        if filename and filename.endswith(".xlsx"):
                            filepath = os.path.join(adjuntos_dir, filename)
                            with open(filepath, "wb") as f:
                                f.write(part.get_payload(decode=True))
                            print(f"Archivo adjunto guardado en: {filepath}")



def procesar_excel(filepath):
    # Cargar el archivo Excel
    df = pd.read_excel(filepath)
    column_names = df.iloc[1].values.tolist()
    df.drop([0, 1], inplace=True)
    df.columns = column_names
    df.dropna(axis=0, inplace=True)

    # Lógica de procesamiento; aquí puedes definir las condiciones de alerta
    # Ejemplo: verificar si algún valor en la columna "Valor" supera un umbral
    alertas = []
    umbral = 100  # Definir el umbral según sea necesario
    for _, row in df.iterrows():
        valor = row.get("Sent", 0)  # Asegúrate de que exista la columna 'Valor'
        if int(valor) > umbral:
            alertas.append(f"Alerta: Valor {valor} supera el umbral en fila {row.name + 1}")

    return alertas



def enviar_alerta(asunto, mensaje):
    remitente = "llcoll@digitalresponse.es"
    destinatario = "llcoll@digitalresponse.es"
    msg = MIMEText(mensaje)
    msg["Subject"] = asunto
    msg["From"] = remitente
    msg["To"] = destinatario

    # Enviar el correo
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(remitente, PASSWORD)
        server.sendmail(remitente, destinatario, msg.as_string())
        print("Alerta enviada")




alertas = procesar_excel(filepath)
if alertas:
    mensaje_alerta = "\n".join(alertas)
    enviar_alerta("Alerta de datos en Excel", mensaje_alerta)
