######################################################################
##        Copyright (c) 2019 Carsten Wulff Software, Norway 
## ###################################################################
## Created       : wulff at 2019-3-25
## ###################################################################
##  The MIT License (MIT)
## 
##  Permission is hereby granted, free of charge, to any person obtaining a copy
##  of this software and associated documentation files (the "Software"), to deal
##  in the Software without restriction, including without limitation the rights
##  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
##  copies of the Software, and to permit persons to whom the Software is
##  furnished to do so, subject to the following conditions:
## 
##  The above copyright notice and this permission notice shall be included in all
##  copies or substantial portions of the Software.
## 
##  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
##  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
##  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
##  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
##  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
##  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
##  SOFTWARE.
##  
######################################################################

import os
import json
import sys
import collections
import datetime
import click
from collections import OrderedDict
import matplotlib.pyplot as plt
import pandas as pd

class rema:
    def __init__(self,file):
        with open(file,"r") as f:
            jsonobj = json.load(f)  

        cat_fn = "categories.json"
        categories = None
        if(os.path.exists(cat_fn)):
            with open(cat_fn,"r") as f:
                categories = json.load(f)

        self.categories = categories
        self.obj = jsonobj
        self.oformat = "str"


    def printGroups(self):
        groups = dict()
        transactions = self.obj["TransactionsInfo"]["Transactions"]
        for t in transactions:
            for item in t["Receipt"]:
                groups[item["ProductGroupDescription"]] = " "
            
        self.printList(groups)

    def printOrderByGroupOrCategory(self,maxcount=10,month = False,category=False,keyName=None,plot=False,quarter=False):
        summary = dict()

        if self.categories is None and category:
            print("Could not find categories.json. Can't run this command")  

        transactions = self.obj["TransactionsInfo"]["Transactions"]
        for t in transactions:
            datestr= str(t["PurchaseDate"])
            d = datetime.datetime.utcfromtimestamp(int(datestr[:-3]))
            if(month):
                header_key = str(d.year) + "-" + str(d.month)
            elif(quarter):
                header_key = str(d.year) + "-Q" + str(pd.Timestamp(d).quarter)
            else:
                header_key = str(d.year)
            if(header_key not in summary):
                summary[header_key] = dict()
            for item in t["Receipt"]:
                key = item["ProductGroupDescription"]
                if(category and key in self.categories ):
                    key = self.categories[key]
               # print(json.dumps(item,indent=4))
                if(keyName and key == keyName):
                    key = item['ProductDescription']
                elif(keyName):
                    continue
                if(key in summary[header_key]):
                    summary[header_key][key] += item["Amount"]
                else:
                    summary[header_key][key] = item["Amount"]

        self.printTransactionSummary(summary,maxcount,plot)
        
    

    def printTransactionSummary(self,summary,maxcount,plot):
        data = OrderedDict()
        for header_key in summary:
            transactions = summary[header_key]
            data[header_key] = list()
            listofTuples = sorted(transactions.items() ,reverse = True,  key=lambda x: x[1])
            count = 0
            for s in listofTuples:
                if(count >= maxcount):
                    continue
                else:
                    count += 1
                data[header_key].append((s[1],s[0]))
        if(plot):
            self.plotDictWithTouple(data)
            pass
        else:
            self.printDictWithTouple(data)

    def printList(self,data):
        """Print a list of items"""
        if(self.oformat == "json"):
            print(json.dumps(data,indent=4))
        else:
            for el in data:
                print(el)

    def plotDictWithTouple(self,data):
        """Print ordered dictionary where each item is a (number,description) touple"""
        pdata = dict()
        #- Reorganize data
        for key in data:
            for el in data[key]:
                val = el[0]
                name = el[1]
                if name not in pdata:
                    pdata[name] = dict()
                    pdata[name]['yval'] = list()
                    pdata[name]['xval'] = list()
                pdata[name]['yval'].append(val)
                pdata[name]['xval'].append(key)
        
        
        #with plt.xkcd():
        for key in pdata:
            plt.plot(pdata[key]['xval'],pdata[key]['yval'],label=key)
        plt.xlabel('Date [n]')
        plt.ylabel("Kostnad [kr]")
        plt.legend()
        plt.xticks(rotation=90)
        plt.savefig("plot.jpg")
            #plt.xlim([datetime.date(2016, 1, 1), datetime.datetime.now()])
            #plt.autoscale() 
        
        plt.show()


    def printDictWithTouple(self,data):
        """Print ordered dictionary where each item is a (number,description) touple"""
        if(self.oformat == "json"):
            print(json.dumps(data,indent=4))
        else:
            for key in data:
                print(str(key) + ":")
                for el in data[key]:
                    print("\t%.1f\t%s" %(el[0],el[1]))




#----------------------------------------------------------
#- Command line interface
#----------------------------------------------------------
@click.group()
@click.argument('data', type=click.Path(exists=True))
@click.option('--json',is_flag=True,help="Set JSON as output format")
@click.pass_context
def cli(ctx,data,json):
    ctx.ensure_object(dict)
    #Load the file
    r = rema(data)

    if(json):
        r.oformat = "json"
    else:
        r.oformat = "str"
    ctx.obj['rema'] = r
    
    
@cli.command('list',help="Sum and list items")
@click.pass_context
@click.option('--maxcount',default=10,help="Number of items to list")
@click.option('--month',is_flag=True,help="Sort per month")
@click.option("--category",is_flag=True,help="Sort by categories.json file")
@click.option("--item",help="Specify a certain group or category")
@click.option("--plot",is_flag=True,help="Plot items")
@click.option('--quarter',is_flag=True,help="Sort per quarter")
def group(ctx,maxcount,month,category,item,plot,quarter):
    ctx.obj['rema'].printOrderByGroupOrCategory(maxcount,month,category,item,plot,quarter)

@cli.command('listgroups',help="List all groups")
@click.pass_context
def listgroups(ctx):
    ctx.obj['rema'].printGroups()

if __name__ == "__main__":
    cli(obj = {})