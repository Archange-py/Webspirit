# server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from fastapi.responses import FileResponse

# Modèle de Bookmark
class Bookmark(BaseModel):
    url: str
    title: str
    collection: str = ""
    tags: List[str] = []

app = FastAPI()

# Activer CORS pour accepter les requêtes de l'extension et de la page web locale
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Autoriser toutes les origines en local
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stockage en mémoire des bookmarks (liste de dict)
bookmarks: List[Bookmark] = []
@app.post("/api/bookmarks")
def add_bookmark(bm: Bookmark):
    """
    Ajoute un nouveau bookmark envoyé depuis l'extension ou l'interface.
    """
    bookmarks.append(bm)
    return {"message": "Bookmark ajouté avec succès"}

@app.get("/api/bookmarks")
def get_bookmarks():
    """
    Renvoie la liste de tous les bookmarks sous forme JSON.
    """
    return bookmarks

@app.get("/")
def root():
    """
    Sert le fichier index.html de l'interface web.
    """
    return FileResponse("frontend/index.html")