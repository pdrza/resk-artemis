import os
import threading
import customtkinter as ctk
from PIL import Image
from pyicloud import PyiCloudService
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import RAWPY_DISPONIVEL, ler_bytes_do_download, abrir_imagem_universal


class TelaProgresso(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(fg_color="transparent")

        self.evento_pausa = threading.Event()
        self.evento_pausa.set()
        self.flag_cancelar = False

        self.botao_voltar = ctk.CTkButton(self, text="← Voltar ao Início", width=60, fg_color="transparent",
                                          hover_color="#C0C1BC", text_color="#2C2D28",
                                          font=("Helvetica", 14), command=self.voltar_inicio, state="disabled")
        self.botao_voltar.pack(anchor="nw", padx=30, pady=30)

        card = ctk.CTkFrame(self)
        card.pack(fill="both", expand=True, padx=50, pady=(0, 50))

        # ==========================================
        # CONTADORES NO CANTO SUPERIOR DIREITO
        # ==========================================
        self.frame_stats = ctk.CTkFrame(card, fg_color="transparent")
        # Fixando no topo direito (anchor="ne") com margens internas (x e y)
        self.frame_stats.place(relx=1.0, rely=0.0, anchor="ne", x=-40, y=40)

        self.frame_stats.grid_columnconfigure((0, 1, 2), weight=1)

        # REDE
        self.label_titulo_rede = ctk.CTkLabel(self.frame_stats, text="REDE", font=("Helvetica", 11, "bold"),
                                              text_color="#7B7C77")
        self.label_titulo_rede.grid(row=0, column=0, padx=15, sticky="e")
        self.label_valor_rede = ctk.CTkLabel(self.frame_stats, text="0.0 MB/s", font=("Helvetica", 14, "bold"),
                                             text_color="#2C2D28")
        self.label_valor_rede.grid(row=1, column=0, padx=15, sticky="e")

        # MÁXIMA
        self.label_titulo_maxima = ctk.CTkLabel(self.frame_stats, text="MÁXIMA", font=("Helvetica", 11, "bold"),
                                                text_color="#7B7C77")
        self.label_titulo_maxima.grid(row=0, column=1, padx=15, sticky="e")
        self.label_valor_maxima = ctk.CTkLabel(self.frame_stats, text="0.0 MB/s", font=("Helvetica", 14, "bold"),
                                               text_color="#2C2D28")
        self.label_valor_maxima.grid(row=1, column=1, padx=15, sticky="e")

        # ARMAZENAMENTO
        self.label_titulo_armazenamento = ctk.CTkLabel(self.frame_stats, text="ARMAZENAMENTO",
                                                       font=("Helvetica", 11, "bold"), text_color="#7B7C77")
        self.label_titulo_armazenamento.grid(row=0, column=2, padx=15, sticky="e")
        self.label_valor_armazenamento = ctk.CTkLabel(self.frame_stats, text="0.0 MB/s", font=("Helvetica", 14, "bold"),
                                                      text_color="#2C2D28")
        self.label_valor_armazenamento.grid(row=1, column=2, padx=15, sticky="e")

        # ==========================================
        # ELEMENTOS CENTRAIS (Limpos e alinhados)
        # ==========================================
        self.label_titulo = ctk.CTkLabel(card, text="Otimizando", font=("Helvetica", 32, "bold"))
        self.label_titulo.pack(pady=(70, 5))

        self.label_status = ctk.CTkLabel(card, text="A preparar o ambiente...", font=("Helvetica", 14),
                                         text_color="#7B7C77")
        self.label_status.pack(pady=(0, 20))

        self.label_porcentagem = ctk.CTkLabel(card, text="0.00%", font=("Helvetica", 48, "bold"), text_color="#B77849")
        self.label_porcentagem.pack(pady=(15, 0))

        self.barra_progresso = ctk.CTkProgressBar(card, width=480, height=14)
        self.barra_progresso.pack(pady=(20, 30))
        self.barra_progresso.set(0)

        self.frame_botoes = ctk.CTkFrame(card, fg_color="transparent")
        self.frame_botoes.pack(pady=10)

        self.botao_pausar = ctk.CTkButton(self.frame_botoes, text="Pausar", width=140, height=45,
                                          fg_color="#C0C1BC", hover_color="#A1A29D", text_color="#2C2D28",
                                          font=("Helvetica", 14, "bold"),
                                          command=self.pausar_retomar)
        self.botao_pausar.grid(row=0, column=0, padx=15)

        self.botao_cancelar = ctk.CTkButton(self.frame_botoes, text="Cancelar", width=140, height=45,
                                            fg_color="#935A5E", hover_color="#7A4B4E", text_color="#FFFFFF",
                                            font=("Helvetica", 14, "bold"),
                                            command=self.cancelar_processo)
        self.botao_cancelar.grid(row=0, column=1, padx=15)

        self.caixa_log = ctk.CTkTextbox(card, width=520, height=180, font=("Courier", 12))
        self.caixa_log.pack(pady=30)

        # ==========================================
        # VARIÁVEIS PARA CÁLCULO DE VELOCIDADE
        # ==========================================
        self.lock_stats = threading.Lock()
        self.total_bytes_rede = 0
        self.total_bytes_armazenamento = 0
        self.last_bytes_rede = 0
        self.last_bytes_armazenamento = 0
        self.velocidade_maxima = 0.0
        self.processando = False

    # =============== LOOP DE ATUALIZAÇÃO DA UI ===============
    def atualizar_loop(self):
        if not self.processando:
            return

        # Só calcula velocidade se o processo não estiver pausado
        if self.evento_pausa.is_set():
            with self.lock_stats:
                bytes_rede_agora = self.total_bytes_rede
                bytes_arm_agora = self.total_bytes_armazenamento

            # Calcula a diferença de bytes (o que foi processado em 1 segundo)
            diff_rede = bytes_rede_agora - self.last_bytes_rede
            diff_arm = bytes_arm_agora - self.last_bytes_armazenamento

            self.last_bytes_rede = bytes_rede_agora
            self.last_bytes_armazenamento = bytes_arm_agora

            # Converte de Bytes para Megabytes por segundo (MB/s)
            mbps_rede = diff_rede / (1024 * 1024)
            mbps_arm = diff_arm / (1024 * 1024)

            # Atualiza o pico máximo registrado
            if mbps_rede > self.velocidade_maxima:
                self.velocidade_maxima = mbps_rede

            self.atualizar_estatisticas(
                f"{mbps_rede:.1f} MB/s",
                f"{self.velocidade_maxima:.1f} MB/s",
                f"{mbps_arm:.1f} MB/s"
            )
        else:
            # Se estiver pausado, iguala os rastreadores para não gerar um pico absurdo ao retomar
            with self.lock_stats:
                self.last_bytes_rede = self.total_bytes_rede
                self.last_bytes_armazenamento = self.total_bytes_armazenamento

            self.atualizar_estatisticas("0.0 MB/s", f"{self.velocidade_maxima:.1f} MB/s", "0.0 MB/s")

        # Chama a função de novo em 1000ms (1 segundo)
        self.after(1000, self.atualizar_loop)

    # =============== LÓGICA PRINCIPAL ===============

    def ao_mostrar(self):
        self.caixa_log.delete("1.0", "end")
        self.barra_progresso.set(0)
        self.label_porcentagem.configure(text="0.00%")
        self.atualizar_estatisticas("0.0 MB/s", "0.0 MB/s", "0.0 MB/s")
        self.botao_pausar.configure(state="normal", text="Pausar", fg_color="#C0C1BC")
        self.botao_cancelar.configure(state="normal")
        self.botao_voltar.configure(state="disabled")
        self.flag_cancelar = False
        self.evento_pausa.set()

        # Reseta as variáveis de velocidade
        with self.lock_stats:
            self.total_bytes_rede = 0
            self.total_bytes_armazenamento = 0
            self.last_bytes_rede = 0
            self.last_bytes_armazenamento = 0
            self.velocidade_maxima = 0.0

        # Inicia o loop de interface visual
        self.processando = True
        self.atualizar_loop()

        servico = self.controller.dados_redutor.get("servico")
        self.label_titulo.configure(text=f"Resk via {servico}")

        thread = threading.Thread(target=self.iniciar_processamento)
        thread.daemon = True
        thread.start()

    def voltar_inicio(self):
        self.controller.mostrar_tela("TelaSelecao")

    def escrever_log(self, mensagem):
        self.after(0, self._inserir_texto, mensagem)

    def _inserir_texto(self, mensagem):
        self.caixa_log.insert("end", mensagem + "\n")
        self.caixa_log.see("end")

    def atualizar_progresso(self, valor_decimal, texto_porcentagem):
        self.barra_progresso.set(valor_decimal)
        self.label_porcentagem.configure(text=texto_porcentagem)

    def atualizar_estatisticas(self, rede, maxima, armazenamento):
        self.label_valor_rede.configure(text=rede)
        self.label_valor_maxima.configure(text=maxima)
        self.label_valor_armazenamento.configure(text=armazenamento)

    def pausar_retomar(self):
        if self.evento_pausa.is_set():
            self.evento_pausa.clear()
            self.botao_pausar.configure(text="Retomar", fg_color="#457297", hover_color="#576193", text_color="#FFFFFF")
            self.escrever_log("\n[AVISO] Processo PAUSADO.")
            self.label_status.configure(text="Processo Pausado", text_color="#B77849")
        else:
            self.evento_pausa.set()
            self.botao_pausar.configure(text="Pausar", fg_color="#C0C1BC", hover_color="#A1A29D", text_color="#2C2D28")
            self.escrever_log("\n[AVISO] Processo RETOMADO!")
            self.label_status.configure(text="A transferir e processar...", text_color="#457297")

    def cancelar_processo(self):
        self.flag_cancelar = True
        self.evento_pausa.set()
        self.botao_cancelar.configure(state="disabled")
        self.botao_pausar.configure(state="disabled")
        self.escrever_log("\n[AVISO] A CANCELAR...")
        self.label_status.configure(text="A cancelar operação...", text_color="#935A5E")

    def pedir_codigo_2fa(self):
        dialog = ctk.CTkInputDialog(text="Introduza o código de 6 dígitos:", title="Segurança Apple (2FA)")
        return dialog.get_input()

    def iniciar_processamento(self):
        servico = self.controller.dados_redutor.get("servico")
        email = self.controller.dados_redutor.get("email")
        senha = self.controller.dados_redutor.get("senha")
        pasta = self.controller.dados_redutor.get("pasta")

        if servico == "iCloud":
            self.processar_icloud(email, senha, pasta)
        else:
            self.escrever_log("Serviço (Google Fotos) em desenvolvimento!")
            self.finalizar_ui("Serviço não implementado")

    def processar_uma_foto(self, foto, pasta_reduzidas):
        if self.flag_cancelar: return False, "Cancelado"
        self.evento_pausa.wait()
        if self.flag_cancelar: return False, "Cancelado"

        nome_ficheiro = foto.filename
        extensao = os.path.splitext(nome_ficheiro)[1].lower()
        if extensao not in ('.jpg', '.jpeg', '.png', '.heic', '.bmp', '.webp', '.dng', '.cr2', '.cr3', '.nef', '.arw',
                            '.rw2', '.orf', '.raf', '.raw'):
            return True, f"{nome_ficheiro} (Ignorado - Formato não suportado)"

        caminho_destino = os.path.join(pasta_reduzidas, f"{os.path.splitext(nome_ficheiro)[0]}.jpg")
        if os.path.exists(caminho_destino): return True, f"{nome_ficheiro} (Já existia)"

        try:
            download = foto.download()
            dados_brutos = ler_bytes_do_download(download)
            if not dados_brutos: return False, f"{nome_ficheiro} (Erro: dados vazios)"

            # Adiciona o peso do download
            with self.lock_stats:
                self.total_bytes_rede += len(dados_brutos)

            img = abrir_imagem_universal(dados_brutos, nome_ficheiro)
            with img:
                if img.mode in ("RGBA", "P", "CMYK"): img = img.convert("RGB")
                img.thumbnail((1920, 1920), Image.Resampling.LANCZOS)
                img.save(caminho_destino, "JPEG", quality=80, optimize=True)

            # Adiciona o peso do arquivo processado no disco local
            with self.lock_stats:
                self.total_bytes_armazenamento += os.path.getsize(caminho_destino)

            return True, nome_ficheiro
        except Exception as e:
            return False, f"{nome_ficheiro} (Erro: {e})"

    def processar_icloud(self, email, senha, pasta_reduzidas):
        try:
            self.escrever_log("A ligar aos servidores da Apple...")
            self.after(0, lambda: self.label_status.configure(text="A autenticar..."))

            api = PyiCloudService(email, senha)
            if api.requires_2fa:
                codigo = self.pedir_codigo_2fa()
                if not codigo or not api.validate_2fa_code(codigo):
                    self.escrever_log("[ERRO] Falha no 2FA.")
                    self.finalizar_ui("Erro de Autenticação")
                    return
                if not api.is_trusted_session: api.trust_session()

            self.after(0, lambda: self.label_status.configure(text="A procurar mídia..."))
            todas_as_fotos = api.photos.all
            total_arquivos = len(todas_as_fotos)
            if total_arquivos == 0:
                self.escrever_log("[AVISO] Nenhum ficheiro encontrado no iCloud.")
                self.finalizar_ui("Concluído (Vazio)")
                return

            self.escrever_log(f"Encontrados {total_arquivos} ficheiros. A iniciar processamento...\n")
            self.after(0, lambda: self.label_status.configure(text="A processar os ficheiros..."))
            os.makedirs(pasta_reduzidas, exist_ok=True)
            sucessos, erros, processados = 0, 0, 0

            with ThreadPoolExecutor(max_workers=5) as executor:
                futuros = [executor.submit(self.processar_uma_foto, foto, pasta_reduzidas) for foto in todas_as_fotos]
                for futuro in as_completed(futuros):
                    if self.flag_cancelar:
                        for f in futuros: f.cancel()
                        break
                    deu_certo, resultado = futuro.result()
                    processados += 1

                    porcentagem = (processados / total_arquivos) * 100
                    self.after(0, self.atualizar_progresso, processados / total_arquivos, f"{porcentagem:.2f}%")

                    if deu_certo:
                        sucessos += 1
                        self.escrever_log(f"[OK] {resultado}")
                    else:
                        erros += 1
                        self.escrever_log(f"[ERRO] {resultado}")

            if self.flag_cancelar:
                self.escrever_log("OPERAÇÃO CANCELADA PELO USUÁRIO.")
                self.finalizar_ui("Cancelado")
            else:
                self.escrever_log("PROCESSO RESK FINALIZADO COM SUCESSO!")
                self.finalizar_ui("Otimização Concluída!")

        except Exception as e:
            self.escrever_log(f"[ERRO FATAL] {str(e)}")
            self.finalizar_ui("Erro Fatal")

    def finalizar_ui(self, status_texto="Finalizado"):
        self.processando = False  # Desliga o loop de velocidade
        self.after(0, lambda: self.botao_pausar.configure(state="disabled"))
        self.after(0, lambda: self.botao_cancelar.configure(state="disabled"))
        self.after(0, lambda: self.botao_voltar.configure(state="normal"))
        self.after(0, lambda: self.label_status.configure(text=status_texto))