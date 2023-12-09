import urllib.request as req
from bs4 import BeautifulSoup
import openpyxl
import os
import csv

#셀레니움통해 크롤링
from selenium import webdriver #브라우저 창을 파이썬 명령으로 제어하는 모듈
from selenium.webdriver.chrome.service import Service
import time




if not os.path.exists("./프리미어리그경기결과.csv"):
    with open("./프리미어리그경기결과.csv", mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        # 여기에서 CSV 파일의 헤더를 작성할 수 있습니다.
        # 예: writer.writerow(["선수 이름", "통계1", "통계2", ...])
'''
option = webdriver.ChromeOptions() #켤때 옵션추가가능하게 해주는 함수
option.add_argument("headless")
browser = webdriver.Chrome("./chromedriver", options=option)
'''

s = Service('./chromedriver')  # 크롬 드라이버 파일의 경로
browser = webdriver.Chrome(service=s)



for i in range(36): # 페이지 수에 따라 조정
    browser.get(f'https://www.fotmob.com/ko/leagues/47/matches/premier-league?page={i}')
    time.sleep(3)  # 페이지 로딩 대기

    # "div.css-1fkfix2-LeagueMatchCSS.e565gvj0 > a" 선택자에 해당하는 모든 요소를 찾는다
    matches = browser.find_elements_by_css_selector("div.css-1fkfix2-LeagueMatchCSS.e565gvj0 > a")
    for match in matches:
        match.click()  # 각 경기 결과 페이지로 이동
        time.sleep(2)  # 페이지 로딩 대기

        # 각 경기 결과 페이지로 이동
        for j in range(22):  # 페이지당 경기 수에 따라 조정
            try:
                # 경기 결과 페이지로 이동
                match_link = browser.find_elements_by_css_selector("div.css-11d04mc-RowContainer.eu5dgts4 > a")
                match_link.click()
                time.sleep(2)  # 페이지 로딩 대기

                # 여기에 각 경기 페이지에서 데이터를 추출하는 코드 작성
                # 예: match_data = browser.find_element_by_css_selector("CSS 선택자").text
                name = [browser.find_element_by_css_selector("div.css-10x6lqx-PlayerName.e1fnykti12").text]
                # 선수의 통계 값들을 추출하여 리스트로 저장
                stat_values_elements = browser.find_elements_by_css_selector("span.StatValue")
                stat_values = [element.text for element in stat_values_elements]
                player = name + stat_values

                # CSV 파일에 데이터 추가
                with open("./프리미어리그경기결과.csv", mode='a', newline='', encoding='utf-8-sig') as file:
                    writer = csv.writer(file)
                    writer.writerow(player)




                browser.back()  # 이전 페이지로 돌아가기
                time.sleep(2)
            except Exception as e:
                print("Error:", e)
                continue
        browser.back()
        time.sleep(2)
    '''

    for j in range(22):
        browser.find_element_by_css_selector("div.css-11d04mc-RowContainer.eu5dgts4 > a").click()
    "div.css-11d04mc-RowContainer.eu5dgts4"

    "div.css-1fkfix2-LeagueMatchCSS.e565gvj0 > a" #결과 페이지
    "div.css-11d04mc-RowContainer.eu5dgts4 > a" #선수페이지 22번 돌린다
    '''



    '''

    # 동시에 2개 리스트 for?
    for i in range(len(title)):  # range 원하는 리스트 생성, len함수 원소의 개수 반환 0~9까지 생성
        print(title[i].string, price[i].string)
        f.write(title[i].string + ", " + price[i].string + "\n")  # ,이용 여러개 값 출력 못하니 문자열 덧셈으로 여러값 나란히 출력
    '''



book.save("./프리미어리그경기결과.csv")
browser.quit()

