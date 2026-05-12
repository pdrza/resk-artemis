# 🌌 Resk Artemis

<p align="center">
  <img src="assets/resk.ico" width="120" alt="Resk Artemis Logo">
</p>

<p align="center">
  <strong>Um aplicativo moderno e elegante para baixar e otimizar fotos da nuvem diretamente para o seu armazenamento local.</strong>
</p>

---

## 📖 Sobre o Projeto

O **Resk Artemis** é uma ferramenta de desktop desenvolvida em Python que permite conectar-se a serviços de nuvem (atualmente focado na Apple iCloud), baixar suas fotos e **otimizá-las automaticamente**. 

Construído com uma interface gráfica moderna usando `customtkinter`, o aplicativo reduz o peso das imagens preservando a qualidade (redimensionamento inteligente e conversão para JPEG), ajudando você a economizar espaço precioso no seu disco rígido.

## ✨ Funcionalidades

* ☁️ **Integração Nativa com iCloud:** Faça login seguro na sua conta Apple, com suporte total a Autenticação de Dois Fatores (2FA).
* 🖼️ **Otimização Inteligente:** Redimensiona imagens maiores para um limite de 1920x1920px (JPEG, qualidade 80%), mantendo a excelência visual.
* 📸 **Suporte Avançado de Formatos:** Compatível com imagens comuns (JPG, PNG) e formatos de alta eficiência/profissionais como **HEIC** e **RAW** (DNG, CR2, NEF, ARW, etc.).
* ⚡ **Alta Performance:** Utiliza processamento multi-thread (`ThreadPoolExecutor`) para baixar e converter múltiplas fotos simultaneamente.
* 📊 **Dashboard em Tempo Real:** Acompanhe estatísticas precisas de velocidade de download (Rede), taxa de gravação no disco (Armazenamento) e progresso detalhado.
* 🎨 **Interface Premium:** Design limpo, minimalista e responsivo, configurado com um tema personalizado (`tema_artemis.json`).
* ⏸️ **Controle Total:** Pause, retome ou cancele a operação a qualquer momento.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** [Python 3.x](https://www.python.org/)
* **Interface Gráfica:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
* **Processamento de Imagem:** [Pillow](https://python-pillow.org/), [rawpy](https://pypi.org/project/rawpy/), [pillow-heif](https://pypi.org/project/pillow-heif/)
* **Integração de Nuvem:** [PyiCloud](https://github.com/picklepete/pyicloud)
* **Banco de Dados:** PostgreSQL (via `psycopg2`) para autenticação de usuários (módulo `auth.py`).

## 🚀 Como Instalar e Executar

### Pré-requisitos
Certifique-se de ter o Python instalado na sua máquina e, se planeja utilizar a integração com banco de dados, tenha um servidor PostgreSQL rodando localmente ou na nuvem.

### 1. Clone o repositório
```bash
git clone [https://github.com/seu-usuario/resk-artemis.git](https://github.com/seu-usuario/resk-artemis.git)
cd resk-artemis
