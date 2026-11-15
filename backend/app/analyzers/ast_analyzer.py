"""Structure extraction from a Python AST (functions, classes, imports, calls, metrics inputs).

Everything is derived from ast nodes; no code is executed or imported.
"""
from __future__ import annotations

import ast
from dataclasses import asdict, dataclass, field
from typing import Iterator, Optional

FUNC_TYPES = (ast.FunctionDef, ast.AsyncFunctionDef)
NEST_TYPES = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith) + (
    (ast.Match,) if hasattr(ast, "Match") else ())


@dataclass
class FunctionInfo:
    name: str
    qualname: str
    lineno: int
    end_lineno: int
    params: list[str]
    returns: Optional[str]
    is_async: bool
    is_method: bool
    decorators: list[str]
    has_docstring: bool
    docstring: Optional[str]
    branches: int = 0
    loops: int = 0
    try_blocks: int = 0
    max_nesting: int = 0
    calls: list[str] = field(default_factory=list)
    calls_local: list[str] = field(default_factory=list)   # calls to functions defined in this module
    untyped_params: list[str] = field(default_factory=list)
    complexity: int = 1                                    # filled by complexity_analyzer
    complexity_tool: str = ""

    @property
    def length(self) -> int:
        return self.end_lineno - self.lineno + 1


@dataclass
class ClassInfo:
    name: str
    lineno: int
    end_lineno: int
    bases: list[str]
    methods: list[str]
    has_docstring: bool
    docstring: Optional[str]


@dataclass
class ImportInfo:
    module: str
    names: list[str]
    alias_map: dict[str, str]
    lineno: int


@dataclass
class ModuleStructure:
    path: str
    line_count: int
    has_docstring: bool
    docstring: Optional[str]
    functions: list[FunctionInfo]
    classes: list[ClassInfo]
    imports: list[ImportInfo]

    def to_dict(self) -> dict:
        return asdict(self)


def walk_shallow(node: ast.AST) -> Iterator[ast.AST]:
    """Yield descendants of `node` without descending into nested function/class/lambda scopes."""
    stack = list(ast.iter_child_nodes(node))
    while stack:
        n = stack.pop()
        yield n
        if isinstance(n, FUNC_TYPES + (ast.ClassDef, ast.Lambda)):
            continue
        stack.extend(ast.iter_child_nodes(n))


def dotted_name(node: ast.AST) -> Optional[str]:
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


def _unparse(node: Optional[ast.AST]) -> Optional[str]:
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except Exception:  # pragma: no cover - defensive
        return None


def _nesting(node: ast.AST, depth: int = 0) -> int:
    best = depth
    for child in ast.iter_child_nodes(node):
        if isinstance(child, FUNC_TYPES + (ast.ClassDef, ast.Lambda)):
            continue
        nd = depth + 1 if isinstance(child, NEST_TYPES) else depth
        best = max(best, _nesting(child, nd))
    return best


def _params(args: ast.arguments) -> tuple[list[str], list[str]]:
    allargs = list(getattr(args, "posonlyargs", [])) + list(args.args) + list(args.kwonlyargs)
    names = [a.arg for a in allargs]
    untyped = [a.arg for a in allargs if a.annotation is None and a.arg not in ("self", "cls")]
    if args.vararg:
        names.append("*" + args.vararg.arg)
        if args.vararg.annotation is None:
            untyped.append(args.vararg.arg)
    if args.kwarg:
        names.append("**" + args.kwarg.arg)
        if args.kwarg.annotation is None:
            untyped.append(args.kwarg.arg)
    return names, untyped


def extract_structure(tree: ast.Module, source: str, path: str) -> ModuleStructure:
    functions: list[FunctionInfo] = []
    classes: list[ClassInfo] = []
    imports: list[ImportInfo] = []

    def visit(node: ast.AST, scope: list[str], in_class: bool) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, FUNC_TYPES):
                qual = ".".join(scope + [child.name])
                names, untyped = _params(child.args)
                shallow = list(walk_shallow(child))
                calls = sorted({dotted_name(n.func) for n in shallow
                                if isinstance(n, ast.Call) and dotted_name(n.func)})[:60]
                doc = ast.get_docstring(child)
                functions.append(FunctionInfo(
                    name=child.name, qualname=qual, lineno=child.lineno,
                    end_lineno=getattr(child, "end_lineno", child.lineno) or child.lineno,
                    params=names, returns=_unparse(child.returns),
                    is_async=isinstance(child, ast.AsyncFunctionDef), is_method=in_class,
                    decorators=[_unparse(d) or "?" for d in child.decorator_list],
                    has_docstring=doc is not None, docstring=doc,
                    branches=sum(isinstance(n, (ast.If, ast.IfExp)) for n in shallow),
                    loops=sum(isinstance(n, (ast.For, ast.AsyncFor, ast.While)) for n in shallow),
                    try_blocks=sum(isinstance(n, ast.Try) for n in shallow),
                    max_nesting=_nesting(child), calls=calls, untyped_params=untyped))
                visit(child, scope + [child.name], False)
            elif isinstance(child, ast.ClassDef):
                doc = ast.get_docstring(child)
                classes.append(ClassInfo(
                    name=child.name, lineno=child.lineno,
                    end_lineno=getattr(child, "end_lineno", child.lineno) or child.lineno,
                    bases=[_unparse(b) or "?" for b in child.bases],
                    methods=[n.name for n in child.body if isinstance(n, FUNC_TYPES)],
                    has_docstring=doc is not None, docstring=doc))
                visit(child, scope + [child.name], True)
            else:
                if isinstance(child, ast.Import):
                    imports.append(ImportInfo(
                        module="", names=[a.name for a in child.names],
                        alias_map={(a.asname if a.asname else a.name.split(".")[0]): (a.name if a.asname else a.name.split(".")[0])
                                   for a in child.names},
                        lineno=child.lineno))
                elif isinstance(child, ast.ImportFrom):
                    mod = ("." * child.level) + (child.module or "")
                    imports.append(ImportInfo(
                        module=mod, names=[a.name for a in child.names],
                        alias_map={(a.asname or a.name): f"{mod}.{a.name}" for a in child.names},
                        lineno=child.lineno))
                visit(child, scope, in_class)

    visit(tree, [], False)

    local_names = {f.name for f in functions}
    for f in functions:
        f.calls_local = sorted({c.split(".")[-1] for c in f.calls
                                if c.split(".")[-1] in local_names and c.split(".")[-1] != f.name} |
                               ({f.name} if f.name in {c.split(".")[-1] for c in f.calls} else set()))
    mdoc = ast.get_docstring(tree)
    return ModuleStructure(path=path, line_count=len(source.splitlines()), has_docstring=mdoc is not None,
                           docstring=mdoc, functions=functions, classes=classes, imports=imports)
