from bs4 import BeautifulSoup
from urllib import parse
from pathlib import Path

import csv
import config
import os
import requests
import sys
import time

# .env設定を確認
MIRAMEET_CONNPASS_URL = config.MIRAMEET_CONNPASS_URL


# イベントページをスクレイピングして、イベントタイトルとイベント参加者一覧のリンク返す。
def get_event(url):
    try:
        # getHTML
        r = requests.get(url)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        # event_title
        event_title = soup.find('h2', class_='event_title').contents[2].replace('\n', '').strip()
        event_title = event_title.replace('/', ' ')
        # attendee
        attendees_link = soup.find('p', class_="p text_right").find('a').get('href')
    # 404エラーハンドリング
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)
    # 一致タグ、クラス名が存在しなかった際のエラーハンドリング
    except AttributeError as e:
        print(e)
        sys.exit(1)
    return event_title, attendees_link


# イベント参加者一覧ページから参加者名、各SNSのリンクが含まれるタグに絞って取得する
# （aタグで狙いのものは全部取れそうだったので今回はaタグに絞る）
def get_event_attendees(attendees_link):
    # getHTML
    time.sleep(2.0)
    tag_attendees_info = []
    try:
        r = requests.get(attendees_link)
        soup = BeautifulSoup(r.text, 'html.parser')
        tag_attendees_info_list = soup.findAll('div', class_='participation_table_area mb_20')
        for i in tag_attendees_info_list:
            tag_attendees_info.extend(i.findAll('a'))
            # デバッグ用
            # print(tag_attendees_info)
    # 一致タグ、クラス名が存在しなかった際のエラーハンドリング
    except AttributeError as e:
        print(e)
        sys.exit(1)
    return tag_attendees_info


# get_event_attendeesで取得内容を整形（空白、改行の削除）
# list[dict]で格納
def attendee_list_forming(attendee):
    attendee_list = []
    for content in attendee:
        if len(content.get_text().replace('\n', '')) != 0:
            d = {'Name': None, 'github': None, 'twitter': None, 'facebook': None}
            d['Name'] = content.get_text()
            attendee_list.append(d)
        elif 'github' in content.get('href'):
            d['github'] = content.get('href')
        elif 'twitter' in content.get('href'):
            d['twitter'] = content.get('href')
        elif 'facebook' in content.get('href'):
            d['facebook'] = content.get('href')
        else:
            pass

    return attendee_list


def output_for_csv(f_path, dct_list):
    # csv_header
    labels = ['Name', 'github', 'twitter', 'facebook']
    try:
        with open(f_path, 'w', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=labels)
            writer.writeheader()
            print(">>>\n")
            for elem in dct_list:
                print(elem)
                writer.writerow(elem)
            print("\n>>>")
    except IOError as e:
        # ファイルパス名のエラーなど
        print("I/O error")
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    val = input("Please input eventPageURL or eventID >> ")
    while val:
        if val.isdigit():
            print("event_id: " + val)
            url = MIRAMEET_CONNPASS_URL + val
            break
        elif parse.urlparse(val):
            print("eventPageURL: " + val)
            url = val
            break
        else:
            val = input("Please input URL or eventID >> ")

    e_title, a_link = get_event(url)
    tag_attendees = get_event_attendees(a_link)
    attendee_dct_list = attendee_list_forming(tag_attendees)

    # output存在確認
    if not os.path.exists('../output'):
        os.mkdir('../output')
    # 親ディレクトリ取得
    path = Path(__file__).parent
    # Path連結
    path /= '../output/' + e_title + '.csv'
    # 絶対パス表示(debug用)
    # print(path.resolve())

    # csv
    output_for_csv(path, attendee_dct_list)
    print("successfully completed.")
