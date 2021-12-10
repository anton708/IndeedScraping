#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 10 01:35:54 2021

@author: lukericciardi
"""

from flask import Flask
from flask import request
from bs4 import BeautifulSoup
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np
import pandas as pd


app = Flask(__name__)


@app.route('/', methods=['GET'])
def homePage():
    return '''<body style="background-color:#DCDBDE"> <h1 style="font-size:2vw">Welcome to the company sentiment portal! There are two features available on this portal.</h1>   <br><br> 1. In order to pull reviews for a single given company, please put the full company name in the url.<br>(ie.) <a href="http://3.21.246.247:8080/Apple">http://3.21.246.247:8080/Apple</a> <br><br> This output will return how many reviews a company has (with a max of 200), the highest sentiment review, the lowest sentiment review, and the average sentiment of the company. <br><br> 2. If you would like to input multiple companies to compare them, write the companies in the URL separated by a comma using no spaces.<br>(ie.) <a href="http://3.21.246.247:8080/Apple,Microsoft,IBM">http://3.21.246.247:8080/Apple,Microsoft,IBM</a> <br><br> This will return how many reviews all of the companies have (with a max of 200), the highest sentiment review, the lowest sentiment review, and the average sentiment of each company in a table. <br> <br> This feature works best for comparisons. <br><br> <b>Please allow for around 10 seconds of run time per company entered </b> </body>'''

#   @Neil: Modified getReviews to handle one or more companies separated by a "," and to send output to a list which then populates a dictionary which will then load a pandas df.
@app.route('/<comp>', methods=['GET'])
def getReviews(comp):
    try:
        Companies = comp.split(",")
        CompNameList = []
        ReviewsCountList = []
        AvgSentimentList = []
        BestReviewList = []
        WorstReviewList = []

        for company in Companies:
            reviews = []
            pages = [0, 20, 40, 60, 80, 100, 120, 140, 160, 180]
            # looping through 10 pages on indeed to scrape reviews
            for page in pages:
                base_url = 'https://www.indeed.com/cmp/{}/reviews?start=' + str(page)
                url = base_url.format(company)

                header = {"User-Agent": "Mozilla/5.0 Gecko/20100101 Firefox/33.0 GoogleChrome/10.0"}

                page = requests.get(url, headers=header)
                soup = BeautifulSoup(page.content, 'lxml')
                try:
                    try:
                        compName = soup.find("div", class_="css-17x766f e1wnkr790").text
                    except:
                        compName = soup.find("div", class_="css-86gyd7 e1wnkr790").text
                except:
                    compName = company
                revs = soup.find_all("span", class_="css-1cxc9zk e1wnkr790")
                for rev in revs:
                    if "aria" in str(rev):
                        text = str(rev).replace('''<span class="css-82l4gy eu4oa1w0">''', "").replace("</span>",
                                                                                                      "").replace(
                            '''<br aria-hidden="true"/>''', "").replace(
                            '''<span aria-hidden="false" class="css-1cxc9zk e1wnkr790" lang="en-AU">''', "").replace(
                            "<span>", "").replace('''<span aria-hidden="false" class="css-1cxc9zk e1wnkr790">''', "")

                        if text != " " and text != "" and text is not None:
                            reviews.append(text)

            reviews = list(set(reviews))
            analyzer = SentimentIntensityAnalyzer()

            sentiment = []
            for review in reviews:
                sentiment.append(analyzer.polarity_scores(review)['compound'])

            reviewCount = len(reviews)
            meanSentiment = np.mean(sentiment)
            worstReview = reviews[sentiment.index(min(sentiment))]
            bestReview = reviews[sentiment.index(max(sentiment))]

            CompNameList.append(compName)
            ReviewsCountList.append(reviewCount)
            AvgSentimentList.append(meanSentiment)
            BestReviewList.append(bestReview)
            WorstReviewList.append(worstReview)

        df = pd.DataFrame(
            {"CompanyName": CompNameList, "ReviewsCount": ReviewsCountList, "AVG_Sentiment": AvgSentimentList,
             "BestReview": BestReviewList, "WorstReview": WorstReviewList})
        table = df.to_html(index=False, justify="center")

        if len(Companies) == 1:
            return '''<html> <body style="background-color:#DCDBDE"> <h1 style="font-size:2vw">Reviews were pulled for {name}.</h1><br><br> A total of {count} reviews were gathered averaging a sentiment score of  {sentiment}.<br><br><br> <b> The most negative review reads as follows:</b> <br> {worst} <br><br> <b>The most positive review reads as follows:</b><br> {best} </body></html>'''.format(name=compName,count= reviewCount,sentiment=meanSentiment,best=bestReview,worst=worstReview) 
        else:
            return table 
        
    # Error page when user gives wrong input
    except:
        return '''<html> <body style="background-color:#DCDBDE"> <p> <h1 style="font-size:2vw">Error:404 Not Found <br> This company does not exist or this is an invalid input.</h1><br><br> Please refer to <a href="http://3.21.246.247:8080">http://3.21.246.247:8080</a> for valid inputs.</p> </body> </html> '''


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)