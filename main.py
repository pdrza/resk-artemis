import sys
import customtkinter as ctk

from telas.tela_selecao import TelaSelecao
from telas.tela_login import TelaLogin
from telas.tela_configuracao import TelaConfiguracao
from telas.tela_progresso import TelaProgresso

# Previne erros de stdout/stderr ao rodar o app compilado (sem console)
class DummyTerminal:
    def write(self, *args, **kwargs): pass
    def flush(self, *args, **kwargs): pass

if sys.stdout is None: sys.stdout = DummyTerminal()
if sys.stderr is None: sys.stderr = DummyTerminal()

ctk.set_default_color_theme("tema_artemis.json")
ctk.set_appearance_mode("light")

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Resk Artemis")
        self.geometry("700x850")

        # Ícone
        try:
            self.iconbitmap("assets/resk.ico")
        except Exception:
            pass

        # Dicionário de estado do app
        self.dados_redutor = {
            "servico": None, "email": "", "senha": "", "pasta": ""
        }

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (TelaSelecao, TelaLogin, TelaConfiguracao, TelaProgresso):
            nome_pagina = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[nome_pagina] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.mostrar_tela("TelaSelecao")

    def mostrar_tela(self, nome_pagina):
        frame = self.frames[nome_pagina]
        if hasattr(frame, "ao_mostrar"):
            frame.ao_mostrar()
        frame.tkraise()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()