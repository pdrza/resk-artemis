import customtkinter as ctk

class TelaLogin(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(fg_color="transparent")

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(self, text="← Voltar", width=60, fg_color="transparent", hover_color="#C0C1BC",
                      text_color="#2C2D28", font=("Helvetica", 14),
                      command=lambda: self.controller.mostrar_tela("TelaSelecao")).place(x=30, y=30)

        card = ctk.CTkFrame(self, width=450, height=450)
        card.grid(row=1, column=0)
        card.pack_propagate(False)

        inner_frame = ctk.CTkFrame(card, fg_color="transparent")
        inner_frame.pack(expand=True)

        self.label_titulo = ctk.CTkLabel(inner_frame, text="Login", font=("Helvetica", 32, "bold"))
        self.label_titulo.pack(pady=(0, 30))

        self.entry_usuario = ctk.CTkEntry(inner_frame, placeholder_text="E-mail iCloud", width=340, height=50)
        self.entry_usuario.pack(pady=(0, 15))

        self.entry_senha = ctk.CTkEntry(inner_frame, placeholder_text="Senha iCloud", show="•", width=340, height=50)
        self.entry_senha.pack(pady=(0, 5))

        self.label_mensagem = ctk.CTkLabel(inner_frame, text="", text_color="#935A5E", font=("Helvetica", 12))
        self.label_mensagem.pack(pady=5)

        ctk.CTkButton(inner_frame, text="Continuar", width=340, height=55, font=("Helvetica", 16, "bold"),
                      command=self.avancar).pack(pady=(15, 0))

    def ao_mostrar(self):
        servico = self.controller.dados_redutor.get("servico", "Serviço")
        self.label_titulo.configure(text=f"{servico}")
        self.label_mensagem.configure(text="")

    def avancar(self):
        email = self.entry_usuario.get().strip()
        senha = self.entry_senha.get()
        if not email or not senha:
            self.label_mensagem.configure(text="Por favor, preencha todos os campos.")
            return

        # Credenciais salvas apenas na memória temporária para enviar direto para a API
        self.controller.dados_redutor["email"] = email
        self.controller.dados_redutor["senha"] = senha
        self.controller.mostrar_tela("TelaConfiguracao")