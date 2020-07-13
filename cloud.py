import praw
import json
import argparse
import re
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from stop_words import safe_get_stop_words
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageColor

parser = argparse.ArgumentParser(description="Fetches comments from a reddit post and makes a word cloud")
parser.add_argument("--sub", action="store_true",
                    help="Treats the ID as the name of a sub")
parser.add_argument("id", type=str,
                    help="The ID of the reddit post")
parser.add_argument("-n", metavar="limit", type=int,
                    help="The amount of times \"More comments...\" is resolved. (Default: all)")
parser.add_argument("-p", metavar="posts", type=int,
                    help="Number of posts to fetch (Only in sub mode) (Default: 25)")
parser.add_argument("-l", nargs="+",
                    help="The languages to add stopwords for")
parser.add_argument("-o", metavar="out", type=str,
                    help="Output file")
parser.add_argument("-s", metavar="scale", type=int,
                    help="The scale of the wordcloud")
parser.add_argument("-m", metavar="mask", type=str,
                    help="The mask that is applied to the wordcloud")
parser.add_argument("-b", metavar="background", type=str,
                    help="Background color of the wordcloud")
parser.add_argument("-c", metavar=("cw", "cc"), type=str, nargs=2,
                    help="Width and color of contour")
parser.add_argument("--color", action="store_true",
                    help="Use mask as color mask")
parser.add_argument("-N", metavar="max_words", type=int,
                    help="Maximum number of words in WordCloud (Default 200)")

args = parser.parse_args()

if args.p is None:
    args.p = 25

if args.s is None:
    args.s = 1

if args.b is None:
    args.b = "black"

if args.N is None:
    args.N = 200


def fetch_comments(comment) -> list:
    if len(comment.replies) == 0:
        c = re.sub(r'(\[text\]\()?https?://[0-9A-Za-z/\?#\[\]@\.!$\&%\-+,;=]+\)?', '', comment.body)
        return [re.sub(r'https?://[0-9A-Za-z/\?#\[\]@\.!$\&%\-+,;=]+', '', c)]

    raw_comments = [comment.body]

    for comm in comment.replies:
        raw_comments.extend(fetch_comments(comm))

    return raw_comments


with open("config.json") as file:
    settings = json.load(file)

reddit = praw.Reddit(client_id=settings["client_id"],
                     client_secret=settings["secret"],
                     user_agent="Windows10:RWC:1.0")

if args.sub:
    posts = reddit.subreddit(args.id).hot(limit=args.p)
else:
    posts = [reddit.submission(id=args.id)]

i = 1
comments = []
for post in posts:
    print(f"\rFetching comments... {i}/{args.p}   ", end=" ", flush=True)
    post.comments.replace_more(limit=args.n)
    for top_level_comment in post.comments:
        comments.extend(fetch_comments(top_level_comment))
    i += 1

print(f"Done! Processed {len(comments)} comments")

stopwords = set(STOPWORDS)
if args.l is not None:
    for language in args.l:
        stopwords.update(safe_get_stop_words(language.lower()))

mask = None
colors = None
if args.m is not None:
    print("Creating mask...", end=" ", flush=True)
    mask = np.array(Image.open(args.m).convert("RGB"))
    colors = ImageColorGenerator(mask)
    print("Done!")

cw = 0
cc = None
if args.c is not None:
    cw = int(args.c[0])
    cc = args.c[1]

wordcloud = WordCloud(font_path="ARIALUNI.TTF",
                      max_words=args.N,
                      collocations=False,
                      scale=args.s,
                      stopwords=stopwords,
                      mask=mask,
                      background_color=args.b,
                      mode="RGB",
                      contour_width=cw,
                      contour_color=cc
                      ).generate(' '.join(comments))

if args.color is True:
    wordcloud.recolor(color_func=colors)

if args.o is not None:
    wordcloud.to_file(args.o)

plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")

plt.show()