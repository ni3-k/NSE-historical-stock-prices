# Importing libraries.
# -*-coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import pandas as pd


# Defining Urls need to scraped.
url1 = "https://www.nseindia.com/content/corporate/eq_research_reports_listed.htm"
url2 = "https://www.nseindia.com/content/corporate/eq_rrl_m2z.htm"

# Defining headers.
headers={'Host': 'www.nseindia.com',
'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Language': 'en-US,en;q=0.5',
}


# Sending Requests for both Urls.
response1 = requests.get(url1, headers=headers)
response2 = requests.get(url2, headers=headers)


# Creating BeautifulSoup Objects.
soup1 = BeautifulSoup(response1.text, 'html.parser')
soup2 = BeautifulSoup(response2.text, 'html.parser')


# Scraping First Page of NSE.
table = soup1.find('table')
table_rows = table.find("div", {"id": "content"})('tr')
df = pd.DataFrame(columns=('Symbol', 'Company_name'))
i = 0
for tr in table_rows:
    if(i != 0):
        td = tr.find_all('td' )
        df.loc[df.shape[0]] = [td[1].text, td[2].text]
    i = 1


# Scraping Second Page of NSE.
table2 = soup2.find_all("td", {"class": "t0"})
temp = []
for td in table2:
    temp.append(td.text)
    if(len(temp) == 3):
        df.loc[df.shape[0]] = [temp[1], temp[2]]
        temp[:] = []


# Header for Google Finance.
headers={'Host': 'www.google.com',
'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Language': 'en-US,en;q=0.5',
}


i=0
for symbol in df['Symbol']:
    start = 0
    num = 200
    url_cid = "https://www.google.com/finance?q=" + symbol
    response_for_cid = requests.get(url_cid, headers=headers)
    soup = BeautifulSoup(response_for_cid.text, 'lxml')
    link  = soup.find('link')
    link_href = link.get('href')
    cid = link_href.strip('http://www.google.com/finance?cid=')
    while True:
        try:
            url = "https://www.google.com/finance/historical?cid="+cid+"&startdate=Jan+1%2C+2000&enddate=Mar+23%2C+2017&start={}&num={}"
            url = url.format(start, num)
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')
            dates = soup.find_all("td", {"class": "lm"})
            datas = soup.find_all("td", {"class": "rgt"})

            dates = [date.text.strip('\n') for date in dates]
            datas = [data.text.strip('\n') for data in datas]
            company_data = df.loc[df['Symbol'] == symbol]
            for date in dates:
                print(company_data['Symbol'][i], company_data['Company_name'][i], date, datas[5*dates.index(date)], datas[5*dates.index(date)+1], datas[5*dates.index(date)+2], datas[5*dates.index(date)+3], datas[5*dates.index(date)+4])
            start += 200
            if(datas == []):
                break
        except:
            print("No Record found for " + company_data['Company_name'][i] + " in Google Finance")
    i += 1