# CommissionLedger

## Product

CommissionLedger is a commission reconciliation system. It ingests sales
orders, invoices, distributor payout statements, and commission plan
documents, extracts structured records from them, and reconciles expected
commission against what was actually paid to surface variances, deductions,
chargebacks, and disputes.

## Archetype

Input Adapter / Extraction Engine. The core deliverable is `processor.py`,
a pure function `process_file(file_bytes) -> list[dict]` that turns arbitrary
uploaded file bytes into normalized records. There is no web server or UI in
this phase.

## Extraction Pipeline

1. Detect file type from raw bytes (PDF, Excel, CSV, or plain text).
2. PDF: extract text per page with pdfplumber.
3. Excel: read worksheets with openpyxl and use the first row as headers.
4. CSV: sniff the delimiter and parse rows with the csv module.
5. Unstructured text or PDF text: if DEEPSEEK_API_KEY is set, call the
   DeepSeek chat API with a strict extraction prompt. Otherwise fall back to
a deterministic text/CSV parser.
6. Normalize keys via KEY_ALIASES, map to CANONICAL_FIELDS, validate status
   against ALLOWED_STATUSES, and normalize dates to ISO-8601.

## Output Record Contract

Every record returned by `process_file` has exactly these keys:

- `title`   - primary tracked entity (payer, payee, customer, supplier, or rep name). Never a document type.
- `status`  - one of the ALLOWED_STATUSES values; defaults to `needs_review`.
- `details` - JSON object of canonical fields plus any extra normalized values.
- `due_date` - ISO-8601 date string or null; always top level, never inside details.

`process_file` always returns a list. An empty input returns `[]`. Undecodable
bytes return a single record with status `invalid_format` and the raw content
in `details.raw_text`.

## Poller Input Expectations

The poller feeds raw file bytes into `process_file`. It expects:

- Supported inputs: `.pdf`, `.xlsx`/`.xlsm`, `.csv`, and `.txt` files, or any
  text-decodable byte stream.
- No filename metadata is required; detection is content based.
- For CSV and Excel, headers are matched against KEY_ALIASES and
  CANONICAL_FIELDS, so common headers like `supplier`, `vendor`, `payer`,
  `rep`, `sku`, `qty`, and `price` are mapped automatically.
- For PDFs and free text, structured extraction requires the
  `DEEPSEEK_API_KEY` environment variable. Without it, the poller still
  receives a fallback record so nothing is dropped.
- The poller should treat every returned record as a candidate for
  reconciliation and persist `title`, `status`, `due_date`, and the full
  `details` object.

## Files

- `processor.py`   - core extraction module.
- `run_demo.py`    - zero-arg hardcoded CSV demo, exits 0 in under 10 seconds.
- `run_tests.py`   - unit tests for CSV extraction, empty input, and fallback text.
- `requirements.txt` - openai, requests, pdfplumber, openpyxl.

## Setup

    pip install -r requirements.txt

For AI extraction from unstructured PDF/text documents:

    export DEEPSEEK_API_KEY=your_key_here

CSV and Excel files are processed deterministically without the API key.

## Usage

    python3 run_demo.py
    python3 run_tests.py

Dashboard: https://commissionledger.vokrix.co
Vercel: commissionledger
Railway: commissionledger
Cloudflare: commissionledger.vokrix.co

Billing: price_1UJN7k2c9uGCcgMSfEhHaz2E

Billing: price_1UJN7k2c9uGCcgMSfEhHaz2E

Landing: https://vokrix.co/commissionledger
