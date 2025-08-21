from fastapi import FastAPI, Request
import requests
from github import Github
from PIL import Image
from io import BytesIO
import tempfile
from moviepy.editor import VideoFileClip

app = FastAPI()

# -------------------------------
# CONFIGURAÇÃO (Substitua pelo seu)
# -------------------------------
TOKEN = "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"
REPO_OWNER = "Pecorine125"
REPO_NAME = "WallpaperAnimes"

g = Github(TOKEN)
repo = g.get_user(REPO_OWNER).get_repo(REPO_NAME)

PASTA_ANIME = "Wallpaper Anime"
PASTA_ANIMADO = "Wallpaper Animated"

# -------------------------------
# FUNÇÕES AUXILIARES
# -------------------------------
def redimensionar_imagem(content):
    with Image.open(BytesIO(content)) as img:
        img = img.resize((300,600))
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        return buffer.getvalue()

def redimensionar_video(content):
    with tempfile.NamedTemporaryFile(suffix=".mp4") as temp_in, tempfile.NamedTemporaryFile(suffix=".mp4") as temp_out:
        temp_in.write(content)
        temp_in.flush()
        clip = VideoFileClip(temp_in.name)
        clip_resized = clip.resize((300,600))
        clip_resized.write_videofile(temp_out.name, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        temp_out.seek(0)
        return temp_out.read()

# -------------------------------
# ENDPOINT
# -------------------------------
@app.post("/api/novo_wallpaper")
async def novo_wallpaper(request: Request):
    data = await request.json()
    url = data["url"]
    tipo = data["tipo"]
    number = str(data["number"])

    if tipo == "Wallpaper Animado":
        pasta = PASTA_ANIMADO
        ext = ".mp4"
    else:
        pasta = PASTA_ANIME
        ext = ".jpg"

    arquivo_nome = f"{tipo} {number}{ext}"
    repo_path = f"{pasta}/{arquivo_nome}"

    # Baixar conteúdo
    r = requests.get(url)
    r.raise_for_status()
    content = r.content

    # Redimensionar
    if tipo == "Wallpaper Anime":
        content = redimensionar_imagem(content)
    else:
        content = redimensionar_video(content)

    # Enviar para GitHub
    try:
        contents = repo.get_contents(repo_path)
        repo.update_file(contents.path, "Novo wallpaper", content, contents.sha)
    except:
        repo.create_file(repo_path, "Novo wallpaper", content)

    return {"status":"ok"}
