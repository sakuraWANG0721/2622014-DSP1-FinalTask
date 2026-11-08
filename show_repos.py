import sqlite3

DB_FILE = "./db/google_repos.sqlite"

con = sqlite3.connect(DB_FILE)
cur = con.cursor()

# 1. 保存した件数
cur.execute("SELECT COUNT(*) FROM repos;")
print("保存したリポジトリ数:", cur.fetchone()[0])
print()

# 2. スターが多いリポジトリ トップ20
print("=== スター数 トップ20 ===")
cur.execute("SELECT name, language, stars FROM repos ORDER BY stars DESC LIMIT 20;")
for name, language, stars in cur.fetchall():
    print(f"{stars:>8}  {name}  ({language})")
print()

# 3. 主要な言語ごとのリポジトリ数 トップ10
print("=== 言語ごとのリポジトリ数 トップ10 ===")
cur.execute("""
SELECT language, COUNT(*) AS cnt
FROM repos
WHERE language IS NOT NULL
GROUP BY language
ORDER BY cnt DESC
LIMIT 10;
""")
for language, cnt in cur.fetchall():
    print(f"{cnt:>5}  {language}")
print()

# 4. Pythonのリポジトリでスターが多いもの トップ10
print("=== Python のリポジトリ スター数トップ10 ===")
cur.execute("""
SELECT name, stars
FROM repos
WHERE language = 'Python'
ORDER BY stars DESC
LIMIT 10;
""")
for name, stars in cur.fetchall():
    print(f"{stars:>8}  {name}")

con.close()
