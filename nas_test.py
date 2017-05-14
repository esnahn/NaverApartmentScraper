import nascraper
import unittest
from urllib.request import urlopen
import os


class List(unittest.TestCase):
    def test_scrape_sido(self):
        correct_sido = {"서울시": "1100000000",
                        "경기도": "4100000000",
                        "인천시": "2800000000",
                        "부산시": "2600000000",
                        "대전시": "3000000000",
                        "대구시": "2700000000",
                        "울산시": "3100000000",
                        "세종시": "3600000000",
                        "광주시": "2900000000",
                        "강원도": "4200000000",
                        "충청북도": "4300000000",
                        "충청남도": "4400000000",
                        "경상북도": "4700000000",
                        "경상남도": "4800000000",
                        "전라북도": "4500000000",
                        "전라남도": "4600000000",
                        "제주도": "5000000000"
                        }

        sidos = nascraper.scrape_list([''], nascraper.loc12_url, nascraper.loc1_id)

        self.assertTrue(sidos)
        for sd_id, sd_name in sidos:
            self.assertEqual(sd_id, correct_sido[sd_name])

    def test_scrape_sigungu(self):
        correct_sgg = {"1168000000": "강남구",
                       "4182000000": "가평군",
                       "3017000000": "서구"}

        sidos = [("1100000000", "서울시"),
                 ("4100000000", "경기도"),
                 ("3000000000", "대전시")]

        sigungus = nascraper.scrape_list([sd_id for sd_id, _ in sidos], nascraper.loc12_url, nascraper.loc2_id)

        self.assertTrue(sigungus)
        for sgg_id, sgg_name in sigungus:
            if sgg_id in correct_sgg.keys():
                self.assertEqual(sgg_name, correct_sgg[sgg_id])

    def test_scrape_emd(self):
        correct_emd = {"1168010600": "대치동",
                       "4182032500": "청평면",
                       "3017010300": "도마동"}

        sggs = [("1168000000", "강남구"),
                ("4182000000", "가평군"),
                ("3017000000", "서구")]

        eupmyeondongs = nascraper.scrape_list([sgg_id for sgg_id, _ in sggs], nascraper.loc3_url, nascraper.loc3_id)

        self.assertTrue(eupmyeondongs)
        for emd_id, name in eupmyeondongs:
            if emd_id in correct_emd.keys():
                self.assertEqual(name, correct_emd[emd_id])

    def test_scrape_apt(self):
        correct_apt = {"107810": "대치더블유타워(도시형)",
                       "104651": "청일덱스빌(3~7동)",
                       "106939": "푸르내리"}

        emds = [("1168010600", "대치동"),
                ("4182032500", "청평면"),
                ("3017010300", "도마동")]

        apartments = nascraper.scrape_list([emd_id for emd_id, _ in emds], nascraper.loc4_url, nascraper.loc4_id)

        self.assertTrue(apartments)
        for apt_id, name in apartments:
            if apt_id in correct_apt.keys():
                self.assertEqual(name, correct_apt[apt_id])

    def test_csv_save(self):
        columns = ["ID", "name"]
        emds = [("1168010600", "대치동"),
                ("4182032500", "청평면"),
                ("3017010300", "도마동")]

        nascraper.save_to_csv("./test_emd.csv", columns, emds)
        read_col, read_list = nascraper.read_from_csv("./test_emd.csv")

        self.assertListEqual(columns, read_col)
        self.assertListEqual(emds, read_list)


class Apartments(unittest.TestCase):
    def test_scrape_info(self):
        apts = [("104651", "청일덱스빌(3~7동)", "gar", "ba", "ge"),
                ("102668", "세곡리엔파크1단지")
                ]

        # ("APT_ID", "Date", "N_Housings", "Max_Floors", "Min_Floors")
        correct_infos = [("104651", "2004/01", "28", "7", "7"),
                         ("102668", "", "395", "13", "10")
                         ]

        try:
            os.remove(nascraper.path_aptinfo + "-test")
        except OSError:
            pass

        nascraper.scrape_apt_info([apt[0] for apt in apts], nascraper.path_aptinfo + "-test")
        _, infos = nascraper.read_from_csv(nascraper.path_aptinfo + "-test")
        self.assertListEqual(infos, correct_infos)

    def test_scrape_fp(self):
        apts = [("104651", "청일덱스빌(3~7동)", "gar", "ba", "ge")]

        # (apt_id, fp_id, area, entrance_type, rooms, baths, units)
        correct_fp = [
            ("104651", "101", '78.33', "복합식", '3', '2', '1', ''),
            ("104651", "106", '84.62', "복합식", '3', '2', '7', ''),
            ("104651", "108", '83.58', "복합식", '3', '2', '6', ''),
            ("104651", "111", '84.92', "복합식", '3', '2', '14', "./test/" + "104651_111.jpg")
        ]
        correct_fp_img_url = [
            "http://landthumb.phinf.naver.net/20160620_5/hscp_img_1466414709037wBvWd_JPEG/photoinfra_1466414708802.jpg"]

        try:
            os.remove(nascraper.path_fp + "-test")
        except OSError:
            pass

        for filepath in [x[7] for x in correct_fp if x[7]]:
            try:
                os.remove(filepath)
            except OSError:
                pass

        nascraper.scrape_apt_fp([x[0] for x in apts], nascraper.path_fp + "-test", "./test/")
        # create list of floorplans and downloads floorplan images to dir_fp

        _, fps = nascraper.read_from_csv(nascraper.path_fp + "-test")
        self.assertListEqual(fps, correct_fp)

        for filepath, url in zip([x[7] for x in correct_fp if x[7]], correct_fp_img_url):
            with open(filepath, 'rb') as fp_file:
                self.assertEqual(fp_file.read(), urlopen(url).read())


if __name__ == '__main__':
    unittest.main()
