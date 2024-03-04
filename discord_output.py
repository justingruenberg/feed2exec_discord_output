import logging
import time
import json
from bs4 import BeautifulSoup
from pprint import pprint 

def cleanup(html):
    # parse html content
    soup = BeautifulSoup(html, "html.parser")
 
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()
 
    # return data by retrieving the tag content
    output = ' '.join(list(soup.stripped_strings)[:-4])
    output = output.replace("View Poll", "").strip()
    return output

def output(*args, feed=None, item=None, session=None, **kwargs):
    webhook_url = feed.get("webhook")
    post_user = feed.get("user", "quack")

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

    published = item.get("published_parsed")
    published_str = time.strftime("%B %d, %Y at %I:%M %p", published)
    reddit = item["tags"][0]["label"]
    
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
                "text": f"{reddit} • Posted at {published_str}"
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
