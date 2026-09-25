import pdfplumber

def extract_handbook_text(path="data/raw/Material/Introduction.pdf"):
    pages_text = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)
    return "\n".join(pages_text)

if __name__ == "__main__":
    text = extract_handbook_text()
    print(text[:1000])  # sanity check the first chunk of output