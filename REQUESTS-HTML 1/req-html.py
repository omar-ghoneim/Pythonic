# Requests-HTML tutorial
from requests_html import HTML

with open("HTML/index.html", "r") as html_file:
    source = html_file.read()
    html = HTML(html=source)

posts = html.find("body > div")

for post in posts:
    try:
        post_title = post.find("h2", first=True).text
        post_link = (list(post.find("h2", first=True).links))[0]
        post_text = post.find("p", first=True).text
        print(post_title)
        print(post_link)
        print(post_text)
        print()
    except AttributeError:
        pass
