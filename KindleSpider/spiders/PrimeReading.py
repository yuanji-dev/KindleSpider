import re
from datetime import date, datetime

import scrapy


class PrimereadingSpider(scrapy.Spider):
    name = "PrimeReading"
    allowed_domains = ["www.amazon.co.jp"]
    start_urls = [
        "https://www.amazon.co.jp/s?rh=n%3A2250738051%2Cn%3A2250739051%2Cn%3A2275256051%2Cp_n_special_merchandising_browse-bin%3A5304495051&s=date-desc-rank"
    ]

    def parse(self, response):
        max_page = int(
            response.css(".a-pagination li:nth-last-child(2)::text").get()
        )
        for page in range(1, max_page + 1):
            url = f"https://www.amazon.co.jp/s?rh=n%3A2250738051%2Cn%3A2250739051%2Cn%3A2275256051%2Cp_n_special_merchandising_browse-bin%3A5304495051&s=date-desc-rank&page={page}"
            yield scrapy.Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        for s in response.css("div[data-asin][data-uuid]"):
            asin = s.attrib.get("data-asin")
            title = s.css(".a-link-normal.a-text-normal span::text").get()
            _r = s.css("h2 + div").css("span[dir]::text,a::text").getall()
            _p_idx = _r.index("販売者:")
            if _r[: _p_idx - 1].count(" | "):
                author = "".join(
                    i.strip() for i in _r[_r.index(" | ") + 1 : _p_idx - 1]
                )
            else:
                author = "".join(i.strip() for i in _r[: _p_idx - 1])
            publisher = _r[_p_idx + 1].strip()
            publish_date = None
            if _r[_p_idx + 1 :].count(" | "):
                _publish_date_str = _r[_p_idx + 3].strip()
                publish_date = datetime.strptime(
                    _publish_date_str, "%Y/%m/%d"
                ).date()
            price = None
            _price_str = s.css(
                "div.a-section.a-spacing-none.a-spacing-top-mini > div > span::text"
            ).get()
            if _price_str:
                price = int(re.sub("[^0-9]", "", _price_str))
            _star_str = s.css(
                "span[aria-label]:first-child::attr(aria-label)"
            ).get()
            star = (
                float(_star_str.replace("5つ星のうち", "")) if _star_str else None
            )
            _rating_count_str = s.css(
                "span[aria-label]:last-child::attr(aria-label)"
            ).get()
            rating_count = (
                int(_rating_count_str.replace(",", ""))
                if _rating_count_str
                else None
            )
            cover = s.css("img::attr(src)").get()
            yield {
                "asin": asin,
                "title": title,
                "author": author,
                "publisher": publisher,
                "publish_date": publish_date,
                "price": price,
                "star": star,
                "rating_count": rating_count,
                "cover": cover,
            }
