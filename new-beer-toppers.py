from flask import Flask
from flask_ask import Ask, statement

import bs4 as bs
import requests 


class Record:
    def __init__(self, name, brewery):
        self.name = name
        self.brewery = brewery

    def __str__(self):
        return '{} by {}'.format(self.name, self.brewery)

url = 'https://www.beeradvocate.com/lists/new/'
source = requests.get(url)
soup = bs.BeautifulSoup(source.text, 'lxml')

app = Flask(__name__)
ask = Ask(app, "/new-beer-toppers")


@ask.launch
def start_skill():
    return find_top_beers()


@ask.intent("YesIntent")
def find_top_beers():
    return statement("Here are the top 10 rated beers added within the last year: {}".format(stringify_records(get_records())))


@ask.intent("NoIntent")
def no_intent():
    return statement('Alright, bye then!')


def get_records():
    records = []
    try:
        table = soup.find('table')
        rows = table.find_all('tr')
        # ignore the first two header rows -- each row after represents one beer
        for row in rows[2:12]:
            links = row.find_all('a')
            name = links[0].find('b').text.strip()
            brewery = links[1].text.strip()
            records.append(Record(name, brewery))
    except:
        # just eat the exception
        pass

    return records


def stringify_records(records):
    if not records:
        response = "I'm sorry, I couldn't get any top beer information"
    elif len(records) == 1:
        response = str(records[0])
    else:
        response = ', '.join(str(record) for record in records[:-1])
        response += ', and ' + str(records[-1])

    return response

if __name__ == '__main__':
    app.run(debug=True)
