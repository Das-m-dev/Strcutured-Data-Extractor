import argparse

from extractor.pipeline import extract_invoice
from extractor.preprocess import load_text


def main():
    p = argparse.ArgumentParser(description="Extract structured invoice data from a .txt or .pdf file")
    p.add_argument("path")
    args = p.parse_args()
    result = extract_invoice(load_text(args.path))
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
