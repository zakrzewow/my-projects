import requests
from bs4 import BeautifulSoup as bs
import csv
'''jeśli pojawią się nowe artykuły trzeba dodać tylko ich nazwę na stronie i myk same się dane zrobią'''
ARTNAMES = ("we-want-this-done-now","negotiating-loopholes","how-dare-you","can-you-hear-me","together-we-are-making-a-difference","cathedral-thinking","a-strange-world","youre-acting-like-spoiled-irresponsible-children","im-too-young-to-do-this","our-house-is-on-fire","prove-me-wrong","unpopular","the-disarming-case-to-act-right-now-on-climate","almost-everything-is-black-and-white","our-lives-are-in-your-hands")

def scrapPage(soup):
    '''

    :param soup: obiekt bs4
    :return: string z tekstem
    '''
    page = soup.findAll('p')
    text = ""
    for i in page:
        text+=(i.getText()+" ")
    return text

def getDate(soup):
    '''

    :param soup: obiekt bs4
    :return: data w postaci str
    '''
    page = soup.find('h2').find('div')
    return page.attrs['datetime']


if __name__ == "__main__":
    header = ["name","date","text"]

    with open("../../speeches/data/data.csv", 'w', encoding='UTF-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(header)
        for i in ARTNAMES:
            resp = requests.get("https://greta.heath3.com/"+i)
            resp.encoding = "UTF-8"
            print(resp.encoding)
            soup = bs(resp.text,'html.parser')
            writer.writerow([i,getDate(soup),scrapPage(soup)])


