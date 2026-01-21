from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings

# יצירת אפליקציית FastAPI
app = FastAPI(
    title="SmartByte API",
    description="AI Sales Assistant for Computer Store",
    version="1.0.0"
)

# הגדרת CORS (כדי שה-Frontend יוכל לדבר עם ה-Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """
    נקודת כניסה בסיסית - לבדיקה שהשרת עובד
    """
    return {
        "message": "SmartByte API is running!",
        "llm_provider": settings.LLM_PROVIDER
    }


@app.get("/health")
def health_check():
    """
    בדיקת תקינות
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True  # לפיתוח - טוען מחדש אוטומטית על שינויים בקוד
    )