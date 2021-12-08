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
import pandas as pd


app = Flask(__name__)


@app.route('/', methods=['GET'])
def homePage():
    return "We need to make this page nicer <br><br>" + "In order to pull reviews for a given company, please put the full company name in the url.<br>(ie.) <b>http://3.21.246.247:8080/Apple</b> <br><br> If you would like to input multiple companies to compare them, write the companies in the URL separated by a comma using no spaces.<br>(ie.) <b>http://3.21.246.247:8080/Apple,Microsoft,IBM</b>"

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
                compName = soup.find("div", class_="css-17x766f e1wnkr790").text
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
            return "Reviews were pulled for " + str(compName) + ".<br><br>" + "A total of " + str(
                reviewCount) + " reviews were gathered averaging a sentiment score of " + str(
                meanSentiment) + ".<br><br><br>" + "The most negative review reads as follows:<br>" + str(
                worstReview) + "<br><br>" + "The most positive review reads as follows:<br>" + str(bestReview)
        else:
            return table
    # Error page when user gives wrong input

    except:
        return "<html><p> This company does not exist or this is an invalid input. Please refer to <b>http://3.21.246.247:8080/</b> for valid inputs."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
