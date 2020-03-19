# Will try to scrape a site using beautifull soup and request 
from bs4 import BeautifulSoup
import requests

def main():

    # getting the site we want to scrape in a "response object", then using the text() to get the source code.
    source = requests.get("http://quotes.toscrape.com/").text
    soup = BeautifulSoup(source, "lxml")

    quotes = soup.find(class_="row").find(class_="col-md-8")
    print(quotes.prettify())
if (__name__ == "__main__"):
    main()