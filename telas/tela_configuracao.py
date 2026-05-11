import customtkinter as ctk
import tkinter.filedialog as filedialog
from utils import validar_permissao_escrita


class TelaConfiguracao(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(fg_color="transparent")

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(self, text="← Voltar", width=60, fg_color="transparent", hover_color="#C0C1BC",
                      text_color="#2C2D28",
                      font=("Helvetica", 14), command=lambda: self.controller.mostrar_tela("TelaLogin")).place(x=30, y=30)

        # ==========================================
        # CARD PRINCIPAL (Container)
        # ==========================================
        card = ctk.CTkFrame(self, width=500, height=500)
        card.grid(row=1, column=0)
        card.pack_propagate(False)

        # Título principal isolado e alinhado no topo
        ctk.CTkLabel(card, text="Onde guardar?", font=("Helvetica", 32, "bold")).pack(pady=(50, 10))
        ctk.CTkLabel(card, text="Escolha a pasta local para salvar os arquivos.", font=("Helvetica", 14),
                     text_color="#7B7C77").pack(pady=(0, 40))

        self.frame_pasta = ctk.CTkFrame(card, fg_color="#FFFFFF", border_width=1, border_color="#A1A29D",
                                        corner_radius=10, width=400, height=55)
        self.frame_pasta.pack(pady=10)
        self.frame_pasta.pack_propagate(False)

        self.label_pasta_atual = ctk.CTkLabel(self.frame_pasta, text=" Nenhuma pasta selecionada",
                                              font=("Helvetica", 14), text_color="#7B7C77")
        self.label_pasta_atual.pack(side="left", padx=15, pady=12)

        ctk.CTkButton(card, text="Procurar Pasta", width=220, height=45, fg_color="#C0C1BC", hover_color="#A1A29D",
                      text_color="#2C2D28",
                      font=("Helvetica", 14, "bold"), command=self.escolher_pasta).pack(pady=15)

        self.label_erro = ctk.CTkLabel(card, text="", text_color="#935A5E", font=("Helvetica", 12))
        self.label_erro.pack(pady=5)

        ctk.CTkButton(card, text="Iniciar", width=340, height=60, font=("Helvetica", 16, "bold"),
                      command=self.avancar).pack(pady=(20, 20))

    def escolher_pasta(self):
        pasta = filedialog.askdirectory(title="Escolha onde guardar as fotos reduzidas", mustexist=True)
        if not pasta: return
        if not validar_permissao_escrita(pasta):
            self.label_erro.configure(text="Sem permissão de escrita nesta pasta.")
            return

        self.label_erro.configure(text="")
        self.controller.dados_redutor["pasta"] = pasta
        texto_exibido = pasta if len(pasta) < 40 else f"...{pasta[-37:]}"
        self.label_pasta_atual.configure(text=texto_exibido, text_color="#2C2D28")

    def avancar(self):
        if not self.controller.dados_redutor.get("pasta"):
            self.label_erro.configure(text="Escolha uma pasta de destino antes de avançar!")
            return
        self.controller.mostrar_tela("TelaProgresso")