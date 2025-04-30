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

print(f"He encontrado {len(tablas)} tablas en total")
# Comprobamos
df = tablas[0]

print (df.head())

# Limpiamos con regex

df.columns = ["Rank", "Song", "Artist", "Streams (billions)", "Date released", "Reference"]

df["Song"] = df["Song"].str.replace(r"\[.*?\]", "", regex=True)
df["Artist"] = df["Artist"].str.replace(r"\[.*?\]", "", regex=True)

df = df[df["Streams (billions)"].astype(str).str.contains(r"^\d+(?:\.\d+)?$", na=False)].copy()


df["Streams (billions)"] = df["Streams (billions)"].astype(float)


df["Date released"] = pd.to_datetime(df["Date released"], errors="coerce")

print(df)

# OK

# Crear base de datos y guardarla en sqlite

conn = sqlite3.connect("top_canciones_spotify.db")
df.to_sql("las_mas_reproducidas", conn, if_exists="replace", index=False)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM las_mas_reproducidas")
print("Rows inserted:", cursor.fetchone()[0])

conn.commit()
conn.close()


# Visualizar
top10 = df.nlargest(10, "Streams (billions)")
plt.figure(figsize=(14, 7))
sns.barplot(data=top10, x="Streams", y="Song", hue="Song", palette="viridis", legend=False)
plt.title("Las 10 canciones más reproducidas en Spotify")
plt.xlabel("Reproducciones (en miles de millones)")
plt.ylabel("Canción")
plt.tight_layout()
plt.savefig('top10_spotify.png')
plt.show()


