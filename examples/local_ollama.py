"""Example script demonstrating extraction using a local small reasoning model via Ollama.

To run this:
1. Install Ollama (https://ollama.com/)
2. Run a small reasoning model, for example: `ollama run deepseek-r1:1.5b` or `ollama run llama3.2`
3. `pip install -e .` from the repo root, then: `python examples/local_ollama.py`
"""

from fastdocparse import Schema, Field, LLMClient, DocumentParser

def run_local_extraction():
    # 1. Define your schema
    schema = Schema(
        name="Invoice",
        fields=[
            Field(name="invoice_number", description="The invoice number", required=True),
            Field(name="total_price", description="Total amount due", type="number", required=True),
            Field(name="vendor_name", description="Name of the company issuing the invoice"),
        ]
    )

    # 2. Point the LLMClient to your local Ollama instance
    # Ollama provides an OpenAI-compatible API on port 11434 by default.
    client = LLMClient(
        base_url="http://localhost:11434/v1",
        api_key="ollama", # API key is not required for local Ollama, but standard clients often expect a string
        model="deepseek-r1:1.5b" # Replace with whichever model you downloaded via Ollama
    )

    parser = DocumentParser(client=client)

    # 3. Provide some dummy document bytes (In a real scenario, read a real PDF or Image)
    # We will use a mock here just to demonstrate the logic.
    print(f"[*] Compiling prompt and connecting to local model: {client.model}...")
    
    # We'll monkeypatch the internal pdf_utils just to feed it plain text without needing a real PDF for the demo
    from unittest.mock import patch
    sample_invoice_text = "Vendor: Tech Supplies Inc.\nInvoice Number: INV-2023-001\nTotal Due: $450.00"
    
    with patch("fastdocparse.parser.extract_text_from_pdf", return_value=sample_invoice_text):
        try:
            # We pass b"dummy" because the patch intercepts the actual PDF parsing
            result = parser.extract(b"dummy_pdf_data", schema)
            
            print("\n[+] Extraction Successful!")
            print(result)
            
        except Exception as e:
            print(f"\n[-] Extraction failed. Make sure Ollama is running and the model '{client.model}' is pulled.")
            print(f"Error: {e}")

if __name__ == "__main__":
    run_local_extraction()
