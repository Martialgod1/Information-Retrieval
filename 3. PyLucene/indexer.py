import argparse
import os
from pathlib import Path

try:
    import lucene
    from java.nio.file import Paths
    from org.apache.lucene.analysis.standard import StandardAnalyzer
    from org.apache.lucene.document import Document, Field, StringField, TextField, StoredField
    from org.apache.lucene.index import IndexWriter, IndexWriterConfig
    from org.apache.lucene.store import FSDirectory
    from org.apache.lucene.codecs.compressing import CompressionMode
    from org.apache.lucene.index import TieredMergePolicy
except Exception:
    print("PyLucene is required. See 3. PyLucene/README.md.")
    raise


def ensure_jvm():
    try:
        env = lucene.getVMEnv()
        if env is None:
            lucene.initVM(vmargs=["-Djava.awt.headless=true"])  # start JVM once
    except Exception:
        try:
            lucene.initVM(vmargs=["-Djava.awt.headless=true"])  # best effort
        except ValueError:
            pass


def iter_text_files(sources):
    for src in sources:
        p = Path(src)
        if p.is_dir():
            for root, _dirs, files in os.walk(p):
                for fname in files:
                    fp = Path(root) / fname
                    if fp.suffix.lower() in {".txt", ".md", ".py", ".java", ".pdf"}:
                        yield fp
        elif p.is_file():
            yield p


def read_text_safe(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def create_writer(index_path: str, best_compression: bool, use_compound: bool) -> IndexWriter:
    directory = FSDirectory.open(Paths.get(index_path))
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)

    if best_compression:
        # Try to set a Lucene codec with high compression, but fall back if unavailable.
        codec_set = False
        for mod_name, cls_name in [
            ("org.apache.lucene.codecs.lucene95", "Lucene95Codec"),
            ("org.apache.lucene.codecs.lucene94", "Lucene94Codec"),
            ("org.apache.lucene.codecs.lucene90", "Lucene90Codec"),
        ]:
            try:
                module = __import__(mod_name, fromlist=[cls_name])
                codec_cls = getattr(module, cls_name)
                config.setCodec(codec_cls(CompressionMode.HIGH_COMPRESSION))
                codec_set = True
                break
            except Exception:
                pass
        if not codec_set:
            print("Warning: No Lucene*Codec found for best-compression; using default codec.")

    merge_policy = TieredMergePolicy()
    config.setMergePolicy(merge_policy)
    config.setUseCompoundFile(use_compound)

    return IndexWriter(directory, config)


def add_doc(writer: IndexWriter, path: Path, text: str):
    doc = Document()
    doc.add(StringField("path", str(path), Field.Store.YES))
    doc.add(StoredField("filename", path.name))
    if text:
        doc.add(TextField("contents", text, Field.Store.NO))
    else:
        doc.add(TextField("contents", "", Field.Store.NO))
    writer.addDocument(doc)


def main():
    parser = argparse.ArgumentParser(description="Index files with PyLucene")
    parser.add_argument("--source", nargs="+", required=True, help="Files or directories to index")
    parser.add_argument("--index", required=True, help="Index directory path")
    parser.add_argument("--best-compression", action="store_true", help="Use codec with best compression mode")
    parser.add_argument("--use-compound", action="store_true", help="Write compound file segments")
    args = parser.parse_args()

    ensure_jvm()

    os.makedirs(args.index, exist_ok=True)
    writer = create_writer(args.index, args.best_compression, args.use_compound)
    try:
        count = 0
        for fp in iter_text_files(args.source):
            text = read_text_safe(fp)
            add_doc(writer, fp, text)
            count += 1
        writer.commit()
        print(f"Indexed {count} documents into {args.index}")
    finally:
        writer.close()


if __name__ == "__main__":
    main()


