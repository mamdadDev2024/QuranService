import requests
import pymysql
import time
import sys

# === مشخصات کلاینت ===
CLIENT_ID = 'bbe41d09-b85f-48ac-9b17-1562a2c73ccf'
CLIENT_SECRET = 'yJVy82v21uBZoxPLrU3X-.PIrI'

# === آدرس‌ها ===
TOKEN_URL = 'https://prelive-oauth2.quran.foundation/oauth2/token'
API_BASE = 'https://apis-prelive.quran.foundation/content/api/v4/'

# تنظیم کانکشن دیتابیس
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        db='quranservice',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

access_token = None
token_expires_at = 0

def get_access_token():
    global access_token, token_expires_at
    if access_token and time.time() < token_expires_at - 60:
        return access_token

    try:
        auth = (CLIENT_ID, CLIENT_SECRET)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'grant_type': 'client_credentials', 'scope': 'content'}
        print("Requesting new access token...")
        resp = requests.post(TOKEN_URL, headers=headers, data=data, auth=auth, timeout=10)
        resp.raise_for_status()
        token_data = resp.json()
    except requests.RequestException as e:
        print(f"[ERROR] Failed to get access token: {e}", file=sys.stderr)
        raise

    access_token = token_data.get('access_token')
    if not access_token:
        raise Exception("Access token not found in response")

    expires_in = token_data.get('expires_in', 3600)
    token_expires_at = time.time() + expires_in
    print(f"[INFO] Got access token, expires in {expires_in} seconds")
    return access_token

def get_headers():
    token = get_access_token()
    return {
        'x-auth-token': token,
        'x-client-id': CLIENT_ID,
        'Accept': 'application/json',
    }

def fetch_data(endpoint, key):
    url = API_BASE + endpoint
    try:
        print(f"[INFO] Fetching {endpoint} ...")
        resp = requests.get(url, headers=get_headers(), timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch {endpoint}: {e}", file=sys.stderr)
        raise
    except ValueError:
        print(f"[ERROR] Response JSON decode error on {endpoint}", file=sys.stderr)
        raise

    if key not in data:
        raise Exception(f"Key '{key}' not found in response for {endpoint}")

    return data[key]

def fetch_verses(surah_num, page=1):
    url = f"{API_BASE}verses/by_chapter/{surah_num}"
    params = {
        'language': 'en',
        'words': 'true',
        'translations': 131,
        'audio': 1,
        'per_page': 50,
        'page': page
    }
    try:
        print(f"[INFO] Fetching verses for surah {surah_num} page {page} ...")
        resp = requests.get(url, headers=get_headers(), params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch verses for surah {surah_num} page {page}: {e}", file=sys.stderr)
        raise
    except ValueError:
        print(f"[ERROR] Response JSON decode error for verses surah {surah_num} page {page}", file=sys.stderr)
        raise

    if 'verses' not in data or 'pagination' not in data:
        raise Exception(f"Missing keys in verses response for surah {surah_num} page {page}")

    return data

def seed_all():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # درج جزء‌ها
            juzs = fetch_data('juzs', 'juzs')
            print(f"[INFO] Inserting {len(juzs)} juzs ...")
            for juz in juzs:
                try:
                    cur.execute(
                        "INSERT IGNORE INTO juzs (number, text, created_at, updated_at) VALUES (%s, %s, NOW(), NOW())",
                        (juz['id'], juz.get('title', f"Juz {juz['id']}"))
                    )
                except Exception as e:
                    print(f"[WARNING] Failed to insert juz {juz['id']}: {e}", file=sys.stderr)
            conn.commit()

            # درج حزب‌ها
            hizbs = fetch_data('hizbs', 'hizbs')
            print(f"[INFO] Inserting {len(hizbs)} hizbs ...")
            for hizb in hizbs:
                try:
                    cur.execute(
                        "INSERT IGNORE INTO hizbs (number, text, created_at, updated_at) VALUES (%s, %s, NOW(), NOW())",
                        (hizb['id'], hizb.get('title', f"Hizb {hizb['id']}"))
                    )
                except Exception as e:
                    print(f"[WARNING] Failed to insert hizb {hizb['id']}: {e}", file=sys.stderr)
            conn.commit()

            # درج سوره‌ها
            chapters = fetch_data('chapters', 'chapters')
            print(f"[INFO] Inserting {len(chapters)} chapters ...")
            for chap in chapters:
                try:
                    cur.execute(
                        "INSERT IGNORE INTO surahs (number, name, place, text, created_at, updated_at) VALUES (%s, %s, %s, %s, NOW(), NOW())",
                        (chap['id'], chap['name_arabic'], chap['revelation_place'], chap['name_simple'])
                    )
                except Exception as e:
                    print(f"[WARNING] Failed to insert chapter {chap['id']}: {e}", file=sys.stderr)
            conn.commit()

            # ساخت مپ‌ها
            cur.execute("SELECT id, number FROM surahs")
            surah_map = {row['number']: row['id'] for row in cur.fetchall()}

            cur.execute("SELECT id, number FROM hizbs")
            hizb_map = {row['number']: row['id'] for row in cur.fetchall()}

            cur.execute("SELECT id, number FROM pages")
            page_map = {row['number']: row['id'] for row in cur.fetchall()}

            # درج آیات و کلمات
            for chap in chapters:
                surah_num = chap['id']
                surah_id = surah_map.get(surah_num)
                if surah_id is None:
                    print(f"[WARNING] Surah id not found in DB map for surah number {surah_num}", file=sys.stderr)
                    continue

                page = 1
                while True:
                    try:
                        data = fetch_verses(surah_num, page)
                    except Exception as e:
                        print(f"[ERROR] Skipping verses for surah {surah_num} page {page} due to error: {e}", file=sys.stderr)
                        break

                    verses = data.get('verses', [])
                    if not verses:
                        print(f"[INFO] No more verses for surah {surah_num} at page {page}")
                        break

                    for v in verses:
                        try:
                            page_number = v.get('page_number')
                            if page_number is None:
                                print(f"[WARNING] Verse {v.get('id')} missing page_number, skipping", file=sys.stderr)
                                continue

                            page_text = v.get('image_url', '')

                            # وارد کردن صفحه اگر موجود نبود
                            if page_number not in page_map:
                                cur.execute(
                                    "INSERT IGNORE INTO pages (number, text, created_at, updated_at) VALUES (%s, %s, NOW(), NOW())",
                                    (page_number, page_text)
                                )
                                conn.commit()
                                cur.execute("SELECT id FROM pages WHERE number = %s", (page_number,))
                                row = cur.fetchone()
                                if row is None:
                                    print(f"[WARNING] Page id not found after insert for page number {page_number}", file=sys.stderr)
                                    continue
                                page_id = row['id']
                                page_map[page_number] = page_id
                            else:
                                page_id = page_map[page_number]

                            hizb_number = v.get('hizb_number')
                            hizb_id = hizb_map.get(hizb_number) if hizb_number is not None else None

                            # درج آیه
                            cur.execute(
                                "INSERT IGNORE INTO verses (global_number, local_number, surah_id, hizb_id, page_id, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())",
                                (v['id'], v['verse_number'], surah_id, hizb_id, page_id)
                            )

                            # گرفتن شناسه آیه
                            cur.execute("SELECT id FROM verses WHERE global_number = %s", (v['id'],))
                            row = cur.fetchone()
                            if row is None:
                                print(f"[WARNING] Verse ID not found after insert for global_number {v['id']}", file=sys.stderr)
                                continue
                            verse_id = row['id']

                            # درج کلمات
                            for w in v.get('words', []):
                                translation = w.get('translation', {}).get('text') if w.get('translation') else None
                                cur.execute(
                                    "INSERT IGNORE INTO words (position, text, translation, verse_id, created_at, updated_at) VALUES (%s, %s, %s, %s, NOW(), NOW())",
                                    (w['position'], w['code_v1'], translation, verse_id)
                                )

                        except Exception as e:
                            print(f"[WARNING] Failed processing verse {v.get('id')}: {e}", file=sys.stderr)

                    conn.commit()

                    if not data.get('pagination', {}).get('next_page'):
                        print(f"[INFO] Completed fetching verses for surah {surah_num}")
                        break

                    page += 1

        print("[SUCCESS] Data seeding completed successfully.")

    except Exception as e:
        print(f"[FATAL ERROR] {e}", file=sys.stderr)
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    seed_all()
