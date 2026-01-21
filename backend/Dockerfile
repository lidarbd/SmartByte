# בוחרים תמונת בסיס עם Python 3.11
FROM python:3.11-slim

# יוצרים תיקיית עבודה בתוך הקונטיינר
# כל הקוד שלנו יושב שם
WORKDIR /app

# מעתיקים את requirements.txt קודם
COPY requirements.txt .

# מתקינים את כל הספריות שרשומות ב-requirements
RUN pip install --no-cache-dir -r requirements.txt

# עכשיו מעתיקים את כל שאר הקוד
COPY . .

# אומרים לDocker שהאפליקציה מאזינה על פורט 8000
# זה לא פותח את הפורט, רק "מסמן" אותו
EXPOSE 8000

# הפקודה שתרוץ כשהקונטיינר מתחיל
# uvicorn מריץ את שרת FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]