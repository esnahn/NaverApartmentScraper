import nascraper
import unittest


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


if __name__ == '__main__':
    unittest.main()
