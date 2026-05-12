import os
import io
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

try:
    import rawpy
    RAWPY_DISPONIVEL = True
except ImportError:
    RAWPY_DISPONIVEL = False

def validar_permissao_escrita(pasta):
    arquivo_teste = os.path.join(pasta, ".teste_permissao_redutor")
    try:
        with open(arquivo_teste, 'w') as f:
            f.write("ok")
        os.remove(arquivo_teste)
        return True
    except Exception:
        return False

def ler_bytes_do_download(download):
    if download is None: return None
    if isinstance(download, (bytes, bytearray)): return bytes(download)
    if hasattr(download, 'raw') and hasattr(download.raw, 'read'): return download.raw.read()
    if hasattr(download, 'content'): return download.content
    if hasattr(download, 'read'): return download.read()
    return None

def abrir_imagem_universal(dados_brutos, nome_ficheiro):
    extensao = os.path.splitext(nome_ficheiro)[1].lower()
    FORMATOS_RAW = {'.dng', '.cr2', '.cr3', '.nef', '.arw', '.rw2', '.orf', '.raf', '.raw'}

    if extensao in FORMATOS_RAW:
        if not RAWPY_DISPONIVEL:
            raise ImportError("Formato RAW detectado mas 'rawpy' não está instalado.")
        with rawpy.imread(io.BytesIO(dados_brutos)) as raw:
            rgb_array = raw.postprocess(use_camera_wb=True, half_size=False, no_auto_bright=False, output_bps=8)
        return Image.fromarray(rgb_array)
    return Image.open(io.BytesIO(dados_brutos))