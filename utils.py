from __future__ import annotations
from requests_html import HTMLSession
from bs4 import BeautifulSoup as BS
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor


@dataclass
class Option:
    text: str
    goto: str


@dataclass
class Question:
    text: str
    options: list[Option] = None


@dataclass
class Response:
    html_raw: str
    question: Question

    def __repr__(self) -> str:
        return f"Response({self.question})"


def get_response_sync(url: str):
    session = HTMLSession()
    response = session.get(url)
    response.html.render()
    res = BS(response.html.html, "html.parser")
    html_raw = res.prettify()
    latest_article = res.select("article")[-1]
    options = [
        Option(option.text, option["data-bvalue"])
        for option in latest_article.select("a[data-bkey='goto']")
    ]
    return Response(html_raw, Question(res.select(".subtitle")[-1].text, options))


async def get_response(url: str):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(pool, get_response_sync, url)


import asyncio

base_url = "https://www.fdma.go.jp/relocation/neuter/topics/filedList9_6/kyukyu_app/kyukyu_app_web/index.html?A000Q0105,A811"


async def main():
    response = await get_response(base_url)
    print(response)
