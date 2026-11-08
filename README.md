# DS Programming 1 最終個人課題

学籍番号：2622014　氏名：WANG BINGSEN

## 課題内容

- GitHub で Google が管理しているリポジトリ（https://github.com/google ）の情報をスクレイピングする
- 取得する情報：リポジトリ名、主要な言語、スターの数
- データを保存するための DB（SQLite）を作成し、スクレイピングしたデータを保存する
- GitHub の API は使わない
- アクセスごとに `time.sleep(1)` を入れる
- 保存したデータを SELECT 文で表示する

## ファイル構成

| ファイル | 内容 |
|---|---|
| `scrape_google_repos.py` | https://github.com/orgs/google/repositories を1ページずつ取得し、リポジトリ名・主要な言語・スター数を SQLite に保存する |
| `show_repos.py` | 保存したデータを SELECT 文で表示する（件数、スター数トップ20、言語ごとの件数、Python のスター数トップ10） |
| `db/google_repos.sqlite` | スクレイピング結果（2026年11月8日取得、2943件） |
| `requirements.txt` | 使ったライブラリ |

## DB のテーブル（repos）

| カラム | 型 | 内容 |
|---|---|---|
| id | INTEGER | 連番（主キー） |
| name | TEXT | リポジトリ名（重複しない） |
| language | TEXT | 主要な言語（ない場合は NULL） |
| stars | INTEGER | スターの数 |
| scraped_at | TEXT | 取得した日時 |

## 実行方法

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# スクレイピングしてDBに保存（全99ページ、1ページごとに time.sleep(1)）
python scrape_google_repos.py

# 保存したデータを表示
python show_repos.py
```

## 工夫したところ・困ったところ

- 一覧ページは画面のHTMLにリポジトリの行が直接書かれておらず、`<script data-target="react-app.embeddedData">` の中に JSON で入っていた。BeautifulSoup でこのタグを探し、`json.loads` で読んでいる（GitHub API は使っていない）。
- 続けてアクセスすると70ページ目あたりで `429 Too Many Requests` が返ってきた。`time.sleep(1)` に加えて、429 のときは60秒待ってやり直すようにした。
- 同じリポジトリを2回保存しないように、`name` を UNIQUE にして `INSERT OR REPLACE` を使った。
- 主要な言語がないリポジトリ（193件）は NULL で保存した。
