import graphviz
from main import traverse, Node


def draw_tree(root: Node):
    G = graphviz.Digraph(format="png")

    def add_edges(node: Node):
        for option_text, child_node in node.children:
            G.edge(node.text, child_node.text, label=option_text)
            add_edges(child_node)

    add_edges(root)

    G.render("output_tree", view=True)


if __name__ == "__main__":
    root_url = "https://www.fdma.go.jp/relocation/neuter/topics/filedList9_6/kyukyu_app/kyukyu_app_web/index.html?A000Q0105,A811"

    root_node = traverse(root_url, depth=3)

    draw_tree(root_node)
