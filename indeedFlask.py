#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 16:57:12 2021

@author: Anton
"""

from flask import Flask
from flask import request
from bs4 import BeautifulSoup
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np


app = Flask(__name__)

@app.route('/<company>',methods=['GET'])
def getReviews(company):    
    
    reviews = []
    pages = [20,40,60,80,100,120,140,160,180,200]
    for page in pages:
        base_url= 'https://www.indeed.com/cmp/{}/reviews?start=' + str(page)
        url = base_url.format(company)
        
        header = {"User-Agent":"Mozilla/5.0 Gecko/20100101 Firefox/33.0 GoogleChrome/10.0"}
        
        page = requests.get(url,headers = header)
        
        soup = BeautifulSoup(page.content, 'lxml')
        
        revs = soup.find_all("span", class_="css-1cxc9zk e1wnkr790")
        
        for rev in revs:
            if "aria" in str(rev):
                text = str(rev).replace('''<span class="css-82l4gy eu4oa1w0">''',"").replace("</span>","").replace('''<br aria-hidden="true"/>''',"").replace('''<span aria-hidden="false" class="css-1cxc9zk e1wnkr790" lang="en-AU">''',"").replace("<span>","").replace('''<span aria-hidden="false" class="css-1cxc9zk e1wnkr790">''',"")
    
                if text!=" " and text!="" and text is not None:
                    reviews.append(text)
    
    
    reviews = list(set(reviews))
    return("hello")
    analyzer = SentimentIntensityAnalyzer()
    
    sentiment = []
    for review in reviews:
        sentiment.append(analyzer.polarity_scores(review)['compound'])
    
    reviewCount = len(reviews)
    meanSentiment = np.mean(sentiment)
    worstReview = reviews[sentiment.index(min(sentiment))]
    bestReview = reviews[sentiment.index(max(sentiment))]
    return "The company you have entered is " + str(company) + ".<br><br>" + "A total of " + str(reviewCount) + " reviews were gathered averaging a sentiment score of " + str(meanSentiment) + ".<br><br><br>" + "The most negative review reads as follows:<br>" + str(worstReview) + "<br><br>" + "The most positive review reads as follows:<br>" + str(bestReview)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)