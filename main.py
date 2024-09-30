import csv
from requests_html import HTMLSession
from bs4 import BeautifulSoup as BS


class Option:
    def __init__(self, text, data_bvalue) -> None:
        self.text = text
        self.data_bvalue = data_bvalue


class Question:
    def __init__(self, text: str, options: Option) -> None:
        self.text: str = text
        self.options: Option = options


class Response:
    def __init__(self, html_raw: str, question: Question) -> None:
        self.html_raw: str = html_raw
        self.question: Question = question

    def __repr__(self) -> str:
        return f"Response({self.question})"


class Node:
    def __init__(self, text: str, options: list[Option]) -> None:
        self.text: str = text
        self.options: list[Option] = options
        self.children: list[Node] = []

    def __repr__(self) -> str:
        return f"Node({self.text})"


def get_response(url: str) -> Response:
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


def traverse(url: str, depth: int = 3, visited=None) -> Node:
    if depth == 0:
        return None

    if visited is None:
        visited = {}

    if url in visited:
        return visited[url]

    response: Response = get_response(url)
    current_node = Node(response.question.text, response.question.options)

    visited[url] = current_node

    write_to_csv(url, current_node)

    for option in response.question.options:
        if option.data_bvalue.split(",")[0] == "20":
            continue

        next_url = f"{url},{','.join(option.data_bvalue.split(',')[::-1])}"
        print(next_url)
        child_node = traverse(next_url, depth - 1, visited)
        if child_node:
            current_node.children.append((option.text, child_node))

    return current_node


def write_to_csv(url: str, node: Node) -> None:
    with open("output.csv", "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        for option in node.options:
            writer.writerow([url, node.text, option.text, option.data_bvalue])


if __name__ == "__main__":
    root_url = "https://www.fdma.go.jp/relocation/neuter/topics/filedList9_6/kyukyu_app/kyukyu_app_web/index.html?A000Q0105,A811"

    with open("output.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["URL", "Question Text", "Option Text", "Option Value"])
    traverse(root_url, depth=10)
