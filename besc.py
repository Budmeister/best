import os
import argparse
from antlr4 import *
from parser.BesLexer import BesLexer
from parser.BesParser import BesParser
from parser.BesVisitor import BesVisitor

def unexpected_child(child):
    raise ValueError(f"Unexpected {type(child)} child: {child.getText()}")

def validate_name(name: str):
    # TODO
    return True

def parse_file(filename):
    with open(filename, "r") as file:
        contents = file.read()

    input_stream = InputStream(contents)

    lexer = BesLexer(input_stream)
    token_stream = CommonTokenStream(lexer)

    parser = BesParser(token_stream)
    tree = parser.file_()

    return tree

def get_file_elements_rec(filepath, imported_files=None):
    if imported_files is None:
        imported_files = set()

    if filepath in imported_files:
        return [], [], []

    parsed_file = parse_file(filepath)
    children = parsed_file.getChildren()

    import_decls = []
    expr_stms = []
    let_stms = []
    fn_stms = []

    for child in children:
        if isinstance(child, BesParser.ImportDeclContext):
            import_decls.append(child)
        elif isinstance(child, BesParser.StatementContext):
            subchildren = list(child.getChildren())
            if len(subchildren) != 1:
                raise ValueError(f"Statement object had {len(subchildren)} subchildren")
            subchild = subchildren[0]

            if isinstance(subchild, BesParser.LetStmContext):
                let_stms.append(subchild)
            elif isinstance(subchild, BesParser.ExprStmContext):
                expr_stms.append(subchild)
            elif isinstance(subchild, BesParser.FunctionStmContext):
                fn_stms.append(subchild)
            else:
                unexpected_child(subchild)
        elif isinstance(child, tree.Tree.TerminalNodeImpl) and child.getText() == "<EOF>":
            pass
        else:
            unexpected_child(child)

    current_dir = os.path.dirname(filepath)
    for import_decl in import_decls:
        import_decl: BesParser.ImportDeclContext
        identifier = import_decl.IDENTIFIER().getText()
        if identifier.startswith("\\"):
            raise ValueError(f"Illegal import name: {identifier}")
        new_filepath = os.path.join(current_dir, f"{identifier}.bes")

        new_expr_stms, new_let_stms, new_fn_stms = get_file_elements_rec(new_filepath)
        expr_stms += new_expr_stms
        let_stms += new_let_stms
        fn_stms += new_fn_stms
        
    return expr_stms, let_stms, fn_stms


def compile_file(filepath):
    expr_stms, let_stms, fn_stms = get_file_elements_rec(filepath)
    for (stms, stms_name) in [(expr_stms, "expr_stms"), (let_stms, "let_stms"), (fn_stms, "fn_stms")]:
        print(f"{stms_name}: ")
        for stm in stms:
            print(stm.getText())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Basic example of argparse with one positional argument.")
    
    parser.add_argument("filepath", help="The name of the file to compile")
    
    args = parser.parse_args()
    
    compile_file(args.filepath)
