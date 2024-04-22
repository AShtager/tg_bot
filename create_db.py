import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Client(Base):
    __tablename__ = "client"

    id = sq.Column(sq.Integer(), primary_key=True)
    id_client = sq.Column(sq.BigInteger(), nullable=False)

    def __str__(self):
        return f"{Client.id}"


class UserWordRu(Base):
    __tablename__ = "user_word_ru"

    id = sq.Column(sq.Integer(), primary_key=True)
    id_client = sq.Column(sq.Integer(), sq.ForeignKey("client.id"), nullable=False)
    word = sq.Column(sq.String(length=255), nullable=False)

    client = relationship(Client, backref="client")


class CommonWords(Base):
    __tablename__ = "common_word_ru" 

    id = sq.Column(sq.Integer(), primary_key=True)
    word = sq.Column(sq.String(length=255), nullable=False)


class SetWordsEn(Base):
    __tablename__ = "set_word_en"

    id = sq.Column(sq.Integer(), primary_key=True)
    word = sq.Column(sq.String(length=255), nullable=False)


def create_table(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
