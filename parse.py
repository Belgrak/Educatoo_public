from bs4 import BeautifulSoup
import requests
import random


# ===================================== WIKI HOW ======================================================================


def parse_wiki_how_categories():
    r = requests.get('https://ru.wikihow.com/Заглавная-страница')
    soup = BeautifulSoup(r.content, 'lxml')
    return [(i['href'], i.text) for i in soup.select('.cat_icon a')]


def parse_wiki_how_skill():
    skill_cat, cat_name = random.choice(parse_wiki_how_categories())
    r = requests.get('https://ru.wikihow.com' + skill_cat)
    soup = BeautifulSoup(r.content, 'lxml')
    return random.choice(
        [(i['href'], ' '.join(i.text.split()), cat_name) for i in soup.select('.responsive_thumb   a')])


def parse_about_skill():
    skill_link, skill_name, cat_name = parse_wiki_how_skill()
    r = requests.get(skill_link)
    soup = BeautifulSoup(r.content, 'lxml')
    description = soup.select_one('.mf-section-0').text
    methods = soup.select('.steps')
    yield skill_name + 2 * '\n'
    yield description
    for i in methods:
        if i.select_one('h3'):
            yield i.select_one('h3').text
        for t in i.select('.step'):
            yield t.text.strip('X\nИсточник информации\n')


# ===================================== WIKI HOW ======================================================================

# ===================================== CITATY INFO ===================================================================


def parse_citaty():
    r = requests.get('https://citaty.info/random')
    soup = BeautifulSoup(r.content, 'lxml')
    return soup.select_one('.field-items').text.strip() + '\n*' + soup.select('.field-items')[1].text.strip()


# ===================================== CITATY INFO ===================================================================

# ===================================== Pritchi ===================================================================


def parse_pritchi():
    r = requests.get('https://pritchi.ru/action_random')
    soup = BeautifulSoup(r.content, 'lxml')
    return soup.select_one('article .headline').text.strip() + '\n' + \
           '\n'.join([i.text.strip() for i in soup.select('article p')])

# ===================================== Pritchi ===================================================================
