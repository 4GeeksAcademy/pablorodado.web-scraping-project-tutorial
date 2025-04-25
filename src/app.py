import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import io

# Conectamos
url = "https://en.wikipedia.org/wiki/List_of_Spotify_streaming_records"

solicitud = requests.get(url)

print (solicitud.status_code)

# Extraemos
html = io.StringIO(solicitud.text)
tablas = pd.read_html(html)

print(f"He encontrado {len(tablas)}, tablas en total")
# Comprobamos
df = tablas[0]

print(df)

print (df.head())
# Procesar y limpar datos

df.columns = ["Rank, Song, Artists, Streams(billions),Release date, Reference)"]
# Repasar pandas , no  sabria hacerlo solo   no entiendo regex y errors coerce 
df["Song"] = df["Song"].str.replace(r"\[.*?\]", "", regex=True)
df["Artist"] = df["Artist"].str.replace(r"\[.*?\]", "", regex=True)

df = df[df["Streams (billions)"].astype(str).str.contains(r"^\d+(?:\.\d+)?$", na=False)].copy()

df["Streams (billions)"] = df["Streams (billions)"].astype(float)
df["Date released"] = pd.to_datetime(df["Date released"], errors="coerce")


df


# A partir de aqui ya voy cojo

conn = sqlite3.connect("spotify_top_songs.db") # creas base de datos pero por que ese link?
df.to_sql("most_streamed", conn, if_exists="replace", index=False)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM most_streamed")
print("Rows inserted:", cursor.fetchone()[0])

conn.commit()
conn.close()

# NO ME DEJA AÑADIR UNA CAJA, NO PUEDO VER MAS ALLA DEL TERMINAL

top10 = df.nlargest(10, "Streams (billions)")
plt.figure(figsize=(12, 6))
sns.barplot(data=top10, x="Streams (billions)", y="Song", hue="Song", palette="viridis", legend=False)
plt.title("Las 10 canciones más reproducidas en Spotify")
plt.xlabel("Reproducciones (en miles de millones)")
plt.ylabel("Canción")
plt.tight_layout()
plt.show()