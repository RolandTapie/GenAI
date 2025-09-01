from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import pandas as pd
import os
load_dotenv()
# Lire les variables d'environnement
DB_HOST = os.getenv("DB_HOST")
DB_PORT=os.getenv("DB_PORT")
DB_USER= os.getenv("DB_USER")
DB_PWD = os.getenv("DB_PWD")
DB_DATABASE = os.getenv("DB_DATABASE")

def format_txt(df):
    title = f" vous avez {len(df)} créance(s) ouvertes: \n la liste des créances ouvertes:\n"
    formatted = "\n".join(
        f" {row[1]}, {row[2]} ,  {row[3]}"
        for row in df.itertuples(index=False)
    )
    return title + formatted

def format_json(df):
    formatted = df.iloc[:, 1:4].to_json(orient="records", force_ascii=False, indent=2)
    return formatted


def f_get_data(id: str):
    """
    :param id: identifiant du redevable
    :return: la liste des créances ou des transactions encore ourvertes
    """
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
    # Création du moteur de connexion
    engine = create_engine(DATABASE_URL)

    # Test de la connexion
    query = text("SELECT * FROM transactions WHERE journal = :id")
    with engine.connect() as connection:
        result = pd.read_sql(query, connection, params={"id": id})

    if result.empty:
        return "la redevable n'a aucune transaction"

    return format_txt(result)

#print(get_data("VDL-000031333"))