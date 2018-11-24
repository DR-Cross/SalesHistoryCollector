import os
import csv
import requests
import datetime
import traceback
from glob import glob
from bs4 import BeautifulSoup
from collections import Counter
from ebaysdk.finding import Connection as finding


#if you pip install ebaysdk requests and bs4, this program ought to run
#out of the box
def collect():
    global soup
    api = finding(appid='api key goes here', config_file=None)
    #The sellername value is set to a local ebay auto recycler
    #named Axis_Auto a.k.a. Joes Auto Wrecking North Ridgeville Ohio.
    SellerNameValue = 'axis_auto'
    datecode = str(datetime.datetime.now()).split(' ')[0].replace('-','.')
    Path_Project = '/'.join(__file__.replace('\\','/').split('/')[:-1]) + '/Sellers/' + SellerNameValue  + '/ActiveAndCompleted.' + datecode + '/Api Content/'
    Path_Continue = '/'.join(__file__.replace('\\','/').split('/')[:-1]) + '/Sellers/' + SellerNameValue  + '/ActiveAndCompleted.' + datecode + '/Continue/'
    if not os.path.exists(Path_Project + '/'): os.makedirs(Path_Project + '/')

    incr = 1
    list_priceranges = [str(i+.01)+'-'+str(i+incr) for i in range(0,10000,incr)]

    #for each price range in my list of price ranges
    #make two requests. one request for the seller's sale history
    #for products at that price, and another for his current active listings
    #at that price. price splitting helps maximize the number of results you get
    for pricerange in list_priceranges:
        print()
        print()
        pricevaluemin = pricerange.split('-')[0]
        pricevaluemax = pricerange.split('-')[1]
        
        Dictionary_ApiRequest = {
            'paginationInput': {'pageNumber':1},
            'outputSelector': 'SellerInfo',
            'itemFilter': [
                {'name': 'Seller', 'value': SellerNameValue},
                {'name': 'MinPrice', 'paramName': 'USD', 'value': pricevaluemin},
                {'name': 'MaxPrice', 'paramName': 'USD', 'value': pricevaluemax},
        ]}       
        response = api.execute('findItemsAdvanced', Dictionary_ApiRequest)
        soup = BeautifulSoup(response.content,'lxml')
        try: totalentries = str(soup.totalentries.text)
        except: continue

        totalpages = str(soup.totalpages.text)
        if int(totalpages) > 100: totalpages = str(100)

        print()
        print()
        print('active price: ' + str(pricerange))
        print('totalentries: ' + totalentries)
        print('totalpages: ' + totalpages)
        
        for page in range(1, int(totalpages) + 1):
            continuetext = Path_Continue + '/pricerange.'+pricerange+'_sold.active_page.'+str(page)
            if os.path.exists(continuetext+'/'): continue
            os.makedirs(continuetext+'/')

            print('active, price: ' + str(pricerange) + ', page: ' + str(page))
            Dictionary_ApiRequest['paginationInput'] = {'pageNumber': str(page)}
            response = api.execute('findItemsAdvanced', Dictionary_ApiRequest)
            soup = BeautifulSoup(response.content, 'lxml')

            filetext = Path_Project + '/active_pricerange.' + str(pricerange) + '_page.' + str(page) + '.txt'
            file = open(filetext,'w')
            file.write(str(soup))
            file.close()
            
        Dictionary_ApiRequest = { 
            'paginationInput': {'pageNumber':1},
            'outputSelector': 'SellerInfo',
            'itemFilter': [
                {'name': 'Seller', 'value': SellerNameValue},
                {'name': 'SoldItemsOnly', 'value': 'false'},
                {'name': 'MinPrice', 'paramName': 'USD', 'value': pricevaluemin},
                {'name': 'MaxPrice', 'paramName': 'USD', 'value': pricevaluemax},
        ]}       
        response = api.execute('findCompletedItems', Dictionary_ApiRequest)
        soup = BeautifulSoup(response.content,'lxml')
        try: totalentries = str(soup.totalentries.text)
        except: continue

        totalpages = str(soup.totalpages.text)
        if int(totalpages) > 100: totalpages = str(100)

        print()
        print()
        print('completed price: ' + str(pricerange))
        print('totalentries: ' + totalentries)
        print('totalpages: ' + totalpages)
        
        for page in range(1, int(totalpages) + 1):
            continuetext = Path_Continue + '/pricerange.'+pricerange+'_sold.completed_page.'+str(page)
            if os.path.exists(continuetext+'/'): continue
            os.makedirs(continuetext+'/')

            Dictionary_ApiRequest['paginationInput'] = {'pageNumber': str(page)}
            response = api.execute('findCompletedItems', Dictionary_ApiRequest)
            soup = BeautifulSoup(response.content, 'lxml')

            filetext = Path_Project + '/completed_pricerange.' + str(pricerange) + '_page.' + str(page) + '.txt'
            file = open(filetext,'w')
            file.write(str(soup))
            file.close()
            print('completed, price ' + str(pricerange) + ', page: ' + str(page))            
    printfunctions()
    

collect()
