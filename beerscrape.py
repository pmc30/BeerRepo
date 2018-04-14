# Scrape stuff off of beer advocate and do stuff with it later

from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
#import requests
#response = requests.get("http://en.wikipedia.org/wiki/January_1")
#soup = Soup(response.content)

import re
import csv
import pandas as pd


# beer advocate Neshaminy Creek Brewing Company url

#my_url = 'https://www.beermenus.com/places/9773-neshaminy-creek-brewing'
#my_url = 'https://www.beermenus.com/places/16936-the-drake-tavern'
my_url = 'https://www.beermenus.com/places/19185-big-top-beverage'
#my_url ='https://www.beermenus.com/places/28598-the-ginger-man-boston'
uClient = uReq(my_url)
page_url =uClient.read() 
uClient.close()

#filename = 'neshaminycreekbrewing.csv'
#filename = 'draketavern.csv'
filename = 'bigtopbeverage.csv'
#filename = 'thegingermanboston.csv'

with open(filename, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter=',')

    # encoding='utf-8' added to handle weird ascii characters
    #f = open(filename,'w', encoding='utf-8') 

    #headers = 'beer name,beer type,ABV,city brewed in,state brewed in,description,oz,container and price,oz,container and price \n'
    headers = ['beer name','type','ABV','city','state','description','oz','quanitity','price']
    writer.writerow(headers)
    tocsv = headers
    #f.write(headers)

    page_soup = soup(page_url, "html.parser")
    # get list where all beers are kept
    pageList = page_soup.find_all('li',{'class':'pure-list-item'})

    # itererate over every item in the list
    for x in pageList:
        listitems = x.find_all('p')
    # print(x.a)
        addline = ''
        # if the item has less than 1 paragraph it is ignored
        if len(listitems)>0:
            #print(listitems[0].text)
            [nm,bt,abv,city,state,dis,oz,quan,prc] = ['','','','','','','','','']    # set all values that will be written to csv blank initially
            word = x.a.text
            #print('\n' + word)
            addline += x.a.text
            addline += ','
            psave = [x.a.text]

            for xx in listitems:
                pList = re.split('; |\*|\n',xx.text)
                for xxx in pList:
                    pClean = xxx.strip()
                    if pClean != '' and pClean != '·':
                        #print(pClean)
                        # Makes sure that there is no unintentional delimiters (,) in the csv
                        addline += pClean.replace(',','|')
                        addline += ','
                        psave.append(pClean.replace(',','|'))
                        
            #addline += '\n'
            #f.write(addline)
            #print(psave)

            # Gotta have a psave[3]  exist or else it will crash when it checks for city,state
            if len(psave)<4:
                psave.append('')

            nm = psave[0]   # save name of beer

            # returns true if any character in psave[1] is NOT a digit, so that ABV is not accidently used
            if not any(char.isdigit() for char in psave[1]):
                bt = psave[1] # save beer type

            # check if city brewed in is listed. will have no numbers and only a few words
            if not any(char.isdigit() for char in psave[2]) and len(psave[2].split())<5 and any(char=='|' for char in psave[2]):
                [city,state] = psave[2].split('|')
            
            if not any(char.isdigit() for char in psave[3]) and len(psave[3].split())<5 and any(char=='|' for char in psave[3]):
                [city,state] = psave[3].split('|')           
            
            # iterate through alll items that are not the beer name
            for it in range(0,len(psave[1:])):
                
                words = psave[it+1].split()  # seperate each item into array of words (delimter=spaces)
                                            # 1 is added to psave index to avoid using iterating over name of beer 
                if len(words)==1:
                    words = words[0]    # convert words from list with one value to just string
                    # if 1 word and has % then it must be the ABV
                    if any(char=='%' for char in words):
                        
                        abv = float(words.rstrip('%'))   # convert ABV to a float and save
                        
                    # if 'oz' and one word then it is number of ounces
                    elif any(char=='o' for char in words) and any(char=='z' for char in words):
                        
                        oz = float(words.rstrip('oz'))

                        # if current entry in pSave was the oz, the next will be the price. then each word is iterated over 
                        quan = 1    # assume quanity of bottles is one
                        for word in psave[it+2].split():
                            
                            #check if there is quanity (ex. 6 bottles ) assoiciated with the price. If none given assume 1
                            if word.isdigit():
                                quan = float(word)

                            # if a word contains a dollar sign it must be the unit price
                            if any(char=='$' for char in word):
                                prc = float(word.lstrip('$'))

                elif len(words) > 5:
                    dis = psave[it+1]     # if more than 5 words it is probably the description      
                        
                

            


            #print(addline)
            addline = [nm,bt,abv,city,state,dis,oz,quan,prc]
            writer.writerow(addline)  
            #print(psave)
            #tocsv.append(addline)      

    # Looks confusing but just puts the name of the place at the end of the csv
    # Finds title of html page, get just text(no tags), split into a list to get rid of non titles, then get 1st valuein list
    # AKA the place title, then srtrip away uneeded spaces, then all inside a bracket so it is a list with one item
    writer.writerow([page_soup.title.text.split('-')[0].strip()])


    # my_df = pd.DataFrame(tocsv)
    # my_df = my_df.transpose()
    #my_df.to_csv(filename, index=False, header=False)
        #f.close()
        #re.split('; |, |\*|\n',a)
        #jj = list(map(lambda x: x.split() ,['pat carror','is','cool guy','45%'] ))