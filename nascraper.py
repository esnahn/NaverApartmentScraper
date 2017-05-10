from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv

'''
네이버 부동산 아파트 평면도 긁개

- 시도, 시군구, 읍면동, 단지 목록

http://land.naver.com/article/groundPlan.nhn?rletTypeCd=A01&rletNo=8928
div ground_area
ul plane
li

div thumb
a
img 평면도

h4
span 면적+유형일련번호
'''
# urls
loc12_url = "http://land.naver.com/article/cityInfo.nhn?rletTypeCd=A01&cortarNo="
loc3_url = "http://land.naver.com/article/divisionInfo.nhn?rletTypeCd=A01&cortarNo="
loc4_url = "http://land.naver.com/article/articleList.nhn?rletTypeCd=A01&cortarNo="
lco4_url = "http://land.naver.com/article/groundPlan.nhn?rletTypeCd=A01&rletNo="

# div ids
loc1_id = "loc_view1"
loc2_id = "loc_view2"
loc3_id = "loc_view3"
loc4_id = "loc_view4"

# file path
path_sd = "./sidos.csv"
path_sgg = "./sigungus.csv"
path_emd = "./eupmyeondongs.csv"
path_apt = "./apartments.csv"
path_fp = "./floorplans.csv"


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


if __name__ == '__main__':
    sidos = []
    sigungus = []
    eupmyeondongs = []
    apartments = []
    floorplans = []

    sidos = scrape_list([''], loc12_url, loc1_id)
    print("** Retrieved {} items for Si/Do **".format(len(sidos)))
    save_to_csv(path_sd, ["ID", "name"], sidos)
    print("==> Saved to {}".format(path_sd))

    sigungus = scrape_list([sd_id for sd_id, _ in sidos], loc12_url, loc2_id)
    print("** Retrieved {} items for Si/Gun/Gu **".format(len(sigungus)))
    save_to_csv(path_sgg, ["ID", "name"], sigungus)
    print("==> Saved to {}".format(path_sgg))

    eupmyeondongs = scrape_list([sgg_id for sgg_id, _ in sigungus], loc3_url, loc3_id)
    print("** Retrieved {} items for Eup/Myeon/Dong **".format(len(eupmyeondongs)))
    save_to_csv(path_emd, ["ID", "name"], eupmyeondongs)
    print("==> Saved to {}".format(path_emd))

    apartments = scrape_list([emd_id for emd_id, _ in eupmyeondongs], loc4_url, loc4_id)
    print("** Retrieved {} items for Apartment complex **".format(len(apartments)))
    save_to_csv(path_apt, ["ID", "name"], apartments)
    print("==> Saved to {}".format(path_apt))
