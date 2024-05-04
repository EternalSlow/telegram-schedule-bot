import requests
from bs4 import BeautifulSoup as bs
import json
import time
time.sleep(5)
full_path="home/jinshot/project/python/test-ilos/json_file/schedule.json"
url_down = "https://a-pet.ru/schedule/?group=%C8%D1%CF%CF-7&curs=1&even=1"
url_up =  "https://a-pet.ru/schedule/?group=%C8%D1%CF%CF-7&even=0&curs=1"
url_exception_up = "https://a-pet.ru/schedule/?group=%C8%D1%CF%CF-7&even=0&curs=1"
url_exception_down = "https://a-pet.ru/schedule/?group=%C8%D1%CF%CF-7&curs=1&even=1"
response_down = requests.get(url_down)
response_up = requests.get(url_up)
response_exception_up = requests.get(url_exception_up)
response_exception_down = requests.get(url_exception_down)
html_down = response_down.content
html_up = response_up.content
html_exception_up = response_exception_up.content
html_exception_down = response_exception_down.content
soup_down = bs(html_down, "html.parser")
soup_up = bs(html_up, "html.parser")
soup_exception_up = bs(html_exception_up,'html.parser')
soup_exception_down = bs(html_exception_down, 'html.parser')
elements_down = soup_down.find_all("tr", class_="sch_sel1")
elements_up = soup_up.find_all("tr", class_="sch_sel1")
elements_exception_up = soup_exception_up.find_all('tr',class_="sch_sel0")
elements_exception_down = soup_exception_down.find_all('tr',class_="sch_sel0")

def get_element(elements):
    arr = []
    day = ""
    for element in elements:
        children = element.findChildren("td",recursive=False)
        if len(children) == 3:
            children.insert(0,day)
        else:
            day = children[0]
        for i in range(len(children)):
            children[i] = children[i].text
        arr.append(children)
    return arr

def generate_schedule(elements,exception):
    
    schedule = {"Понедельник":[],
                "Вторник":[],
                "Среда":[],
                "Четверг":[],
                "Пятница":[],
                "Суббота":[]
    }
    for row in elements:
        schedule[row[0]].append((row[1],row[2],row[3]))
    for row in exception:
        schedule[row[0]].append((row[1],row[2],row[3]))
    return schedule

def save(texted, mode):
    with open("json_file/schedule.json", 'r', encoding="utf-8") as file:
        parity = json.load(file)[2]
        texted.append(parity)
    with open("json_file/schedule.json", mode, encoding="utf-8") as file:
        json.dump(texted, file, sort_keys=False, indent=4, ensure_ascii=False, separators=(',',':'))
        
save([generate_schedule(get_element(elements_up),get_element(elements_exception_up)), generate_schedule(get_element(elements_down),get_element(elements_exception_down))], "w")
