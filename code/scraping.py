import requests
import json
import csv
from unidecode import unidecode
import urllib.parse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
import time

f = open("code/exclude_list.txt", "r")
exclude_list = f.read().splitlines()
f.close()

f = open("data.json", "r", encoding="utf-8")
json_data = json.loads(f.read())
f.close()

def scrape(url) :
    r = requests.get(url)
    return r.text

def find_all_links(s) :
    links = []
    while ("href=" in s) :
        s=s[s.index("href=")+6:]
        link = s[:s.index('"')]
        s=s[s.index('"'):]
        if link not in links and "#" not in link :
            links.append(link)
    return links

#makes sure that none of the exclusion terms are in the link (ex. bachelor)
def non_exclude_list(link) :
    for exclude in exclude_list :
        if exclude in link :
            return False
    return True

#there are some small things that cause issues, like if the Alma matter header is a link instead of p.  This method fixes those issues
def special_exceptions(source) :
    source = source.replace('<a href="/wiki/Alma_mater" title="Alma mater">Alma mater</a>', 'Alma&#160;mater</th>')
    return source

#this method scrapes the wikipedia page of the given link and then tries to scrape the listings under Education and Institutions.  It's definitely not perfect but through my testing, it seems basically flawless.  Should work well enough so that the list is short enough so I can go through to verify manually
def scrape_wiki_data(link) :
    alma_matters = [] #universities they attended
    category = "" #physics, chemistry, etc.
    year = "" #year they won the nobel prize

    source = special_exceptions(scrape(link))
    try :
        temp_source = source[source.index('Education</th>'):]
        temp_source = temp_source[:temp_source.index('</tr>')]
        while("href" in temp_source) :
            temp_source = temp_source[temp_source.index('href="')+6:]
            alma_matter = temp_source[:temp_source.index('"')]
            if ("/wiki/" in alma_matter and non_exclude_list(alma_matter)) :
                alma_matter = alma_matter
                if (alma_matter not in alma_matters) :
                    alma_matters.append(clean_up(alma_matter))
    except :
        pass
    try :
        temp_source = source[source.index('Alma&#160;mater</th>'):]
        temp_source = temp_source[:temp_source.index('</tr>')]
        while("href" in temp_source) :
            temp_source = temp_source[temp_source.index('href="')+6:]
            alma_matter = temp_source[:temp_source.index('"')]
            if ("/wiki/" in alma_matter and non_exclude_list(alma_matter)) :
                alma_matter = alma_matter
                if (alma_matter not in alma_matters) :
                    alma_matters.append(clean_up(alma_matter))
    except :
        pass
    if (len(alma_matters) == 0) :
        print("No alma matters found for " + link)
    
    #getting the category and year
    
    return alma_matters

#takes in a name, like Wilhelm R%C3%B6ntgen and returns Wilhelm Rontgen.  Gets rid of annoying unicode characters
def clean_up(s) :
    s = urllib.parse.unquote(s, encoding='utf-8')
    s = unidecode(s)
    s = urllib.parse.quote(s, encoding='utf-8')
    return urllib.parse.quote(s, encoding='utf-8')

def generate_list_of_universities() :
    f = open("data.json", "r", encoding="utf-8")
    data = json.loads(f.read())
    f.close()
    universities = []
    for name in data :
        for alma_matter in data[name]["alma_matters"] :
            if alma_matter not in universities :
                universities.append(alma_matter)
    f = open("code/universities.txt", "w", encoding="utf-8")
    for university in universities :
        f.write('"' + university + '",\n')
    f.close()

#goes through and looks for cases where schools are at the wrong link (ex. wiki/MIT & wiki/Massac... or wiki/Olin_Business_School vs wiki/Wash...)
def fix_mistakes() :
    #replacement section
    f = open("data.json", "r", encoding="utf-8")
    data = f.read()
    f.close()

    #edits
    data = data.replace("/wiki/MIT", "/wiki/Massachusetts_Institute_of_Technology")
    data = data.replace("/wiki/Caltech", "/wiki/California_Institute_of_Technology")
    data = data.replace("/wiki/NYU", "/wiki/New_York_University")
    data = data.replace('"/wiki/Harvard"', '"/wiki/Harvard_University"')
    data = data.replace("/wiki/University_of_Chicago_Booth_School_of_Business", "/wiki/University_of_Chicago")
    data = data.replace("/wiki/Booth_School_of_Business", "/wiki/University_of_Chicago")
    data = data.replace("/wiki/Stanford_University_School_of_Medicine", "/wiki/Stanford_University")
    data = data.replace("/wiki/Simon_Business_School", "/wiki/University_of_Rochester")
    data = data.replace("/wiki/Harvard_Business_School", "/wiki/Harvard_University")
    data = data.replace("/wiki/Wharton_School_of_the_University_of_Pennsylvania", "/wiki/University_of_Pennsylvania")
    data = data.replace("/wiki/Wharton_School", "/wiki/University_of_Pennsylvania")
    data = data.replace("/wiki/Samuel_Curtis_Johnson_Graduate_School_of_Management", "/wiki/Cornell_University")
    data = data.replace("/wiki/Olin_Business_School", "/wiki/Washington_University_in_St._Louis")
    data = data.replace("/wiki/Perelman_School_of_Medicine_at_the_University_of_Pennsylvania", "/wiki/University_of_Pennsylvania")
    data = data.replace("/wiki/Columbia_Law_School", "/wiki/Columbia_University")
    data = data.replace("/wiki/New_York_University_School_of_Law", "/wiki/New_York_University")
    data = data.replace("/wiki/Case_Western_Reserve_University_School_of_Medicine", "/wiki/Case_Western_Reserve_University")
    data = data.replace("/wiki/Johns_Hopkins_School_of_Medicine", "/wiki/Johns_Hopkins_University")
    data = data.replace("/wiki/Washington_University_School_of_Medicine", "/wiki/Washington_University_in_St._Louis")
    data = data.replace("/wiki/Harvard_Medical_School", "/wiki/Harvard_University")
    data = data.replace("/wiki/New_York_University_School_of_Medicine", "/wiki/New_York_University")
    data = data.replace("/wiki/University_of_Pennsylvania_School_of_Medicine", "/wiki/University_of_Pennsylvania")
    data = data.replace("/wiki/Rady_School_of_Management", "/wiki/University_of_California,_San_Diego")
    data = data.replace("/wiki/New_York_University_Tandon_School_of_Engineering", "/wiki/New_York_University")
    data = data.replace("Robert_Wood_Johnson_Medical_School", "/wiki/Rutgers_University")
    data = data.replace("/wiki/Tulane_University_School_of_Medicine", "/wiki/Tulane_University")
    data = data.replace("/wiki/UCLA_School_of_Medicine", "/wiki/University_of_California,_Los_Angeles")
    data = data.replace("/wiki/Tufts_University_School_of_Medicine", "/wiki/Tufts_University")
    data = data.replace("/wiki/University_of_Massachusetts_Medical_School", "/wiki/University_of_Massachusetts")
    data = data.replace("/wiki/Harvard_School_of_Medicine", "/wiki/Harvard_University")
    data = data.replace("/wiki/Boston_University_School_of_Medicine", "/wiki/Boston_University")
    data = data.replace("/wiki/Harvard_Law_School", "/wiki/Harvard_University")
    data = data.replace("/wiki/Harvard_University_Law_School", "/wiki/Harvard_University")
    data = data.replace("/wiki/UNC_School_of_Medicine", "/wiki/University_of_North_Carolina_at_Chapel_Hill")
    data = data.replace("/wiki/Yale_School_of_Medicine", "/wiki/Yale_University")
    data = data.replace("/wiki/Stanford_University_School_of_Medicine", "/wiki/Stanford_University")
    data = data.replace("/wiki/Baylor_College_of_Medicine", "/wiki/Baylor_University")
    data = data.replace("/wiki/University_of_Texas_Southwestern_Medical_Center", "/wiki/University_of_Texas_at_Dallas")
    data = data.replace("/wiki/Weill_Cornell_Medicine", "/wiki/Cornell_University")
    data = data.replace("/wiki/Columbia_University_College_of_Physicians_and_Surgeons", "/wiki/Columbia_University")
    data = data.replace("/wiki/UCLA", "/wiki/University_of_California,_Los_Angeles")
    data = data.replace("/wiki/UC_Berkeley", "/wiki/University_of_California,_Berkeley")
    data = data.replace("/wiki/UC_San_Diego", "/wiki/University_of_California,_San_Diego")
    data = data.replace("/wiki/UC_Santa_Barbara", "/wiki/University_of_California,_Santa_Barbara")
    data = data.replace("/wiki/Gottingen_University", "/wiki/University_of_Gottingen")
    data = data.replace("/wiki/Georg_August_University_of_Gottingen", "/wiki/University_of_Gottingen")
    data = data.replace("/wiki/The_Rockefeller_University", "/wiki/Rockefeller_University")
    data = data.replace("/wiki/University_of_California_at_Berkeley", "/wiki/University_of_California,_Berkeley")
    data = data.replace("/wiki/University_of_Illinois_at_Urbana-Champaign", "/wiki/University_of_Illinois_Urbana-Champaign")
    data = data.replace("/wiki/University_of_Leiden", "/wiki/Leiden_University")
    data = data.replace("/wiki/University_of_Wisconsin,_Madison", "/wiki/University_of_Wisconsin-Madison")
    data = data.replace("/wiki/University_of_Colorado_at_Boulder", "/wiki/University_of_Colorado_Boulder")
    data = data.replace("/wiki/King's_College,_London", "/wiki/King's_College_London")
    data = data.replace("/wiki/Indiana_University,_Bloomington", "/wiki/Indiana_University_Bloomington")
    data = data.replace("/wiki/Trinity_College,_Cambridge", "/wiki/University_of_Cambridge")
    data = data.replace("/wiki/Gonville_and_Caius_College,_Cambridge", "/wiki/University_of_Cambridge")
    data = data.replace("/wiki/King's_College,_Cambridge", "/wiki/University_of_Cambridge")
    data = data.replace("/St_John's_College,_Cambridge", "/wiki/University_of_Cambridge")
    data = data.replace("/wiki/Peterhouse,_Cambridge", "/wiki/University_of_Cambridge")
    data = data.replace("/wiki/Corpus_Christi_College,_Cambridge", "/wiki/University_of_Cambridge")
    data = data.replace("/wiki/Fitzwilliam_College,_Cambridge", "/wiki/University_of_Cambridge")
    data = data.replace("/wiki/Churchill_College,_Cambridge", "/wiki/University_of_Cambridge")
    data = data.replace("/wiki/Sidney_Sussex_College,_Cambridge", "/wiki/University_of_Cambridge")
    data = data.replace("/wiki/St_John's_College,_Cambridge", "/wiki/University_of_Cambridge")
    data = data.replace("/wiki/Emmanuel_College,_Cambridge", "/wiki/University_of_Cambridge")
    data = data.replace("/wiki/Clare_Hall,_Cambridge", "/wiki/University_of_Cambridge")
    data = data.replace("/wiki/Cambridge_University", "/wiki/University_of_Cambridge")
    data = data.replace("/wiki/St._John's_College,_Cambridge", "/wiki/University_of_Cambridge")
    data = data.replace("/wiki/All_Souls_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Balliol_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Brasenose_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Christ_Church,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Corpus_Christi_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Exeter_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Green_Templeton_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Harris_Manchester_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Hertford_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Jesus_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Keble_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Kellogg_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Lady_Margaret_Hall,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Linacre_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Lincoln_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Magdalen_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Magdalen_College_School,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Mansfield_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Merton_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/New_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Nuffield_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Oriel_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Pembroke_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/The_Queen's_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Reuben_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/St_Anne's_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/St_Antony's_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/St_Catherine's_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/St_Cross_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/St_Edmund_Hall,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/St_Hilda's_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/St_Hugh's_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/St_John's_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/St_Peter's_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Somerville_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Trinity_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/University_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Wadham_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Wolfson_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Worcester_College,_Oxford", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/Oxford_University", "/wiki/University_of_Oxford")
    data = data.replace("/wiki/wiki/", "/wiki/")
    data = data.replace("/wiki/America's_Top_Colleges", "")
    #edits

    data = data.replace("%27", "'")
    data = data.replace("%2C", ",")
    data = data.replace("%252C", ",")
    data = data.replace("%2527", "'")
    data = data.replace("%2529", ")")
    data = data.replace("%2528", "(")

    f = open("data.json", "w", encoding="utf-8")
    f.write(data)
    f.close()

options = Options()
options.add_argument("--headless")  # Enable headless mode
service = Service(GeckoDriverManager().install())

def find_wiki_link(name):
    driver = webdriver.Firefox(service=service, options=options)

    try:
        driver.get("https://duckduckgo.com/")
        search = driver.find_element(By.NAME, "q")
        search.send_keys(name + " billionaire wikipedia")
        search.send_keys(Keys.RETURN)

        time.sleep(3)  # Allow time for search results to load
        
        # Get the page source and parse with BeautifulSoup
        source = driver.page_source
        soup = BeautifulSoup(source, 'html.parser')
        links = soup.find_all('a')
        
        for link in links:
            if "href" in link.attrs:
                if "wikipedia.org/" in link.attrs["href"] and "https" in link.attrs["href"]:
                    return link.attrs["href"]
    
    except Exception as e:
        print("Error:", e)
        return "Failed to find link"
    
    finally:
        driver.quit()

def has_it_been_done(name) :
    f = open("data.json", "r", encoding="utf-8")
    data = json.loads(f.read())
    f.close()
    for laureate in data :
        if name == laureate or name.replace(" & family", "") == laureate :
            return True
    return False

#generates data.json file, with a json of all the scraped data
def main() :
    #scrape_laureates() #retrieves all the wikipedia links of the laureates and saves them to "laureates.txt"
    f = open("input.csv", "r", encoding="utf-8")
    csv_reader = csv.reader(f)
    next(csv_reader)
    for row in csv_reader :
        if (len(row) == 0) :
            continue
        if (has_it_been_done(row[1])) :
            print("Already done " + row[1])
            continue
        try :
            time.sleep(2)
            name = row[1]
            name = name.replace(" & family", "")
            link = find_wiki_link(name)
            cur_alma_matters = scrape_wiki_data(link)
            json_data[name] = {}
            json_data[name]["link"] = link
            json_data[name]["alma_matters"] = cur_alma_matters
            json_data[name]["rank"] = row[0]
            json_data[name]["net_worth"] = row[2]
            json_data[name]["age"] = row[4]
            json_data[name]["source"] = row[5]
            json_data[name]["country"] = row[6]
            print(name + " went to " + str(cur_alma_matters))
            g = open("data.json", "w", encoding="utf-8")
            g.write(json.dumps(json_data, indent=4))
            g.close()
        except :
            name = row[1]
            print("\n\n\nFailed to get data for " + name + "\n\n\n")

    f.close()
    f = open("data.json", "w", encoding="utf-8")
    f.write(json.dumps(json_data, indent=4))
    f.close()



#main() #generates data.json using the laureates.txt file
fix_mistakes()
generate_list_of_universities() #generates universities.txt