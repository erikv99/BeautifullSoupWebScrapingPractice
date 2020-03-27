# Author = Erik V.
# Github = https://github.com/erikv99
# Project for experimenting and practicing with webscraping using beautifulsoup. 
# Site i'm going to scrape = quotes to scrape.
# TODO:
# - make it crawl (also scrape other page numbers) (rn it only does the main page)
# - save data in a sql database using xampp. 
# - Maybe display the data on a page? or in a GUI?

# Imports
from bs4 import BeautifulSoup
import requests
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

def __getSoup(url):
    """Will return the soup object for our url"""

    try:

        # getting the site we want to scrape in a "response object", will timeout if connection takes more then 10 seconds or data hasn't been send for more then 10 seconds
        response = requests.get(url, timeout=10)
        source = response.content
        # calling raise_for_status to see if any HTTP errors occured.
        response.raise_for_status()

    # catching http errors (like 401 Unauthorized)
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error: ", errh)
        return None
    # catching connection errors
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting: ", errc)
        return None
    # catching timeout errors
    except requests.exceptions.Timeout as errt:
        print("Timeout Error: ", errt)
        return None
    # catching other exceptions (more general ones)
    except requests.exceptions.RequestException as err:
        print("General Error: ", err)
        return None

    # When no errors have occured
    else:

        # parsing the source code in to a soup object using a lxml parser
        soup = BeautifulSoup(source, "lxml")
        # returning our soup object
        return soup

def __scrapeQuotes(amountOfPages):
    """Will scrape x amount of pages saving quotes and authors"""
    # pageNumber will be incremented at the end of each scrape (each page)
    pageNumber = 1
    scrapedData = {}

    # Scraping x amount of pages
    for i in range(amountOfPages): 

        # First page is just the standard url
        if (pageNumber == 1):
            firstPageURL = "http://quotes.toscrape.com/"
            soup = __getSoup(firstPageURL)

        else:

            # different page number every time we come thru here
            pageToScrapeURL = "http://quotes.toscrape.com/page/{}/".format(str(pageNumber))
            soup = __getSoup(pageToScrapeURL)

        # Finding all the quote divs
        allDivs = soup.find_all("div", {"class":"quote"})
        
        # If we get empty divs we know there is no more content so we break
        if (len(allDivs) == 0):
            break

        # Looping thru each div
        for div in allDivs:

            quote = div.find("span", {"class":"text"}).text
            author = div.find("small", {"class":"author"}).text
            scrapedData.update({author : quote})
            print("Quote:\n" + quote + "\nAuthor:" + author + "\n")

        # Incrementing the page number
        pageNumber += 1

    print("\n\nScraped {} pages!".format(pageNumber - 1))
    return scrapedData
    
def __handleUserInput():
    """Will ask the number of pages to scrape from the user and check the input for problems will return the input"""
    while True:

        try: 

            userInput = int(input("How many pages would you like to scrape: "))

            if (userInput > 100):              
           
                print("Error: no more then 100 pages allowed!")

            else:
                
                return userInput

        except (ValueError, TypeError):

            print("Error: input must be a whole number!")

def __addToSQL(dataInDic):
    """Will add the given dictionary full of data to our sql database"""
    try:
        db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        passwd = "",
        database = "bs4scrape"
        )

        cursor = db.cursor()    
        sqlInsertQuery = "INSERT INTO quotes (author, quote) VALUES (%s, %s)"
        
        # Making a list of tuples / each tuple containing author and quote
        valuesToInsert = []
        # For each key / val we make a tuple and add it to the list
        for key, value in dataInDic.items():
            
            valuesToInsert.append((key, value))

        cursor.executemany(sqlInsertQuery, valuesToInsert)
        db.commit()
        print("Data succesfully inserted in table!")
        
    # Catching the error(s)
    except mysql.connector.Error as error:
        
        print("Failed to insert data into table {}".format(error))

    # Closing the connection in finally so if an error occurs (doesn't matter if we catch it) it will still close the connection
    finally:

        # Checking if the connection is still open
        if (db.is_connected()):
            # Closing the connection
            db.close()
            cursor.close()
            print("MySQL connection closed!")

def main():

    # Getting the amount of pages the user wants to scrape
    amountToScrape = __handleUserInput()
    # Getting the scraped data in a dictionary (k=author v=quote)
    scrapedData = __scrapeQuotes(amountToScrape)
    # Adding the author and quote to the database
    __addToSQL(scrapedData)

if (__name__ == "__main__"):
    main()