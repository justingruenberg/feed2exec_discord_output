import logging
import time
import json
import pytz
from bs4 import BeautifulSoup, Comment
from pprint import pprint 
from datetime import datetime

def cleanup(markup):
    soup = BeautifulSoup(markup, "html.parser")
    begining_element = soup.find(string=lambda text:isinstance(text,Comment) and "SC_OFF" in text)
    return "".join([elem.get_text(separator="\n") for elem in begining_element.find_next_siblings('div')]).replace("View Poll", "").strip()

def output(*args, feed=None, item=None, session=None, **kwargs):
    webhook_url = feed.get("webhook")
    post_user = feed.get("user", "quack")
    tzstr = feed.get("timezone", "").strip()
    tz = pytz.timezone(tzstr) if tzstr else pytz.utc

    if not webhook_url:
        logging.error("webhook not set in config, nowhere to post")
        return False

    if feed.get('catchup'):
        return True
    
    url = item.get("link")
    title = item.get("title")
    author = item.get("author_detail").get("name")
    author_link = item.get("author_detail").get("href")

    if "media_thumbnail" in item:
        image = item["media_thumbnail"][0].get("url", "")
    else:
        image = ""

    published = datetime.fromtimestamp(time.mktime(item.get("published_parsed")))
    published_str = published.replace(tzinfo=pytz.utc).astimezone(tz).strftime("%B %d, %Y at %I:%M %p")
    redditsub = item["tags"][0]["label"]
    
    summary = item.get("summary", "")
    if "SC_OFF" not in summary:
        summary = ""
    else:
        summary = cleanup(summary)

    post = {
        "username": post_user,
        "embeds": [{
            "color": 16729344,
            "author": {
                "name": author,
                "url": author_link
            },
            "title": title,
            "description": summary,
            "url": url,
            "footer": {
                "text": f"{redditsub} • Posted at {published_str}"
            }
        }]
    }

    if image:
        post["embeds"][0]["image"] = {"url": image}

    r = session.post(webhook_url, data=json.dumps(post), headers={"Content-Type": "application/json"})

    if r.ok:
        logging.debug("post to discord webhook appears successful")
        return True
    else:
        if r.status_code == 429:
            logging.debug("rate limited, skip for now")
            return False
        else:
            logging.error(f"post to discord webhook failed with code {r.status_code} with content {r.content}")
            return False
