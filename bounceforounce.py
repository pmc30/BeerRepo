# This program takes .csv files created by beerscrape.py (using beermenus.com) to find beers with mist alc per volume per price
# Created as an exercise in working with pandas

import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import glob


# Used to determine if a word is contained in the type column
def checkword(x,word):
    #return any(word in wor for wor in x['type'].split())
    return word in x['type']

# allow for the mean of the coulumn in a stated group. If group doent exits returns none
def group_mean(groupobj,group,column,mask):
    
    if any(mask):
        return groupobj.get_group(group)[column].mean()
    
    else:
        return 'none'




plt.figure()
plt.ion()

# csvnames = ['bigtopbeverage.csv','draketavern.csv','neshaminycreekbrewing.csv','thegingermanboston.csv']
# #csvnames = ['bigtopbeverage.csv','draketavern.csv','neshaminycreekbrewing.csv']
# csvnames = ['draketavern.csv','neshaminycreekbrewing.csv','thegingermanboston.csv']

csvnames = glob.glob('*.csv')   # Get all csv in the current folder

for nme in csvnames:
    #beers = pd.read_csv('thegingermanboston.csv')
    beers = pd.read_csv(nme)
    beers.name = beers.iloc[-1]['beer name']

    # create a mask that will get rid of every beer where there is a NaN in ABV, Qaunity,  oz, or price
    #beermask = np.isnan(beers['ABV']) | np.isnan(beers['quanitity']) | np.isnan(beers['oz']) | np.isnan(beers['price'])
    beermask = (beers['ABV']>0) & (beers['quanitity']>0) & (beers['oz']>0) & (beers['price']>0)
    #beermask = ~ beermask

    # dataframe of beers containing no NaNs
    bf=beers[beermask].copy()

    # quanity times oz is the total volume (oz), times ABV/100 is the amount of alchohol, then divided by price
    # to get alcohol per dollar
    bf['alc'] = bf['quanitity']*bf['oz']*bf['ABV']/100/bf['price']
    bf.name = beers.name
    # create a dataframe sorted from lowest alc to highest
    bfs = bf.sort_values(by='alc')

    # Check for single servings instead
    plt.title('Single Servings')
    singlemask = (bfs['quanitity']==1) & (bfs['oz']<25)
    bfsingle = bfs[singlemask].copy()
    bfsingle.name=bf.name
    if not any(singlemask):

        continue    #if there is no single serving skip this csv and continue for loop

    bf=bfsingle
    bf.name=bfsingle.name

    # create a new column for beer family. Assume at 1st all are other until a specific family is found
    bf['family'] = 'other'

    bf['type'] = bf['type'].fillna('')

    # create a boolean mask where only tpes including word IPA are true
    mask_ipa = bf.apply(checkword, axis=1, args=('IPA',))
    bf.loc[mask_ipa, 'family'] = 'IPA'

    mask_stout = bf.apply(checkword, axis=1, args=('Stout',))

    mask_stout = bf.apply(checkword, axis=1, args=('Porter',)) | mask_stout
    bf.loc[mask_stout, 'family'] = 'Stout'

    mask_cider = bf.apply(checkword, axis=1, args=('Cider',))
    bf.loc[mask_cider, 'family'] = 'Cider'

    # Count total beers in each catagory

    sumother = bf['family'].str.count('other').sum()
    sumcider = bf['family'].str.count('Cider').sum()
    sumstout = bf['family'].str.count('Stout').sum()
    sumipa = bf['family'].str.count('IPA').sum()

    # create groups for different family of beers
    famgroup = bf.groupby('family')


    print(bf.name)
    print('total ciders= ',sumcider, ' Avg alc= ', group_mean(famgroup,'Cider','alc',mask_cider),
    ' avg price= ',group_mean(famgroup,'Cider','price',mask_cider))
    print('total stouts= ',sumstout, ' Avg alc= ',group_mean(famgroup,'Stout','alc',mask_stout),
    ' avg price= ',group_mean(famgroup,'Stout','price',mask_stout))
    print('total IPAs= ',sumipa, ' Avg alc= ',group_mean(famgroup,'IPA','alc',mask_ipa),
    ' avg price= ', group_mean(famgroup,'IPA','price',mask_ipa))
    print('others= ',sumother, ' Avg alc= ',group_mean(famgroup,'other','alc',[sumother!=0]),
    ' avg price= ', group_mean(famgroup,'other','price',[sumother!=0]))
    print('')
    print(bfs.iloc[-1])
    print('')



    #bf['alc'].plot.box()
    bf['alc'].plot.hist(alpha=0.5,bins=20, label=bf.name)

    # for x in ['Stout','Cider','IPA']:
    #     famgroup.get_group(x)['alc'].plot.hist(alpha=0.8,bins=20)

    plt.legend(loc='upper right')
plt.xlabel('Alc/$')
plt.show()

