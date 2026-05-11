import customtkinter as ctk
from PIL import Image
import os

class TelaSelecao(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(fg_color="transparent")

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0) # Linha da Logo
        self.grid_rowconfigure(2, weight=0) # Linha do Card
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ==========================================
        # LOGO PRINCIPAL
        # ==========================================
        try:
            caminho_logo = "assets/resk.ico"
            if os.path.exists(caminho_logo):
                img_logo_pil = Image.open(caminho_logo)
                # Tamanho ajustado para ficar idêntico ao seu print
                logo_image = ctk.CTkImage(light_image=img_logo_pil, size=(110, 110))
                self.label_logo = ctk.CTkLabel(self, text="", image=logo_image)
                self.label_logo.grid(row=1, column=0, pady=(0, 20))
        except Exception as e:
            print(f"Aviso: Erro ao carregar a logo na tela de seleção: {e}")


        # ==========================================
        # CARD PRINCIPAL (Container)
        # ==========================================
        # Reduzi a altura para 450 para um visual mais enxuto
        card = ctk.CTkFrame(self, width=450, height=450)
        card.grid(row=2, column=0)
        card.grid_propagate(False)
        card.pack_propagate(False)

        # ==========================================
        # CONTAINER DE ALINHAMENTO (Novo)
        # ==========================================
        # Este frame interno centraliza todos os itens no meio do card
        inner_frame = ctk.CTkFrame(card, fg_color="transparent")
        inner_frame.pack(expand=True)

        # Título principal (agora dentro do inner_frame)
        ctk.CTkLabel(
            inner_frame,
            text="Qual serviço\ndeseja conectar?",
            font=("Helvetica", 32, "bold"),
            justify="center"
        ).pack(pady=(0, 40))

        # Botões sem ícones, centralizados (agora dentro do inner_frame)
        btn_icloud = ctk.CTkButton(
            inner_frame,
            text="Apple iCloud",
            width=320,
            height=60,
            font=("Helvetica", 16, "bold"),
            command=lambda: self.selecionar_servico("iCloud")
        )
        btn_icloud.pack(pady=10)

        btn_gphotos = ctk.CTkButton(
            inner_frame,
            text="Google Fotos",
            width=320,
            height=60,
            font=("Helvetica", 16, "bold"),
            command=lambda: self.selecionar_servico("Google Fotos")
        )
        btn_gphotos.pack(pady=10)


    def selecionar_servico(self, servico):
        self.controller.dados_redutor["servico"] = servico
        self.controller.mostrar_tela("TelaLogin")