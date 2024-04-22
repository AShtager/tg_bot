import sqlalchemy as sq
import requests
import json
import os
import random
from sqlalchemy.orm import sessionmaker
from  sqlalchemy.sql.expression import func
from create_db import Client, UserWordRu, CommonWords, SetWordsEn, create_table 
from dotenv import load_dotenv
load_dotenv()

LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
NAME_DB = os.getenv("NAME_DB")
TYPE_DB = os.getenv("TYPE_DB")
YANTOKEN = os.getenv("YANTOKEN")

DSN = f"{TYPE_DB}://{LOGIN}:{PASSWORD}@{HOST}/{NAME_DB}"
engine = sq.create_engine(url=DSN)

Session = sessionmaker(bind=engine)
session = Session()

def record_db(file):
    with open(file, encoding="utf-8") as f:
        data = json.load(f)

    for row in data:
        table = {
            "common_words": CommonWords,
            "set_words_en": SetWordsEn,
        }
        table_class = table[row.get("model")]
        session.add(table_class(id=row.get("pk"), word=row.get("word")))
    session.commit()
    
def random_words():
    set_word = session.query(SetWordsEn.word).order_by(func.random()).limit(3)
    return list(word for (word,) in set_word)

def word_ru(user_id=None):
    pk_user = session.query(Client.id).filter_by(id_client=user_id).first()
    word_common = session.query(CommonWords.word)
    word_user = session.query(UserWordRu.word).filter(UserWordRu.id_client == pk_user[0])
    query = sq.union(word_common, word_user)
    with engine.connect() as conn:
        result = conn.execute(query).all()
    return random.choice(result)[0]

def translator(word):
    url = 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup'
    params ={
        "key": YANTOKEN,
        "lang": "ru-en",
        "text": word
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        word_attrib = response.json()
        trans_word = word_attrib["def"][0]["tr"][0]["text"]
        return trans_word
    else:
        return "Возникла не предвиденная ошибка"
    
def added_user(id_user):
    verification = session.query(Client.id_client).filter_by(id_client=id_user).first()
    if verification is None:
        user = Client(id_client=id_user)
        session.add(user)
        session.commit()
    else:
        pass

def added_word(id_user=None, word=None):
    pk_user = session.query(Client.id).filter_by(id_client=id_user).first()
    user_word = UserWordRu(id_client=int(pk_user[0]), word=word)
    session.add(user_word)
    session.commit()

def delete_word(id_user=None, word=None):
    pk_user = session.query(Client.id).filter_by(id_client=id_user).first()
    session.query(UserWordRu).filter(UserWordRu.id_client == int(pk_user[0]), UserWordRu.word == word).delete()
    session.commit()
    

session.close()

if __name__ == "__main__":
    create_table(engine)
    record_db("data.json")
    
