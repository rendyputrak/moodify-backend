from fastapi import FastAPI
import models  
from database import engine, Base
from API import user_router, quote_router, music_dataset_router, mood_recap_router, mood_list_router, image_router, expression_analysis_router


app = FastAPI()

app.include_router(user_router)
app.include_router(quote_router)
app.include_router(music_dataset_router)
app.include_router(mood_recap_router)
app.include_router(mood_list_router)
app.include_router(image_router)
app.include_router(expression_analysis_router)

Base.metadata.create_all(bind=engine)