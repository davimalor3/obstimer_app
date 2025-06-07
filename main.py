import time

from obswebsocket import obsws, requests

HOST = "192.168.0.100"
PORT = 4455
PASSWORD = "NoslCIOYUUQa2dNN"
TEMPO_DE_GRAVACAO = 5

# Conectar ao OBS WebSocket
ws = obsws(HOST, PORT, PASSWORD)
ws.connect()

# Iniciar gravação
print("Iniciando gravação...")
ws.call(requests.StartRecord())

# Esperar o tempo definido
time.sleep(TEMPO_DE_GRAVACAO)

# Parar gravação
print("Parando gravação...")
ws.call(requests.StopRecord())

# Desconectar
ws.disconnect()
print("Gravação finalizada com sucesso!")
