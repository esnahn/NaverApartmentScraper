import csv
from pathlib import Path
from urllib.request import urlopen, urlretrieve
from bs4 import BeautifulSoup
from datetime import datetime

'''
네이버 부동산 아파트 평면도 긁개

- 시도, 시군구, 읍면동, 단지 목록

- 평면유형별 면적, 방 수, 욕실 수, 세대 수, 평면도
'''

# file path
path_sd = "./sidos.csv"
path_sgg = "./sigungus.csv"
path_emd = "./eupmyeondongs.csv"
path_apt = "./apartments.csv"
path_aptinfo = "./apt_info.csv"
path_fp = "./floorplans.csv"

dir_fp = "./fp_img/"

### internal variables
# urls
loc12_url = "http://land.naver.com/article/cityInfo.nhn?rletTypeCd=A01&cortarNo="
loc3_url = "http://land.naver.com/article/divisionInfo.nhn?rletTypeCd=A01&cortarNo="
loc4_url = "http://land.naver.com/article/articleList.nhn?rletTypeCd=A01&cortarNo="
apt_url = "http://land.naver.com/article/complexInfo.nhn?rletTypeCd=A01&rletNo="
fp_url = "http://land.naver.com/article/groundPlan.nhn?rletTypeCd=A01&rletNo="

# div ids
loc1_id = "loc_view1"
loc2_id = "loc_view2"
loc3_id = "loc_view3"
loc4_id = "loc_view4"


def scrape_list(url_ids, url, div_id):
    # returns a list of (id, name)
    pairs = []

    for url_id in url_ids:
        html = urlopen(url + url_id)
        soup = BeautifulSoup(html.read(), 'html.parser')
        options = soup.find(id=div_id).find_all('option', value=True)
        options = [option for option in options if option['value'].isdigit()]

        print("Retrieved {} items for ID# {}".format(len(options), url_id))

        pairs += [(option['value'], option.text) for option in options]
    return pairs


def save_to_csv(filepath, columns, savelist):
    if not Path(filepath).parent.exists(): Path(filepath).parent.mkdir()
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
        listwriter = csv.writer(csvfile)
        listwriter.writerow(columns)
        listwriter.writerows(savelist)


def read_from_csv(filepath):
    readlist = []

    with open(filepath, 'r', newline='', encoding='utf-8-sig') as csvfile:
        listreader = csv.reader(csvfile)
        rows = list(listreader)

    columns = rows[0]

    for item in rows[1:]:
        readlist.append(tuple(item))

    return columns, readlist


def scrape_apt_info(apt_ids, filepath=path_aptinfo):
    columns = ["APT_ID", "Date", "N_Housings", "Max_Floors", "Min_Floors"]
    apt_id_set = {}
    count = 0

    if Path(filepath).exists():
        col_from_file, list_from_file = read_from_csv(filepath)
        assert columns == col_from_file
        apt_id_set = {x[0] for x in list_from_file}  # "APT_ID"
    else:
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
            listwriter = csv.writer(csvfile)
            listwriter.writerow(columns)

    with open(filepath, 'a', newline='', encoding='utf-8-sig') as csvfile:
        listwriter = csv.writer(csvfile)

        for apt_id in apt_ids:
            if apt_id not in apt_id_set:
                html = urlopen(apt_url + apt_id)
                soup = BeautifulSoup(html.read(), 'html.parser')
                table = soup.find(class_="housing_info")

                date_built = table.find(string='준공년월').find_next('td').string
                try:
                    date_simple = datetime.strptime(date_built, '%Y년%m월').strftime('%Y/%m')
                except:
                    date_simple = ''

                num_housings = table.find(string='총세대수').find_next('td').string.split('세대')[0]

                max_floors = table.find(string='최고층').find_next('td').string.split('층')[0]
                min_floors = table.find(string='최저층').find_next('td').string.split('층')[0]

                listwriter.writerow((apt_id, date_simple, num_housings, max_floors, min_floors))
                count += 1
                print("Retrieved info for Apt. #{}".format(apt_id))
            else:
                print("Apt. #{} was already retrieved.".format(apt_id))

        print("Saved {} items for Information on Apartment Complex".format(count))


def scrape_apt_fp(apt_ids, filepath=path_fp, img_dir=dir_fp, img_overwrite=False):
    columns = ["APT_ID", "FP_ID", "Area", "Entrance", "Rooms", "Baths", "N_Units", "Image"]
    apt_id_set = {}
    count = 0

    if not Path(img_dir).exists():
        Path(img_dir).mkdir()

    if Path(filepath).exists():
        col_from_file, list_from_file = read_from_csv(filepath)
        assert columns == col_from_file
        apt_id_set = {x[0] for x in list_from_file}  # "APT_ID"
    else:
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
            listwriter = csv.writer(csvfile)
            listwriter.writerow(columns)

    with open(filepath, 'a', newline='', encoding='utf-8-sig') as csvfile:
        listwriter = csv.writer(csvfile)

        for apt_id in apt_ids:
            if apt_id not in apt_id_set:
                html = urlopen(fp_url + apt_id)
                soup = BeautifulSoup(html.read(), 'html.parser')

                fp_items = soup.find(class_="plane").find_all('li', recursive=False)

                for i in fp_items:
                    fp_id = i.h4.span.string.rstrip('㎡')

                    details = i.find_all('dd')
                    assert len(details) == 6
                    area = details[1].em.string.rstrip('㎡')
                    entrance_type = details[2].string
                    num_rooms = int(details[3].string.rstrip('개'))
                    num_baths = int(details[4].string.rstrip('개'))
                    num_units = int(details[5].string.rstrip('세대'))

                    if i.find('div', class_='thumb').a:
                        fp_img_url = i.find('img')['src']
                        fp_img_path = img_dir + apt_id + '_' + fp_id + '.' + fp_img_url.rsplit('.', 1)[1]
                        if not Path(fp_img_path).exists() or img_overwrite:
                            urlretrieve(fp_img_url, fp_img_path)
                    else:
                        fp_img_path = ''

                    listwriter.writerow(
                        (apt_id, fp_id, area, entrance_type, num_rooms, num_baths, num_units, fp_img_path)
                    )
                    count += 1

                print("Retrieved {} items for Apt. #{}".format(len(fp_items), apt_id))
            else:
                print("Apt. #{} was already retrieved.".format(apt_id))

    print("Saved {} items for Apartment floorplans".format(count))


if __name__ == '__main__':
    sidos = []
    sigungus = []
    eupmyeondongs = []
    apartments = []
    floorplans = []

    if not Path(path_sd).exists():
        sidos = scrape_list([''], loc12_url, loc1_id)
        print("** Retrieved {} items for Si/Do **".format(len(sidos)))
        save_to_csv(path_sd, ["ID", "name"], sidos)
        print("==> Saved to {}".format(path_sd))
    else:
        _, sidos = read_from_csv(path_sd)
        print("Loaded {} items for Si/Do from saved file".format(len(sidos)))

    if not Path(path_sgg).exists():
        sigungus = scrape_list([sd_id for sd_id, _ in sidos], loc12_url, loc2_id)
        print("** Retrieved {} items for Si/Gun/Gu **".format(len(sigungus)))
        save_to_csv(path_sgg, ["ID", "name"], sigungus)
        print("==> Saved to {}".format(path_sgg))
    else:
        _, sigungus = read_from_csv(path_sgg)
        print("Loaded {} items for Si/Gun/Gu from saved file".format(len(sigungus)))

    if not Path(path_emd).exists():
        eupmyeondongs = scrape_list([sgg_id for sgg_id, _ in sigungus], loc3_url, loc3_id)
        print("** Retrieved {} items for Eup/Myeon/Dong **".format(len(eupmyeondongs)))
        save_to_csv(path_emd, ["ID", "name"], eupmyeondongs)
        print("==> Saved to {}".format(path_emd))
    else:
        _, eupmyeondongs = read_from_csv(path_emd)
        print("Loaded {} items for Eup/Myeon/Dong from saved file".format(len(eupmyeondongs)))

    if not Path(path_apt).exists():
        apartments = scrape_list([emd_id for emd_id, _ in eupmyeondongs], loc4_url, loc4_id)
        print("** Retrieved {} items for Apartment complex **".format(len(apartments)))
        save_to_csv(path_apt, ["ID", "name"], apartments)
        print("==> Saved to {}".format(path_apt))
    else:
        _, apartments = read_from_csv(path_apt)
        print("Loaded {} items for Apartment complex from saved file".format(len(apartments)))

    apt_ids = [apt[0] for apt in apartments]

    scrape_apt_info(apt_ids, path_aptinfo)
    scrape_apt_fp(apt_ids, path_fp, dir_fp)
