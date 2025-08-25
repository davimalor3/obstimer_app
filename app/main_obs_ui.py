import asyncio
import logging
import threading
from tkinter import messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from app.obs_client import OBSClient
from app.timer_obs import TimerController

logger = logging.getLogger(__name__)


class OBSTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OBS Timer - Gravação Automática")
        self.root.geometry("500x700")
        self.root.resizable(False, False)

        # Estado
        self.obs = None
        self.obs_loop = asyncio.new_event_loop()
        self.timer = None
        self.total_seconds = 0
        self.is_connected = False
        self.is_recording = False

        # Interface
        self.host = ttk.StringVar(value="localhost")
        self.port = ttk.StringVar(value="4455")
        self.password = ttk.StringVar(value="")
        self.show_password = ttk.BooleanVar()

        self.hours = ttk.StringVar(value="0")
        self.minutes = ttk.StringVar(value="0")
        self.seconds = ttk.StringVar(value="30")

        # Botoes Interface
        self.connection_status = None
        self.recording_status = None
        self.time_display = None
        self.time_remaining_status = None
        self.progress = None
        self.progress_label = None
        self.connect_btn = None
        self.test_btn = None
        self.start_btn = None
        self.stop_btn = None
        self.password_entry = None

        self.setup_ui()
        self.start_async_loop()

    def setup_ui(self):

        # Titulo janela
        ttk.Label(
            self.root,
            text="OBS Timer - Gravação Automática",
            font=("Arial", 16, "bold"),
        ).pack(pady=10)

        # --------------      CONFIGURAÇÃO DE CONEXÃO  --------------
        connection_frame = ttk.LabelFrame(
            self.root, text="Configurações de Conexão OBS", padding=10
        )
        connection_frame.pack(fill="x", padx=20, pady=5)

        config_grid = ttk.Frame(connection_frame)
        config_grid.pack(fill="x", pady=5)

        ttk.Label(config_grid, text="Host/IP:").grid(row=0, column=0, sticky="w")
        ttk.Entry(config_grid, textvariable=self.host, width=60).grid(
            row=0, column=1, padx=5, sticky="ew"
        )

        ttk.Label(config_grid, text="Porta:").grid(
            row=0, column=2, sticky="w", padx=(10, 0)
        )
        ttk.Entry(config_grid, textvariable=self.port, width=8).grid(
            row=0, column=3, padx=5
        )

        ttk.Label(config_grid, text="Senha:").grid(
            row=1, column=0, sticky="w", pady=(5, 0)
        )
        self.password_entry = ttk.Entry(
            config_grid, textvariable=self.password, show="*", width=25
        )
        self.password_entry.grid(
            row=1, column=1, columnspan=2, padx=5, pady=(5, 0), sticky="ew"
        )

        ttk.Checkbutton(
            config_grid,
            text="Mostrar",
            variable=self.show_password,
            command=self.toggle_password,
            bootstyle="info-outline-toolbutton",
        ).grid(row=1, column=3, padx=5, pady=(5, 0))

        config_grid.columnconfigure(1, weight=1)

        self.connection_status = ttk.Label(
            connection_frame,
            text="● Desconectado - Configure os dados acima",
            style="danger.TLabel",
            font=("Arial", 10, "bold"),
        )
        self.connection_status.pack()

        connection_buttons = ttk.Frame(connection_frame)
        connection_buttons.pack(pady=5)

        self.connect_btn = ttk.Button(
            connection_buttons,
            text="Conectar ao OBS",
            command=self.connect_obs,
            bootstyle=SUCCESS,
            width=18,
        )
        self.connect_btn.pack(side="left", padx=5)

        self.test_btn = ttk.Button(
            connection_buttons,
            text="Testar",
            command=self.test_connection,
            bootstyle="info-outline",
            width=10,
        )
        self.test_btn.pack(side="left", padx=5)

        # ===================== TIMER =====================
        timer_frame = ttk.LabelFrame(self.root, text="Configurar Timer", padding=10)
        timer_frame.pack(fill="x", padx=20, pady=10)

        time_frame = ttk.Frame(timer_frame)
        time_frame.pack()

        # Campo horas
        ttk.Label(time_frame, text="Horas:").grid(row=0, column=0, padx=5)
        ttk.Combobox(
            time_frame,
            textvariable=self.hours,
            values=[str(i) for i in range(11)],
            width=5,
            state="readonly",
        ).grid(row=1, column=0, padx=5)

        # Campo minutos
        ttk.Label(time_frame, text="Minutos:").grid(row=0, column=1, padx=5)
        ttk.Combobox(
            time_frame,
            textvariable=self.minutes,
            values=[str(i) for i in range(60)],
            width=5,
            state="readonly",
        ).grid(row=1, column=1, padx=5)

        # Campo segundos
        ttk.Label(time_frame, text="Segundos:").grid(row=0, column=2, padx=5)
        ttk.Combobox(
            time_frame,
            textvariable=self.seconds,
            values=[str(i) for i in range(60)],
            width=5,
            state="readonly",
        ).grid(row=1, column=2, padx=5)

        # --------------     CONTROLES  --------------
        control_frame = ttk.LabelFrame(self.root, text="Controles", padding=10)
        control_frame.pack(fill="x", padx=20, pady=10)

        button_frame = ttk.Frame(control_frame)
        button_frame.pack()

        self.start_btn = ttk.Button(
            button_frame,
            text="Iniciar Gravação",
            command=self.start_recording,
            bootstyle=PRIMARY,
            width=15,
        )
        self.start_btn.pack(side="left", padx=5)

        self.stop_btn = ttk.Button(
            button_frame,
            text="Parar Gravação",
            command=self.stop_recording,
            bootstyle=DANGER,
            width=15,
            state="disabled",
        )
        self.stop_btn.pack(side="left", padx=5)

        # --------------     STATUS  --------------
        counter_frame = ttk.LabelFrame(self.root, text="Status da Gravação", padding=10)
        counter_frame.pack(fill="x", padx=20, pady=10)

        self.time_display = ttk.Label(
            counter_frame, text="00:00:00", font=("Arial", 24, "bold")
        )
        self.time_display.pack()

        self.recording_status = ttk.Label(
            counter_frame, text="Pronto para Gravar", font=("Arial", 12)
        )
        self.recording_status.pack(pady=5)

        self.time_remaining_status = ttk.Label(
            counter_frame, text="", font=("Arial", 11, "bold"), foreground="orange"
        )
        self.time_remaining_status.pack(pady=2)

        self.progress = ttk.Progressbar(
            counter_frame, mode="determinate", bootstyle=INFO
        )
        self.progress.pack(fill="x", pady=5)

        self.progress_label = ttk.Label(counter_frame, text="", font=("Arial", 10))
        self.progress_label.pack(pady=2)

    def toggle_password(self):
        if self.show_password.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

    def start_async_loop(self):
        threading.Thread(target=self.obs_loop.run_forever, daemon=True).start()

    def run_in_loop(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self.obs_loop)

    def update_status(self, text, style="info.TLabel"):
        self.connection_status.config(text=text, style=style)

    def connect_obs(self):
        self.obs = OBSClient(
            host=self.host.get(),
            port=int(self.port.get()),
            password=self.password.get(),
        )
        future = self.run_in_loop(self.obs.connect())

        def check():
            if future.done():
                if future.result():
                    self.is_connected = True
                    self.update_status("● Conectado e Pronto", "success.TLabel")
                else:
                    self.update_status("● Falha na Conexão", "danger.TLabel")
            else:
                self.root.after(100, check)

        check()

    def test_connection(self):
        test_client = OBSClient(
            host=self.host.get(),
            port=int(self.port.get()),
            password=self.password.get(),
        )
        future = self.run_in_loop(test_client.connect())

        def check():
            if future.done():
                if future.result():
                    self.update_status(
                        "● Teste OK - Clique em Conectar", "success.TLabel"
                    )
                    messagebox.showinfo("Sucesso", "Conexão testada com sucesso!")
                else:
                    self.update_status(
                        "● Teste Falhou - Verifique os dados", "danger.TLabel"
                    )
                    messagebox.showerror("Erro", "Falha ao testar conexão.")
            else:
                self.root.after(100, check)

        check()

    def start_recording(self):
        if not self.is_connected:
            messagebox.showerror("Erro", "Conecte-se ao OBS primeiro.")
            return
        if self.is_recording:
            messagebox.showwarning("Aviso", "Gravação em andamento.")
            return

        h, m, s = (
            int(self.hours.get()),
            int(self.minutes.get()),
            int(self.seconds.get()),
        )
        self.total_seconds = h * 3600 + m * 60 + s
        if self.total_seconds <= 0:
            messagebox.showerror("Erro", "Configure um tempo maior que zero.")
            return

        self.recording_status.config(
            text="Iniciando gravação...", style="warning.TLabel"
        )
        self.start_btn.config(state="disabled")
        future = self.run_in_loop(self.obs.start_recording())

        def check():
            if future.done():
                if future.result():
                    self.start_timer()
                else:
                    self.recording_status.config(
                        text="Erro ao iniciar", style="danger.TLabel"
                    )
                    self.start_btn.config(state="normal")
            else:
                self.root.after(100, check)

        check()

    def start_timer(self):
        self.is_recording = True
        self.timer = TimerController(
            self.total_seconds,
            update_ui_callback=self.update_timer_ui,
            finish_callback=self.finish_recording,
        )
        self.timer.start()
        self.recording_status.config(text="🔴 Gravando...", style="danger.TLabel")
        self.stop_btn.config(state="normal")

    def update_timer_ui(self, remaining, total):
        h, rem = divmod(remaining, 3600)
        m, s = divmod(rem, 60)
        self.time_display.config(text=f"{h:02d}:{m:02d}:{s:02d}")

        if remaining <= 60:
            self.time_remaining_status.config(
                text=f"⚠️ FINALIZANDO EM {s}s!", foreground="red"
            )
        else:
            self.time_remaining_status.config(
                text=f"⏰ Restam {m}min {s}s para finalizar", foreground="orange"
            )

        progress_value = (total - remaining) / total * 100
        self.progress.config(value=progress_value)
        self.progress_label.config(text=f"Progresso: {progress_value:.1f}%")

    def finish_recording(self):
        self.is_recording = False
        future = self.run_in_loop(self.obs.stop_recording())

        def check():
            if future.done():
                self.recording_status.config(
                    text="✅ Gravação Finalizada!", style="success.TLabel"
                )
                self.time_remaining_status.config(
                    text="🎉 Timer concluído com sucesso!", foreground="green"
                )
                self.start_btn.config(state="normal")
                self.stop_btn.config(state="disabled")
                self.progress.config(value=100)
                self.progress_label.config(text="Progresso: 100.0%")
                messagebox.showinfo("Concluído", "Gravação finalizada automaticamente!")
            else:
                self.root.after(100, check)

        check()

    def stop_recording(self):
        if self.timer:
            self.timer.stop()
        if self.is_recording:
            future = self.run_in_loop(self.obs.stop_recording())
            self.is_recording = False

            def check():
                if future.done():
                    self.recording_status.config(
                        text="⏹️ Gravação Interrompida", style="warning.TLabel"
                    )
                    self.time_remaining_status.config(
                        text="⏸️ Gravação interrompida manualmente", foreground="orange"
                    )
                    self.start_btn.config(state="normal")
                    self.stop_btn.config(state="disabled")
                    self.progress.config(value=0)
                    self.progress_label.config(text="")
                else:
                    self.root.after(100, check)

            check()
