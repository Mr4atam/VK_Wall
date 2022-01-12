import json
import os.path
import requests

from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("TOKEN")
POST_COUNT = 10

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--count", required=False)
args = parser.parse_args()

# Проверяем наличия существующих директорий
def check_dir(dir_name):
    if os.path.exists(f'{dir_name}'):
        print(f"Директория с именем {dir_name} уже существует!")
    else:
        os.mkdir(dir_name)

def get_wall_posts(group_name):
    params = {
        'domain': group_name,
        'count': args.count or POST_COUNT,
        'access_token': TOKEN,
        'v': '5.131'
    }
    req = requests.get('http://api.vk.com/method/wall.get', params=params)
    src = req.json()

    check_dir(group_name)

    # Сохраняем данные в json файл, чтобы видеть структуру
    with open(f"{group_name}/{group_name}.json","w", encoding="utf-8") as file:
        json.dump(src, file, indent=4, ensure_ascii=False)

    # Собираем ID новых постов  в список
    fresh_posts_id = []
    posts = src['response']['items']

    for fresh_post_id in posts:
        fresh_post_id = fresh_post_id["id"]
        fresh_posts_id.append(fresh_post_id)

    # Проверка, если файла не существует, значит это первый парсинг (отправляем все новые фото).
    # Иначе начинаем проверку и отправляем только новые фото
    if not os.path.exists(f"{group_name}/exist_posts_{group_name}.txt"):
        print("Файла с таким ID не существует, создаем файл!")

        with open(f"{group_name}/exist_posts_{group_name}.txt", "w") as file:
            for item in fresh_posts_id:
                file.write(str(item) + "\n")

        # Извлекаем данные из постов
        for post in posts:
            post_id = post['id']
            print(f'Отправляем пост с ID {post_id}')

            try:
                if "attachments" in post:
                    post = post['attachments']

                    if post[0]['type'] == "photo":
                        for post_item_photo in post:
                            post_photo = post_item_photo["photo"]['sizes']
                            desired_photo = max(post_photo, key=lambda x: x['height'])
                            photo_url = desired_photo['url']
                            print(photo_url)

            except Exception:
                print(f"Что-то пошло не так c запросом ID {post_id}!")

    else:
        print("Файл существует, начинаем обрабатывать свежее!")

def main():
    group_name = input("Enter group name: ")
    get_wall_posts(group_name)

if  __name__ == "__main__":
    main()
