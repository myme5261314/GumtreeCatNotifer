#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2016 Peng Liu <myme5261314@gmail.com>
#
# Distributed under terms of the gplv3 license.

"""
This is the crawler and notifier for Gina to get latest cat info from gumtree.
"""


import time
import requests as rs
from bs4 import BeautifulSoup as bs
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
import smtplib

url = "http://www.gumtree.com.au/s-cats-kittens/launceston/c18435l3000393"
domain = "http://www.gumtree.com.au"


def load_exempt(path="./exempt.txt"):
    exempt_list = []
    with open(path) as f:
        for line in f.readlines():
            exempt_list.append(line.strip())
    return exempt_list


def abstract_entry(entry):
    result = {}
    result["name"] = entry("a", itemprop="url", class_="ad-listing__title-link")[0].text.strip()
    if result["name"].upper().startswith("WANTED"):
        result["name"]= ""
    result["price"]= entry("span", class_="j-original-price")[0].text.strip()
    result["add_datetime"]= entry("div", class_="ad-listing__date")[0].text.strip()
    result["entry_url"]= entry("a", itemprop="url")[0]["href"]
    img = entry("img")
    if len(img)==0:
        img = None
    else:
        img = img[0]["src"]
    result["img"] = img
    area = entry("span", class_="ad-listing__location-area")[0].text.strip()
    suburb = entry("span", class_="ad-listing__location-suburb")
    if len(suburb) == 0:
        suburb = ""
    else:
        suburb = suburb[0].text.strip()
    result["loc"] = area + suburb
    result["description"] = entry("p", class_="ad-listing__description")[0].text.strip()
    return result


def notify(result):
    # Send an HTML email with an embedded image and a plain text message for
    # email clients that don't want to display the HTML.


    # Define these once; use them twice!
    strFrom = 'my5261314@163.com'
    strTo = 'jingna93@163.com'

    # Create the root message and fill in the from, to, and subject headers
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = result["name"]
    msgRoot['From'] = strFrom
    msgRoot['To'] = strTo
    msgRoot.preamble = 'This is a multi-part message in MIME format.'

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    text_message_template = "Title: %s\nPrice: %s\nLocation: %s\nAdd Time: %s\nDescription: %s\n"
    text_message = text_message_template % (result["name"], result["price"], result["loc"] , result["add_datetime"], result["description"])
    # msgText = MIMEText('This is the alternative plain text message.')
    msgText = MIMEText(text_message)
    msgAlternative.attach(msgText)

    # We reference the image in the IMG SRC attribute by the ID we give it below
    html_msg = text_message.replace("\n", "<br>")
    if result["img"] is not None:
        html_msg += '<img src="%s">' % result["img"]
    html_msg += '<b><a href="%s">link</a></b>' % (domain + result["entry_url"])
    # msgText = MIMEText('<b>Some <i>HTML</i> text</b> and an image.<br><img src="cid:image1"><br>Nifty!', 'html')
    msgText = MIMEText(html_msg, 'html')
    msgAlternative.attach(msgText)

    # # This example assumes the image is in the current directory
    # fp = open('test.jpg', 'rb')
    # msgImage = MIMEImage(fp.read())
    # fp.close()

    # # Define the image's ID as referenced above
    # msgImage.add_header('Content-ID', '<image1>')
    # msgRoot.attach(msgImage)

    # Send the email (this example assumes SMTP authentication is required)
    smtp = smtplib.SMTP()
    smtp.connect('smtp.163.com')
    smtp.login('my5261314', '5261314')
    smtp.sendmail(strFrom, strTo, msgRoot.as_string())
    smtp.quit()


def main():
    exempt_list = load_exempt()
    while True:
        list_page = rs.get(url)
        list_page = bs(list_page.text)
        area = list_page("ul", id="srchrslt-adtable")
        entry_list = area[0]("li")
        result_list = [abstract_entry(entry) for entry in entry_list]
        result_list = [result for result in result_list if result["name"] != "" and result["entry_url"].split("/")[-1] not in exempt_list]
        for result in result_list:
            print(result)
            notify(result)
            exempt_list.append(result["entry_url"].split("/")[-1])
            time.sleep(20)
        with open("./exempt.txt", "a") as f:
            for result in result_list:
                idx = result["entry_url"].split("/")[-1]
                f.write("%s\n" % idx)
        time.sleep(120)


if __name__ == '__main__':
    main()
