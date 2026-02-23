import pickle
from contextlib import closing
from pathlib import Path

import nltk
import mysql.connector
import tensorflow as tf
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymorphy3 import MorphAnalyzer
from nltk.corpus import stopwords
from keras.preprocessing.sequence import pad_sequences

BASE_DIR = Path(__file__).parent.parent
MODEL_PATH = BASE_DIR / "public" / "models" / "lstm_model.h5"
TOKENIZER_PATH = BASE_DIR / "public" / "models" / "tokenizer.pickle"

TARGET_NAMES = ['normal', 'insult', 'threat', 'obscenity']

morph = MorphAnalyzer()
stop_words = set(stopwords.words('russian'))
stop_words.update(["такой", "это", "всё", "весь"])

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
                   "http://0.0.0.0:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model = tf.keras.models.load_model(MODEL_PATH)
with open(TOKENIZER_PATH, 'rb') as f:
    tokenizer = pickle.load(f)
print("Модель и токенизатор загружены")

class TextRequest(BaseModel):
    text: str


def full_preprocess(text: str):
    """
    Токенизация, очистка и лемматизация текста
    """
    tokens = nltk.word_tokenize(text.lower())
    words = [t.replace('ё', 'е') for t in tokens if t.isalpha()]
    lemmas = [morph.parse(w)[0].normal_form for w in words]
    return [l for l in lemmas if l not in stop_words]


def get_prediction(text: str):
    clean_text = full_preprocess(text)
    seq = tokenizer.texts_to_sequences([clean_text])
    padded = pad_sequences(seq, maxlen=100)

    pred = model.predict(padded)[0]
    return {TARGET_NAMES[i]: float(pred[i]) for i in range(len(TARGET_NAMES))}


@app.post("/predict")
async def predict(request: TextRequest):
    text = request.text

    current_prediction = get_prediction(text)
    is_toxic = any(current_prediction[label] > 0.5 for label in TARGET_NAMES if label != 'normal')

    predicted_rows = {}

    with closing(mysql.connector.connect(host="localhost", user="root", password="1234", database="toxic_comments")) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                "INSERT INTO `toxic_comments`.`comments` (`comment`) VALUES (%s)",
                (text,)
            )
            conn.commit()

            cursor.execute("SELECT id_comment, comment FROM comments")
            rows = cursor.fetchall()

            for row_id, row_text in rows:
                predicted_rows[row_id] = {
                    'comment': row_text,
                    'prediction': get_prediction(row_text)
                }

    return {
        "text": text,
        "predictions": current_prediction,
        "is_toxic": is_toxic,
        "rows": predicted_rows
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)