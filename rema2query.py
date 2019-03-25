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

class rema:
    def __init__(self,file):
        with open(file,"r") as f:
            jsonobj = json.load(f)        
        self.obj = jsonobj

    def printOrderByGroup(self,maxcount=10):
        summary = dict()
        transactions = self.obj["TransactionsInfo"]["Transactions"]
        for t in transactions:
            datestr= str(t["PurchaseDate"])
            d = datetime.datetime.utcfromtimestamp(int(datestr[:-3]))
            year = d.year
            if(d.year not in summary):
                summary[year] = dict()
            #print(json.dumps(t["PurchaseDate"],indent=4))
            for item in t["Receipt"]:
                #print(json.dumps(item,indent=4))
                key = item["ProductGroupDescription"]
                if(key in summary[year]):
                    summary[year][key] += item["Amount"]
                else:
                    summary[year][key] = item["Amount"]
        for year in summary:
            transactions = summary[year]
            listofTuples = sorted(transactions.items() ,reverse = True,  key=lambda x: x[1])
            count = 0
            print(str(year) + ":\n")
            for s in listofTuples:
                if(count > maxcount):
                    continue
                else:
                    count += 1
                print("\t%.1f\t%s" %(s[1],s[0]))
        #return listofTuples
                #print(json.dumps(item,indent=4))
                #print("\n\n")
            


def main(filename):
    r = rema(filename)
    summary = r.printOrderByGroup()
        #print("%.1f\t%s" %(s[1],s[0]))
    #print(json.dumps(r.obj["TransactionsInfo"]["Transactions"] ,indent=4))



if __name__ == "__main__":
    main(sys.argv[1])