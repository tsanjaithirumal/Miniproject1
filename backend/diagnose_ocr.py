import os
import sys
from app import models, database
try:
    from PIL import Image
    import pytesseract
except ImportError:
    print("PIL or pytesseract not installed.")
    sys.exit(1)

# Tesseract Path Setup
possible_paths = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    os.path.join(os.getenv('LOCALAPPDATA', ''), r"Tesseract-OCR\tesseract.exe"),
    os.path.join(os.getenv('LOCALAPPDATA', ''), r"Programs\Tesseract-OCR\tesseract.exe"),
    r"C:\Tesseract-OCR\tesseract.exe"
]

print("Searching for Tesseract in:")
for path in possible_paths:
    print(f" - {path}")
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        print(f"✅ FOUND Tesseract at: {path}")
        break
else:
    print("❌ Tesseract NOT found in any common path.")

def test_tesseract():
    try:
        # Create a simple image with text
        img = Image.new('RGB', (100, 30), color = (255, 255, 255))
        # We can't easily write text without fonts, but we can try to run tesseract on blank or check version
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract Version: {version}")
        return True
    except Exception as e:
        print(f"❌ Tesseract Test Failed: {e}")
        return False

def check_docs():
    db = database.SessionLocal()
    docs = db.query(models.Document).all()
    print(f"\nChecking {len(docs)} documents...")
    
    for doc in docs:
        print(f"\nDocument ID: {doc.id}")
        print(f"Filename: {doc.filename}")
        print(f"Path: {doc.file_path}")
        
        if not os.path.exists(doc.file_path):
            print("❌ File does not exist on disk.")
            continue
            
        file_ext = os.path.splitext(doc.file_path)[1].lower()
        print(f"Type: {file_ext}")
        
        if file_ext == ".pdf":
            from pypdf import PdfReader
            try:
                reader = PdfReader(doc.file_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                print(f"Extracted Text Length (pypdf): {len(text)}")
                if len(text) < 10:
                    print("⚠️  Warning: Very little text extracted. This might be a scanned PDF.")
            except Exception as e:
                print(f"❌ PDF Read Error: {e}")

if __name__ == "__main__":
    print("--- Diagnostic Start ---")
    if test_tesseract():
        check_docs()
    print("--- Diagnostic End ---")
