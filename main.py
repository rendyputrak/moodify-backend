from fastapi import FastAPI
from database import engine, Base
from API import user_router, quote_router, music_dataset_router, mood_recap_router, mood_list_router, image_router, expression_analysis_router
from APISpotify import track_router
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from API.detect import detect_router 

app = FastAPI()

# Define OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")

# Define custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="MoodifyAPI",
        version="1.0.0",
        description="API untuk Moodify Mobile",
        routes=app.routes,
    )
    # Add security scheme to OpenAPI
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    # Apply security globally
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(user_router, tags=["User "])
app.include_router(quote_router, tags=["Quote"])
app.include_router(music_dataset_router, tags=["Music Dataset"])
app.include_router(image_router, tags=["Image"])
app.include_router(expression_analysis_router, tags=["Expression Analysis"])
app.include_router(track_router, tags=["Spotify"])
app.include_router(detect_router, tags=["Emotion Detection"]) 
app.mount("/images", StaticFiles(directory="images/user-faces"), name="images")
app.mount("/images", StaticFiles(directory="images/avatars"))

Base.metadata.create_all(bind=engine)