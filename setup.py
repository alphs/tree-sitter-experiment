from pprint import pprint
from typing import Generator
import tree_sitter as ts


def traverse_tree(tree: ts.Tree) -> Generator[ts.Node, None, None]:
    cursor = tree.walk()

    visited_children = False
    while True:
        if not visited_children:
            if cursor.node.is_named:
                yield cursor.node
            if not cursor.goto_first_child():
                visited_children = True
        elif cursor.goto_next_sibling():
            visited_children = False
        elif not cursor.goto_parent():
            break


ts.Language.build_library(
    "build/tree-sitter-cpp-lib.so",
    ["vendor/tree-sitter-cpp"]
)
CPP_LANUAGE = ts.Language("build/tree-sitter-cpp-lib.so", "cpp")

parser = ts.Parser()
parser.set_language(CPP_LANUAGE)

# with open("example-file.cpp", "rb") as f:
with open("example.cpp", "rb") as f:
    src_data = f.read()


def read_callable_byte_offset(byte_offset, point):
    return src_data[byte_offset:byte_offset + 1]


tree = parser.parse(read_callable_byte_offset)
# tree_it = map(lambda node: node, traverse_tree(tree))

funcs_with_target = set()

root_node = tree.root_node
assert root_node.type == "translation_unit"

for func_def in root_node.named_children:
    if func_def.type == "declaration":
        continue

    assert func_def.type == "function_definition"
    func_dec = func_def.child(1)
    assert func_dec.type == "function_declarator"
    func_ident = func_dec.child(0)
    assert func_ident.type == "identifier"
    func_name = src_data[func_ident.start_byte:func_ident.end_byte]
    print(f"{func_name=}")

    func_body = func_def.child(2)
    assert func_body.type == "compound_statement"
    for node in traverse_tree(func_body):
        if node.type == "field_identifier":
            pot_match = src_data[node.start_byte:node.end_byte]
            print(f"++++++++++\n{pot_match=}")
            if pot_match.decode("utf-8") == "setB":
                funcs_with_target = func_name.decode('utf-8')
                continue
        # print(node.type)

print("end.")
pprint(funcs_with_target)
