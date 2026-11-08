import json
import os
import sqlite3
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

# GoogleのGitHubリポジトリ一覧ページ（?page=2 のようにページ番号を付ける）
BASE_URL = "https://github.com/orgs/google/repositories"

# 保存先のDBファイル
DB_FILE = "./db/google_repos.sqlite"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def create_table(cur):
    # リポジトリ情報を入れるテーブルを作る（既にあれば作らない）
    sql = """
    CREATE TABLE IF NOT EXISTS repos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        language TEXT,
        stars INTEGER,
        scraped_at TEXT
    );
    """
    cur.execute(sql)


def get_page_data(page):
    # 1ページ分のHTMLを取得する
    # 続けてアクセスすると 429 (Too Many Requests) が返ることがあるので、
    # そのときは少し長めに待ってからやり直す（最大5回）
    for i in range(5):
        res = requests.get(BASE_URL, params={"page": page}, headers=headers, timeout=15)
        if res.status_code != 429:
            break
        wait = 60
        print(f"  429が返ったので {wait} 秒待ってやり直します")
        time.sleep(wait)
    res.raise_for_status()

    # このページは一覧のデータをHTMLの中の<script>タグ(JSON)に入れているので、
    # BeautifulSoupでそのタグを探して、中身をJSONとして読む
    soup = BeautifulSoup(res.text, "html.parser")
    script = soup.find("script", attrs={"data-target": "react-app.embeddedData"})
    data = json.loads(script.string)
    return data["payload"]["orgReposPageRoute"]


def main():
    # dbフォルダがなければ作る
    os.makedirs("./db", exist_ok=True)
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    create_table(cur)

    sql_insert = """
    INSERT OR REPLACE INTO repos (name, language, stars, scraped_at)
    VALUES (?, ?, ?, ?)
    """

    page = 1
    page_count = 1  # 1ページ目を読んだら本当のページ数に更新する
    total = 0

    while page <= page_count:
        route = get_page_data(page)
        page_count = route["pageCount"]

        rows = []
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for repo in route["repositories"]:
            name = repo["name"]
            # 主要な言語がないリポジトリもあるので、そのときはNoneにする
            if repo["primaryLanguage"] is None:
                language = None
            else:
                language = repo["primaryLanguage"]["name"]
            stars = repo["starsCount"]
            rows.append((name, language, stars, now))

        cur.executemany(sql_insert, rows)
        con.commit()
        total += len(rows)
        print(f"{page}/{page_count} ページ目: {len(rows)} 件保存（合計 {total} 件）")

        page += 1
        # サーバーに負担をかけないように、1回アクセスするごとに1秒待つ
        time.sleep(1)

    con.close()
    print("スクレイピング終了")


if __name__ == "__main__":
    main()
