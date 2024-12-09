import json
import os
import base64
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import requests
from sqlalchemy.orm import Session
from models.music_dataset import MusicDataset  # Pastikan mengimpor kelas model
from database import get_db  # Fungsi untuk mendapatkan sesi database

router = APIRouter()

# Memuat variabel lingkungan
load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

def get_token():
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = requests.post(url, data=data, headers=headers)
    
    if result.status_code != 200:
        raise HTTPException(status_code=500, detail="Error fetching token from Spotify")

    json_result = json.loads(result.content)
    return json_result["access_token"]

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def get_track_url(token, track_id):
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers = get_auth_header(token)

    result = requests.get(url, headers=headers)
    if result.status_code != 200:
        return None

    json_result = json.loads(result.content)
    return json_result.get("external_urls", {}).get("spotify", None)

# Endpoint untuk memperbarui SongUrl berdasarkan SpotifyID
@router.put("/update-song-urls")
async def update_song_urls(db: Session = Depends(get_db)):
    try:
        # Mendapatkan token autentikasi Spotify
        token = get_token()

        # Query untuk mendapatkan semua entri tanpa SongUrl
        music_datasets = db.query(MusicDataset).filter((MusicDataset.SongUrl == None) | (MusicDataset.SongUrl == "")).all()

        updated_count = 0
        for music in music_datasets:
            # Ambil URL track dari Spotify
            track_url = get_track_url(token, music.SpotifyID)

            # Jika URL ditemukan, perbarui kolom SongUrl
            if track_url:
                music.SongUrl = track_url
                db.add(music)
                updated_count += 1

        # Simpan semua perubahan ke database
        db.commit()

        return {"message": f"Updated {updated_count} SongUrl(s)."}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
