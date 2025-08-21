from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import requests, os, base64
from github import Github
from PIL import Image
from io import BytesIO
import tempfile
from moviepy.editor import VideoFileClip

app = FastAPI()

# -------------------------------
# CONFIGURAÇÕES SEGURAS (via ENV)
# -------------------------------
TOKEN = os.environ["GITHUB_TOKEN"]
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]
ADMIN_USER = os.environ["ADMIN_USER"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]

g = Github(TOKEN)
repo = g.get_user("Pecorine125").get_repo("WallpaperAnimes")

PASTA_ANIME = "Wallpaper Anime"
PASTA_ANIMADO = "Wallpaper Animated"

endpoint_ativo = True

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

def validar_auth(request: Request):
    auth = request.headers.get("Authorization")
    if auth is None or not auth.startswith("Basic "):
        raise HTTPException(status_code=401, detail="Não autorizado")
    decoded = base64.b64decode(auth.split(" ")[1]).decode("utf-8")
    user, password = decoded.split(":")
    if user != ADMIN_USER or password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Não autorizado")

# -------------------------------
# WEBHOOK / API
# -------------------------------
@app.post("/api/novo_wallpaper")
async def novo_wallpaper(request: Request):
    global endpoint_ativo
    if not endpoint_ativo:
        return JSONResponse({"status":"desativado"})

    data = await request.json()
    if data.get("secret") != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Chave secreta inválida")

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

    r = requests.get(url)
    r.raise_for_status()
    content = r.content

    if tipo == "Wallpaper Anime":
        content = redimensionar_imagem(content)
    else:
        content = redimensionar_video(content)

    try:
        contents = repo.get_contents(repo_path)
        repo.update_file(contents.path, "Novo wallpaper", content, contents.sha)
    except:
        repo.create_file(repo_path, "Novo wallpaper", content)

    return JSONResponse({"status":"ok"})

# -------------------------------
# TOGGLE / ATIVAR-DESATIVAR
# -------------------------------
@app.post("/api/toggle")
async def toggle(request: Request):
    try:
        validar_auth(request)
    except HTTPException as e:
        return JSONResponse({"status": "erro", "detail": e.detail}, status_code=401)

    global endpoint_ativo
    endpoint_ativo = not endpoint_ativo
    return JSONResponse({"status": endpoint_ativo})

# -------------------------------
# DASHBOARD HTML
# -------------------------------
@app.get("/dashboard")
async def serve_dashboard(request: Request):
    try:
        validar_auth(request)
    except HTTPException as e:
        return JSONResponse({"status": "erro", "detail": e.detail}, status_code=401)
    return FileResponse("public/index.html")
