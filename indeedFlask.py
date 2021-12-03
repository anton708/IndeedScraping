#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 16:57:12 2021

@author: Anton
"""

from flask import Flask
app = Flask(__name__)

@app.route('/',methods=['GET'])
def helloworld():
    return "Hello World"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)