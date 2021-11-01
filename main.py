import re
import time
import requests
from bs4 import BeautifulSoup
import csv

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cookie': 'PHPSESSID=b70814cb9e7cd7f53d1ca5b37e71af4d; geoip_country_code=RU; check_cookie_eu=0; prian_hash=15784691b81b3177b5356a48cc75b197; search_view=2; alert_block_hide=1; request_error_type=none; request_form_send=yes; __cf_bm=0XJHNi54sWmh_.bsnsTJO9CDAzJYiGY073VmEjhCO9Q-1635678339-0-ATDJWUjdU46sRP285K2oieKJpB3HpFmCn6CbTmrSQB+tcf4BxnPRmUoGyX8R4LgWqIzS6QUohlL+6eddTPLO8y40x3GRD/mNvnr/vlK0tE92K6uSPEXEdhDk5gEZ5H2qvw==',
    'referer': 'https://prian.ru/company/',
    'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
}


def Phone_post(id_compani):
    url = 'https://prian.ru/sys/savestat.php'
    parametrs = {
        "type": "show_phone",
        "lng": "1",
        "contact": "undefined",
        "place": "0",
        "pagetype": "",
        "phone_status": "1",
        "pricestatus": "undefined",
        "companystatus": "1",
        "phone_type": "",
        "messenger_type": "",
        "place_type": "contact",
        "fsubscribe": "0",
        "fsearch": "",
        "fsearch_hash": "",
        "about_vacancy_id": "0",
        "fobject": "",
        "fmessage": "",
        "fmessage3": "",
        "ftype": "",
        "fcompany": f"{id_compani}",
        "fcountry": "193",
        "fcompanytype": "4",
        "fcompanytype2": "1",
        "fbuttontype": "0",
        "fauthor": "0",
        "favorites_ids": '',
        "search_urls": '',
        "ws_page_id": '',
        "vstat": '',
        "block_notice_type": "0",
        "partner_material": "0",
        "felement": "",
        "sp_cr": "pFzZbT2gSz2FSEkCzeNQPVuipZBm11Z7hoPMAoIGlm4=",
        "rf_cr": "9nZpfC4qdptdfeYK1qQ61DdElgiVrcBhxuE1GtkVFA8=",
        "type_place": "gtm_page"
    }

    Phone = requests.post(url=url, params=parametrs).text

    return Phone


def request_no_error(url, retry=5):
    try:
        response = requests.get(url=url, headers=headers)
        # print(f"[+] {url} {response.status_code}")
    except Exception as ex:
        time.sleep(3)
        if retry:
            print(f"[INFO] retry={retry} => {url}")
            return request_no_error(url, retry=(retry - 1))
        else:
            raise
    else:
        return response


def main():
    file_list = []

    url = 'https://prian.ru/company/?next=0'
    req = request_no_error(url)
    src = req.text
    # print(src)
    soup = BeautifulSoup(src, 'html.parser')
    caunt_page = int(soup.find_all(class_='pagination-square__anchor')[-1].text)

    print(caunt_page)

    # caunt_page = 2

    url_list = []
    for page in range(0, (caunt_page - 1) * 10, 10):
        print(f'Page {page} / {(caunt_page - 1) * 10}')
        url = f'https://prian.ru/company/?next={page}'
        req = request_no_error(url)
        src = req.text

        with open("index.html", "w", encoding='utf-8') as file:
            file.write(src)

        # print(src)

        with open("index.html", encoding='utf-8') as file:
            src = file.read()

        # print(src)
        soup = BeautifulSoup(src, 'html.parser')

        conten = soup.find(class_='content').find(class_='company-list').find_all('li')
        # print(conten)

        for compani in conten[1:]:
            url_compani = f"https:{compani.find(class_='company-item__content').find('a').get('href')}"
            # print(url_compani)
            url_list.append(url_compani)

    print(url_list)
    print('Сбор ссылок закончен, начинаю работу по компаниям')
    caunt = 0

    for compani in url_list:
        caunt += 1
        print(f'Собираю данные компаний {caunt} из {len(url_list)}')
        url = compani
        req = request_no_error(url)
        src = req.text

        with open("index.html", "w", encoding='utf-8') as file:
            file.write(src)

        # print(src)

        with open("index.html", encoding='utf-8') as file:
            src = file.read()

        # print(src)
        soup = BeautifulSoup(src, 'html.parser')

        Name_grup = soup.find(class_='col-lg-9').text

        try:
            web = soup.find(class_='company_go_link').get('href')
        except:
            web = ''

        try:
            script = str(soup.find(class_='bg_white').find("script"))
        except:
            script = ''

        match = re.search('ga_item_id = "(.*?)"', script).group(1)
        try:
            Phone = str(Phone_post(match))
        except:
            Phone = ''

        fasys = soup.find_all(class_='face')
        # print(fasys)

        person_list = []
        for fase in fasys:
            try:
                representative_name = str(fase.find(class_='name').text).strip()

                try:
                    post_p = str(fase.find(class_='name').find('span').text).strip()
                    representative_name = representative_name.replace(post_p, '')
                except:
                    post_p = ''

            except:
                representative_name = ''
                post_p = ''

            print(representative_name)

            try:
                Phone_p = str(fase.find(class_='messengers pr-js-show-phone-number').get('id')).replace('m_phone_', '')
            except:
                # print(f'Проверь {compani}')
                try:
                    id_nimber = fase.find(class_='pr-js-show-phone-number').get('data-id')
                    # print(id_nimber)
                    params = {
                        'type': 'show_phone',
                        'lng': '1',
                        'contact': f'{id_nimber}',
                        'place': '0',
                        'pagetype': '',
                        'phone_status': '2',
                        'pricestatus': 'undefined',
                        'companystatus': '1',
                        'phone_type': '',
                        'messenger_type': '',
                        'place_type': 'contact',
                        'fsubscribe': '0',
                        'fsearch': '',
                        'fsearch_hash': '',
                        'about_vacancy_id': '0',
                        'fobject': '',
                        'fmessage': '',
                        'fmessage3': '',
                        'ftype': '',
                        'fcompany': f'{match}',
                        'fcountry': '43',
                        'fcompanytype': '4',
                        'fcompanytype2': '1',
                        'fbuttontype': '0',
                        'fauthor': '0',
                        'favorites_ids': '',
                        'search_urls': '',
                        'ws_page_id': '',
                        'vstat': '',
                        'block_notice_type': '0',
                        'partner_material': '0',
                        'felement': '',
                        'sp_cr': 'ZGRojh60GljN0sHmET7e3r6E57suytlFAQDdn0Y9Gtc',
                        'rf_cr': '8',
                        'RK5cbYJcela2VPqH9EkZg==': '',
                        'type_place': 'gtm_page'
                    }
                    Phone_p = requests.post('https://prian.ru/sys/savestat.php', params=params).text
                except:
                    Phone_p = ''

            # mail = fase.find(class_='c-contacts__social c-contacts__social_last').text
            # print()
            person_list.append(f'{representative_name}\n{post_p}\n{Phone_p}')

        file_writer = [Name_grup, web, Phone] + person_list
        print(file_writer)
        file_list.append(file_writer)

    with open('exit_data.csv', 'w', encoding='cp1251', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(file_list)




if __name__ == '__main__':
    main()