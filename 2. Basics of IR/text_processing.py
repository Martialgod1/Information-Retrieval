import re
from typing import Iterable, List

try:
    
    import lucene  # type: ignore
    from org.apache.lucene.analysis.en import EnglishAnalyzer  # type: ignore
    from org.apache.lucene.analysis.tokenattributes import CharTermAttribute  # type: ignore
    from java.io import StringReader  # type: ignore
    _HAS_LUCENE = True
except Exception:
    _HAS_LUCENE = False


_DEFAULT_STOPWORDS = {
    "a","an","and","are","as","at","be","by","for","from","has","he","in","is","it",
    "its","of","on","that","the","to","was","were","will","with","this","these","those",
}


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[\-_/]", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str, use_lucene: bool = True) -> List[str]:
    if use_lucene and _HAS_LUCENE:
        if not lucene.getVMEnv():
            lucene.initVM(vmargs=["-Djava.awt.headless=true"])
        analyzer = EnglishAnalyzer()
        stream = analyzer.tokenStream("field", StringReader(text))
        term_attr = stream.addAttribute(CharTermAttribute.class_)
        stream.reset()
        tokens: List[str] = []
        while stream.incrementToken():
            tokens.append(term_attr.toString())
        stream.end()
        stream.close()
        analyzer.close()
        return tokens
    # Fallback simple regex tokenizer
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


def remove_stopwords(tokens: Iterable[str], stopwords: Iterable[str] = None) -> List[str]:
    sw = set(stopwords) if stopwords is not None else _DEFAULT_STOPWORDS
    return [t for t in tokens if t not in sw]


def stem_porter(tokens: Iterable[str]) -> List[str]:
    # Minimal Porter-like suffix stripping (no external deps); educational, not production-ready
    result: List[str] = []
    for t in tokens:
        original = t
        for suf in ("ing", "edly", "edly", "ed", "ly", "ies", "es", "s"):
            if t.endswith(suf) and len(t) > len(suf) + 1:
                t = t[: -len(suf)]
                break
        if t == "":
            t = original
        result.append(t)
    return result


def lemmatize_rule_based(tokens: Iterable[str]) -> List[str]:
    # Simple, tiny lemmatizer rules for demo
    lemmas: List[str] = []
    irregular = {"mice": "mouse", "men": "man", "children": "child", "geese": "goose"}
    for t in tokens:
        if t in irregular:
            lemmas.append(irregular[t])
            continue
        if t.endswith("ies") and len(t) > 3:
            lemmas.append(t[:-3] + "y")
        elif t.endswith("ves"):
            lemmas.append(t[:-3] + "f")
        elif t.endswith("s") and not t.endswith("ss") and len(t) > 3:
            lemmas.append(t[:-1])
        else:
            lemmas.append(t)
    return lemmas


def process_text(
    text: str,
    use_lucene: bool = True,
    remove_sw: bool = True,
    stemming: bool = False,
    lemmatization: bool = True,
):
    tokens = tokenize(text, use_lucene=use_lucene)
    if remove_sw:
        tokens = remove_stopwords(tokens)
    if stemming:
        tokens = stem_porter(tokens)
    if lemmatization:
        tokens = lemmatize_rule_based(tokens)
    return tokens


