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

    def printOrderByGroupOrCategory(self,maxcount=10,month = False,category=False):
        summary = dict()

        if self.categories is None and categeory:
            print("Could not find categories.json. Can't run this command")  

        transactions = self.obj["TransactionsInfo"]["Transactions"]
        for t in transactions:
            datestr= str(t["PurchaseDate"])
            d = datetime.datetime.utcfromtimestamp(int(datestr[:-3]))
            if(month):
                header_key = str(d.year) + "-" + str(d.month)
            else:
                header_key = str(d.year)
            if(header_key not in summary):
                summary[header_key] = dict()
            for item in t["Receipt"]:
                key = item["ProductGroupDescription"]
                if(category and key in self.categories ):
                    key = self.categories[key]
                if(key in summary[header_key]):
                    summary[header_key][key] += item["Amount"]
                else:
                    summary[header_key][key] = item["Amount"]
        self.printTransactionSummary(summary,maxcount)
    
    def printOrderByGroup(self,maxcount=10,month = False):
        summary = dict()
        transactions = self.obj["TransactionsInfo"]["Transactions"]
        for t in transactions:
            datestr= str(t["PurchaseDate"])
            d = datetime.datetime.utcfromtimestamp(int(datestr[:-3]))
            year = d.year
            month = d.month
            if(d.year not in summary):
                summary[year] = dict()
            for item in t["Receipt"]:
                key = item["ProductGroupDescription"]
                if(key in summary[year]):
                    summary[year][key] += item["Amount"]
                else:
                    summary[year][key] = item["Amount"]

        self.printTransactionSummary(summary,maxcount)

    def printTransactionSummary(self,summary,maxcount):
        data = OrderedDict()
        for header_key in summary:
            transactions = summary[header_key]
            data[header_key] = list()
            listofTuples = sorted(transactions.items() ,reverse = True,  key=lambda x: x[1])
            count = 0
            for s in listofTuples:
                if(count > maxcount):
                    continue
                else:
                    count += 1
                data[header_key].append((s[1],s[0]))
        self.printDictWithTouple(data)

    

    def printList(self,data):
        if(self.oformat == "json"):
            print(json.dumps(data,indent=4))
        else:
            for el in data:
                print(el)

    #- Print function expects the following:
    # Ordered dictionary headers as keys, where each item in the dict is a touple
    # The touple needs to be (number, description)
    def printDictWithTouple(self,data):
        if(self.oformat == "json"):
            print(json.dumps(data,indent=4))
        else:
            for key in data:
                print(str(key) + ":")
                for el in data[key]:
                    print("\t%.1f\t%s" %(el[0],el[1]))




#----------------------------------------------------------
#- Command line
#----------------------------------------------------------

@click.group()
@click.argument('data', type=click.Path(exists=True))
@click.option('--oformat',default=str,help="Output format, json or str")
@click.pass_context
def cli(ctx,data,oformat):
    ctx.ensure_object(dict)
    #Load the file
    r = rema(data)
    r.oformat = oformat
    ctx.obj['rema'] = r
    
    
@cli.command('group',help="Top items ordered by group")
@click.pass_context
@click.option('--maxcount',default=10,help="Number of items to list")
@click.option('--month',is_flag=True,help="Sort per month")
def group(ctx,maxcount,month):
    ctx.obj['rema'].printOrderByGroupOrCategory(maxcount,month,category = False)

@cli.command('listgroup',help="List all groups")
@click.pass_context
def listgroup(ctx):
    ctx.obj['rema'].printGroups()


@cli.command('category',help="Top items ordered by category")
@click.pass_context
@click.option('--maxcount',default=10,help="Number of items to list")
@click.option('--month',is_flag=True,help="Sort per month")
def category(ctx,maxcount,month):
    ctx.obj['rema'].printOrderByGroupOrCategory(maxcount,month,category = True)

    

if __name__ == "__main__":
    cli(obj = {})