from __future__ import annotations
from requests_html import HTMLSession
from bs4 import BeautifulSoup as BS
from dataclasses import dataclass


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


def get_response(url: str):
    session = HTMLSession()
    response = session.get(url)
    response.html.render()
    res = BS(response.html.html, "html.parser")
    html_raw = res.prettify()
    latest_article = res.select("article")[-1]
    options = latest_article.select("a[data-bkey='goto']")
    options = [Option(option.text, option["data-bvalue"]) for option in options]
    return Response(html_raw, Question(res.select(".subtitle")[-1].text, options))
