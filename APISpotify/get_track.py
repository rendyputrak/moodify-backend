import json
import os
import base64
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import requests

router = APIRouter()

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
    token = json_result["access_token"]
    # print(f"Fetched Token: {token}")  # Debugging token fetching
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def get_track_url(token, track_id):
    try:
        # Memperbaiki URL dengan format string untuk track_id
        url = f"https://api.spotify.com/v1/tracks/{track_id}"
        headers = get_auth_header(token)

        result = requests.get(url, headers=headers)

        # Debugging status code and response
        print(f"Response Status Code: {result.status_code}")
        print(f"Response Content: {result.content}")

        if result.status_code != 200:
            raise HTTPException(status_code=500, detail="Error fetching URL from Spotify")

        json_result = json.loads(result.content)

        # Debugging structure of the response JSON
        print(f"JSON Result: {json_result}")

        # Memeriksa apakah ada 'external_urls' dalam respon
        if 'external_urls' in json_result:
            return json_result["external_urls"]["spotify"]  # Mengambil URL Spotify eksternal
        else:
            print(f"No external URL found for track: {track_id}")  # Debugging line
            return None
    except Exception as e:
        print(f"Error in get_track_url: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching track URL")

# Implementasi endpoint FastAPI untuk mengambil track URL
@router.get("/get-track")
async def get_track_endpoint(id: str):
    try:
        # Ambil token untuk autentikasi
        token = get_token()

        # Ambil URL track berdasarkan id
        track_url = get_track_url(token, id)

        # Jika tidak ditemukan URL eksternal
        if track_url is None:
            return JSONResponse(status_code=404, content={"message": "URL not found"})

        # Jika ditemukan URL, kembalikan URL tersebut dalam response
        return {"track_url": track_url}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

