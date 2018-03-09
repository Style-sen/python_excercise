#-*- coding: utf-8 -*-

"""
来源:用100行Python爬虫代码抓取公开的足球数据玩（一）(https://juejin.im/entry/5a7952c16fb9a0633f0dff0a)
"""


from __future__ import print_function, division
from selenium import webdriver
import pandas as pd

import os

class Spider(object):
    def __init__(self):
        ## setup
        #self.base_url = base_url
        try:
            self.driver = webdriver.Chrome(os.getenv('CHROME_DRIVER'))
        except:
            print("\033[1;31m未指明CHROME_DRIVER环境变量\033[0m")
            print("例如:(Ubuntu)")
            print("    1. sudo apt-get install chromium-chromedriver")
            print("    2. export CHROME_DRIVER=/usr/lib/chromium-browser/chromedriver")
            print("    3. 重新运行")
            exit()
        self.driver.implicitly_wait(30)
        self.verificationErrors = []
        self.accept_next_alert = True

    def get_all_team_data(self):
        # 先通过世界杯主页获取所有32只队的ID（构成球队URL）
        self.get_team_ids()
        # 循环爬取每一支队的比赛数据
        data = []
        for i, [team_id, team_name] in enumerate(self.team_list):
            #if i == 1:
            #    break
            print(i, team_id, team_name)
            df = self.get_team_data(team_id, team_name)
            data.append(df)
        output = pd.concat(data)
        output.reset_index(drop=True, inplace=True)
        #print(output)
        output.to_csv('data_2018WorldCup.csv', index=False, encoding='utf-8')
        self.driver.close()

    def get_team_ids(self):
        main_url = 'http://zq.win007.com/cn/CupMatch/75.html'
        self.driver.get(main_url)
        teams = self.driver.find_elements_by_xpath("//td[@style='background-color:#fff;text-align:left;']")
        data = []
        for team in teams:
            team_id = int(team.find_element_by_xpath(".//a").get_attribute('href').split('/')[-1].split('.')[0])
            team_name = team.find_element_by_xpath(".//a").text
            print(team_id, team_name)
            data.append([team_id, team_name])
        self.team_list = data
        #self.team_list = pd.DataFrame(data, columns=['team_name', 'team_id'])
        #self.team_list.to_excel('国家队ID.xlsx', index=False)

    def get_team_data(self, team_id, team_name):
        """获取一个国家队的比赛数据。TODO：没有实现翻页"""
        url = 'http://zq.win007.com/cn/team/CTeamSche/%d.html'%team_id
        self.driver.get(url)

        table = self.driver.find_element_by_xpath("//div[@id='Tech_schedule' and @class='data']")
        matches = table.find_elements_by_xpath(".//tr")
        print(len(matches))
        
        # 抓取比赛数据，并保存成DataFrame
        data = []
        for i, match in enumerate(matches):
            if i == 0:
                headers = match.find_elements_by_xpath(".//th")
                h1, h2, h3, h4, h5 = headers[0].text, headers[1].text, headers[2].text, headers[3].text, headers[4].text
                print(h1, h2, h3, h4, h5)
                continue
            try:
                info = match.find_elements_by_xpath(".//td")
                cup = str(info[0].text# .encode('utf-8')
                          )
                match_time = str(info[1].text# .encode('utf-8')
                                 )
                home_team = str(info[2].text# .encode('utf-8')
                                )
                fts = info[3].text
                #print('-', cup, '-')
                fs_A, fs_B = int(fts.split('-')[0]), int(fts.split('-')[1])
                away_team = str(info[4].text# .encode('utf-8')
                                )
                print(cup, match_time, home_team, away_team, fs_A, fs_B)
                data.append([cup, match_time, home_team, away_team, fs_A, fs_B, team_name])
            except:
                break
        df = pd.DataFrame(data, columns=['赛事', '时间', '主队', '客队', '主队进球', '客队进球', '国家队名'])
        return df

if __name__ == "__main__":
    
    spider = Spider()
    # 第一步：抓2018世界杯球队的ID。第二部：循环抓取每一支队的比赛数据。
    spider.get_all_team_data()
