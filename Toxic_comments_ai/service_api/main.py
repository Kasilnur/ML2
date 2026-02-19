import nltk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tensorflow as tf
import pickle
import numpy as np
from pymorphy3 import MorphAnalyzer
from nltk.corpus import stopwords
from keras.preprocessing.sequence import pad_sequences

morph = MorphAnalyzer()
my_stop_words = ["такой", "это", "всё", "весь"]
stop_words = set(stopwords.words('russian'))
stop_words.update(my_stop_words)

def full_preprocess(text):  
    # Токенизация
    tokens = nltk.word_tokenize(text.lower())
    # Очистка
    words = [t.replace('ё', 'е') for t in tokens if t.isalpha()]
    # Лемматизация
    lemmas = [morph.parse(w)[0].normal_form for w in words]
    # Удаление стоп-слов
    filtered_lemmas = [l for l in lemmas if l not in stop_words]
    
    return filtered_lemmas

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model = tf.keras.models.load_model('..\\public\\models\\lstm_model.h5')
with open('..\\public\\models\\tokenizer.pickle', 'rb') as f:
    tokenizer = pickle.load(f)

target_names = ['normal', 'insult', 'threat', 'obscenity']

class TextRequest(BaseModel):
    text: str

@app.post("/predict")
async def predict(request: TextRequest):
    clean_text = full_preprocess(request.text)
    
    seq = tokenizer.texts_to_sequences([clean_text])
    padded = pad_sequences(seq, maxlen=100)
    
    pred = model.predict(padded, verbose=0)[0]
    
    results = {target_names[i]: float(pred[i]) for i in range(len(target_names))}
    
    return {
        "text": request.text,
        "predictions": results,
        "is_toxic": any(results[label] > 0.5 for label in target_names if label != 'normal')
    }