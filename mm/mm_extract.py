import json
from pathlib import Path
from typing import Callable, Dict, List, Tuple


BASE_URL = "https://mmouterde.github.io/regles-ultimate-fr"

MYDIR = Path(__file__).parent.absolute()
ROOT_DIR = MYDIR.parent
SOURCE_DIR = ROOT_DIR / "src"
DATA_DIR = SOURCE_DIR / "_data"

# inputs
RULES_PATH = DATA_DIR / "rules.json"
DEFINITIONS_PATH = DATA_DIR / "definitions.json"

# outdir in the assets
OUTDIR = DATA_DIR / "facts"


def replace_all_links(markdown: str, base_url: str):
    """Replace self links to public links.

    self links are replace
    >>> replace_all_links("[plip](#plop)", "https://foo.bar")
    '[plip](https://foo.bar#plop)'

    This support some special characters
    >>> replace_all_links("[plip_plip](#plop_plop)", "https://foo.bar")
    '[plip_plip](https://foo.bar#plop_plop)'

    >>> replace_all_links("[plip-plip](#plop-plop)", "https://foo.bar")
    '[plip-plip](https://foo.bar#plop-plop)'

    >>> replace_all_links("[plip42](#plop42)", "https://foo.bar")
    '[plip42](https://foo.bar#plop42)'

    >>> replace_all_links("[17.3.1.](#rule-17.3.1.)", "https://foo.bar")
    '[17.3.1.](https://foo.bar#rule-17.3.1.)'
    """
    import re

    return re.sub(
        r"\[([\w\-\.]+)\]\(#([\w\-\.]+)\)", r"[\1](%s#\2)" % base_url, markdown
    )


def _text(rule: Dict):
    return rule["text"]


def _text_id_link(rule: Dict):
    return f"[{rule['id']}](#rule-{rule['id']}): {rule['text']}"


def _merge(
    rule: Dict, level=0, fnc: Callable[[Dict], str] = _text
) -> List[Tuple[str, int]]:
    """
    >>> d = {"text": "plop"}
    >>> _merge(d)
    [('plop', 0)]

    >>> d = {"text": "plop", "children": [{"text": "plip"}]}
    >>> _merge(d)
    [('plop', 0), ('plip', 1)]

    >>> d = {
    ... "text": "plop",
    ... "children": [{"text": "plip", "children": [{"text": "plup"}]}, {"text": "plap"}]
    ... }
    >>> _merge(d)
    [('plop', 0), ('plip', 1), ('plup', 2), ('plap', 1)]
    """
    # recursively concatenate all the children together
    items = [(fnc(rule), level)]
    if not "children" in rule or len(rule["children"]) == []:
        return items
    children = rule["children"]
    for child in children:
        items += _merge(child, level=level + 1, fnc=fnc)
    return items


def merge(rule: Dict, fnc: Callable[[Dict], str] = _text) -> str:
    """
    >>> d = {"text": "plop"}
    >>> merge(d)
    '* plop'

    >>> d = {"text": "plop", "children": [{"text": "plip"}]}
    >>> merge(d)
    '* plop\\n\\t* plip'

    >>> d = {
    ... "text": "plop",
    ... "children": [{"text": "plip", "children": [{"text": "plup"}]}, {"text": "plap"}]
    ... }
    >>> merge(d)
    '* plop\\n\\t* plip\\n\\t\\t* plup\\n\\t* plap'

    """
    # list of str + level
    merged = _merge(rule, level=0, fnc=fnc)
    # indent all the blocks
    merged = ["\t" * lvl + "* " + txt for (txt, lvl) in merged]
    merged = "\n".join(merged)
    return merged


def dump(fact_identifier: str, text: str):

    text = f"""## 🥏 Le point de règle du jour 🥏

fournit avec ❤️ par notre robot (_{fact_identifier}_)

---
{text}

---
[en savoir plus]({BASE_URL})
"""

    data = dict(
        text=text,
        # décommente pour spammer les copains sur le canal à chaque fois qu'une commande est invoquée
        # response_type="in_channel",
    )
    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / f"{fact_identifier}.json").write_text(json.dumps(data))


def extract_rules(json_path: str):
    rules = Path(json_path).read_text()
    rules = json.loads(rules)

    # on prend les règle au premier niveau et on merge chacune avec ses descendants
    # de manière à ce que l'ensemble reste cohérent (si on essaie d'être plus fin on
    # risque d'extraire des bouts qui n'ont pas trop de sens tout seul (ex: une
    # alternative d'une liste))
    for rule in rules:
        for section in rule.get("children", []):
            text = merge(section, fnc=_text_id_link)
            text = replace_all_links(text, BASE_URL)
            dump(f"fact-{section['id']}", text)


def extract_definitions(json_path: str):
    definitions = Path(json_path).read_text()
    definitions = json.loads(definitions)

    for definition in definitions:
        md = f"**{definition['term']}**: {definition['text']}"
        dump(f"fact-{definition['id']}", md)


def main():
    # on remplace tous les liens pour qu'il pointe vers le site
    extract_rules(RULES_PATH)
    extract_definitions(DEFINITIONS_PATH)


if __name__ == "__main__":
    import sys

    # poor's man cli
    if len(sys.argv) > 1:
        # e.g python mm_extract.py test
        import doctest

        doctest.testmod()
    else:
        main()
