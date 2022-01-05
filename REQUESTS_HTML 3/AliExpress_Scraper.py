# Requests-HTML Tutrial Part 3
from requests_html import HTMLSession
import pandas as pd

df = pd.DataFrame(columns=["Title", "Price", "qty_sold", "Rating", "Shipping"])

session = HTMLSession()

url = "https://best.aliexpress.com/?lan=en"
r = session.get(url)
r.html.render(sleep=1)
cats = r.html.find(
    "#home-firstscreen > div > div > div.categories > div > div.categories-list-box > dl.cl-item",
)

cats_list = []
for cat in cats:
    cat_link = list(cat.absolute_links)[0]
    cat_name = cat.text
    cat_dict = {"name": cat_name, "link": cat_link}
    cats_list.append(cat_dict)

for cat in cats_list:
    link = cat["link"]
    r = session.get(link)
    r.html.render(sleep=2, scrolldown=15)
    page_no = r.html.find(".total-page", first=True).text
    page_no = int(page_no.split(" ")[1])

    for page in range(1, page_no + 1):
        link = link + f"?page={page_no}"
        r = session.get(link)
        r.html.render(sleep=2, scrolldown=15)
        products = r.html.find(
            "#root > div.glosearch-wrap > div > div.main-content > div.right-menu > div > div.JIIxO > div._1OUGS"
        )

        for product in products:
            try:
                product_title = product.find(".awV9E", first=True).text
                product_price = product.find("._12A8D", first=True).text
                qty_sold = product.find("._2i3yA", first=True).text
                rating = product.find("._1hEhM", first=True).text
                shipping = product.find(".ZCLbI", first=True).text
                info_dict = {
                    "Title": product_title,
                    "Price": product_price,
                    "qty_sold": qty_sold,
                    "Rating": rating,
                    "Shipping": shipping,
                }
            except AttributeError:
                pass
            df = df.append(info_dict, ignore_index=True)

df.to_csv("AliExpress.csv")
