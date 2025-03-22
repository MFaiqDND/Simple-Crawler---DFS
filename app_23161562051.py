import requests
from bs4 import BeautifulSoup
import pymysql
pymysql.install_as_MySQLdb()

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password=""
    )
    cursor = conn.cursor()
    print("[INFO] Koneksi ke MySQL berhasil.")
except pymysql.MySQLError as err:
    print(f"[ERROR] Gagal koneksi ke MySQL: {err}")
    exit()

cursor.execute("CREATE DATABASE IF NOT EXISTS Webfaiq;")
print("[INFO] Database `Webfaiq` siap.")

cursor.close()
conn.close()

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="Webfaiq"
    )
    cursor = conn.cursor()
    print("[INFO] Koneksi ke database `Webfaiq` berhasil.")
except pymysql.MySQLError as err:
    print(f"[ERROR] Gagal koneksi ke database: {err}")
    exit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Scraper (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(255),
    judul_artikel VARCHAR(255),
    paragraf TEXT
)
""")
print("[INFO] Tabel `Scraper` siap.")

visited = set()

def dfs(url):
    if url in visited:
        print(f"[SKIP] {url} sudah dikunjungi.")
        return
    visited.add(url)

    print(f"[INFO] Mengunjungi: {url}")

    # Request halaman
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"[WARNING] Gagal mengakses {url} (Status: {response.status_code})")
            return
    except requests.RequestException as e:
        print(f"[ERROR] Request error: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    judul_artikel = soup.find("h1").string if soup.find("h1") else "tidak ada judul"
    paragraf = soup.find("p").text if soup.find("p") else "tidak ada paragraf"

    print(f"[INFO] Menyimpan ke database: {judul_artikel}")

    cursor.execute("INSERT INTO web_data (url, judul_artikel, paragraf) VALUES (%s, %s, %s)", (url, judul_artikel, paragraf))
    conn.commit()

    for link in soup.find_all("a", href=True):
        next_url = "http://localhost:8000/" + link["href"]
        if next_url not in visited:
            dfs(next_url)

print("[INFO] Memulai DFS...")
dfs("http://localhost:8000/index.html")

cursor.close()
conn.close()
print("[INFO] Selesai.")
