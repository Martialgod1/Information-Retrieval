import argparse
import os
from pathlib import Path

try:
    import lucene
    from java.nio.file import Paths
    from org.apache.lucene.analysis.standard import StandardAnalyzer
    from org.apache.lucene.document import Document, Field, StringField, StoredField, FieldType
    from org.apache.lucene.index import IndexWriter, IndexWriterConfig
    from org.apache.lucene.store import FSDirectory
    from org.apache.lucene.index import TieredMergePolicy
    from org.apache.lucene.index import IndexOptions
except Exception:
    print("PyLucene is required. Build/run via Docker in this folder.")
    raise


def ensure_jvm():
    try:
        env = lucene.getVMEnv()
        if env is None:
            lucene.initVM(vmargs=["-Djava.awt.headless=true"])
    except Exception:
        try:
            lucene.initVM(vmargs=["-Djava.awt.headless=true"])
        except ValueError:
            pass


def iter_text_files(sources):
    for src in sources:
        p = Path(src)
        if p.is_dir():
            for root, _dirs, files in os.walk(p):
                for fname in files:
                    fp = Path(root) / fname
                    if fp.suffix.lower() in {".txt", ".md"}:
                        yield fp
        elif p.is_file():
            yield p


def read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def create_writer(index_path: str) -> IndexWriter:
    directory = FSDirectory.open(Paths.get(index_path))
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    merge_policy = TieredMergePolicy()
    config.setMergePolicy(merge_policy)
    config.setUseCompoundFile(True)
    return IndexWriter(directory, config)


def build_tv_fieldtype() -> FieldType:
    ft = FieldType()
    ft.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)
    ft.setTokenized(True)
    ft.setStored(False)
    ft.setStoreTermVectors(True)
    ft.setStoreTermVectorPositions(True)
    ft.setStoreTermVectorOffsets(False)
    return ft


def add_doc(writer: IndexWriter, path: Path, text: str, ft: FieldType):
    doc = Document()
    doc.add(StringField("path", str(path), Field.Store.YES))
    doc.add(StoredField("filename", path.name))
    doc.add(Field("contents", text, ft))
    writer.addDocument(doc)


def main():
    parser = argparse.ArgumentParser(description="Advanced indexer with term vectors for feedback/expansion")
    parser.add_argument("--source", nargs="+", required=True, help="Files or directories to index")
    parser.add_argument("--index", required=True, help="Index directory path")
    args = parser.parse_args()

    ensure_jvm()
    os.makedirs(args.index, exist_ok=True)
    writer = create_writer(args.index)
    try:
        ft = build_tv_fieldtype()
        count = 0
        for fp in iter_text_files(args.source):
            text = read_text_safe(fp)
            add_doc(writer, fp, text, ft)
            count += 1
        writer.commit()
        print(f"Indexed {count} documents into {args.index} with term vectors.")
    finally:
        writer.close()


if __name__ == "__main__":
    main()


