# OBSTimer App

Um script Python para controlar o tempo de gravação do OBS Studio remotamente através do WebSocket. Ele inicia uma gravação, aguarda por um tempo pré-definido e para a gravação automaticamente.

### Pré-requisitos

- [Git](https://git-scm.com/)
- [Python 3.x](https://www.python.org/downloads/)
- **OBS Studio** com o servidor **WebSocket** ativado.
  - No OBS, vá em `Ferramentas` -> `Configurações do WebSocket`.
  - Marque a opção `Ativar servidor WebSocket`.
  - Anote a porta (padrão `4455`) e defina uma senha.

### Instalação e Configuração

1.  **Clone o repositório**
    Abra seu terminal ou prompt de comando e execute o seguinte comando:

    ```bash
    git clone https://github.com/davimalor3/obstimer_app.git
    ```

2.  **Acesse o diretório do projeto**

    ```bash
    cd obstimer_app
    ```

3.  **Instale as dependências**
    É altamente recomendado usar um ambiente virtual(venv). Após criar e ativa-lo, instale as dependências do projeto:

    ```bash
    pip install -r requirements.txt
    ```

## Executando o Script

```bash
python main.py
```

O script irá se conectar ao OBS, iniciar a gravação pelo tempo determinado e depois pará-la.
