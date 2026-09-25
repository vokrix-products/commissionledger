import os
import io
import csv
import json
import datetime
from openai import OpenAI
import pdfplumber
import openpyxl

ALLOWED_STATUSES = {
    'draft', 'active', 'expired', 'superseded', 'archived',
    'missing_plan', 'version_mismatch', 'needs_review', 'approved',
    'received', 'missing', 'late', 'duplicate', 'invalid_format',
    'partially_ingested', 'fully_ingested', 'unmatched_payer',
    'unmatched_payee', 'period_mismatch', 'currency_mismatch',
    'total_mismatch', 'flagged',
    'valid', 'expected', 'paid_as_expected', 'overpaid', 'short_paid',
    'underpaid', 'missing_payment', 'missing_statement_line',
    'unmatched_order', 'unmatched_payout', 'timing_difference',
    'unpaid', 'past_due', 'partially_paid', 'duplicate_payment',
    'duplicate_line', 'unauthorized_deduction', 'unauthorized_chargeback',
    'unauthorized_fee', 'unexpected_adjustment', 'incorrect_rate',
    'incorrect_tier', 'incorrect_split', 'incorrect_override',
    'net_terms_discrepancy', 'tax_withholding_discrepancy',
    'currency_difference', 'data_mismatch', 'disputed', 'resolved',
    'recovered', 'partially_recovered', 'not_recovered', 'written_off',
    'escalated', 'closed',
    'new', 'evidence_needed', 'ready_to_send', 'sent', 'acknowledged',
    'under_review', 'rejected', 'partially_approved',
    'aged_30', 'aged_60', 'aged_90_plus'
}

CANONICAL_FIELDS = {
    # Order / invoice fields
    'source_document_id', 'source_type', 'order_number', 'invoice_number',
    'order_date', 'invoice_date', 'booking_date', 'shipment_date', 'due_date',
    'payment_terms', 'net_terms_days', 'distributor_vendor_carrier_payer_name',
    'manufacturer_supplier_name', 'customer_account_name', 'end_customer_name',
    'ship_to_name', 'bill_to_name', 'sales_rep_name', 'sales_rep_id',
    'rep_firm_name', 'split_rep_1_name', 'split_rep_1_id',
    'split_rep_1_percent', 'split_rep_2_name', 'split_rep_2_id',
    'split_rep_2_percent', 'product_sku', 'product_name', 'product_family',
    'product_category', 'quantity', 'unit_price', 'gross_amount',
    'discount_amount', 'net_sales_amount', 'commissionable_sales_amount',
    'tax_amount', 'shipping_amount', 'currency', 'exchange_rate',
    'line_number', 'external_event_id', 'global_event_id', 'order_status',
    'invoice_status', 'source_file_name', 'source_row_number',
    # Payout / remittance fields
    'statement_id', 'payer_name', 'payee_name', 'payer_type',
    'statement_date', 'payment_date', 'period_start', 'period_end',
    'payment_reference', 'payment_method', 'statement_total', 'prior_balance',
    'carryover_balance', 'current_charges', 'referenced_order_number',
    'referenced_invoice_number', 'referenced_order_date',
    'referenced_invoice_date', 'referenced_customer_account_name',
    'referenced_product_sku', 'referenced_product_name', 'quantity_paid',
    'gross_sales_amount', 'commissionable_sales_amount',
    'commission_rate_paid', 'commission_amount_paid',
    'expected_commission_amount', 'variance_amount', 'variance_percent',
    'adjustment_amount', 'adjustment_code', 'adjustment_description',
    'deduction_amount', 'deduction_code', 'deduction_description',
    'chargeback_amount', 'chargeback_code', 'chargeback_description',
    'fee_amount', 'fee_code', 'tax_withheld_amount', 'net_paid_amount',
    'paid_after_due_date_flag', 'remittance_currency',
    'statement_line_status', 'statement_notes',
    # Plan configuration fields
    'plan_id', 'plan_name', 'plan_version', 'effective_start_date',
    'effective_end_date', 'plan_status', 'scope_type', 'scope_value',
    'rep_id', 'rep_name', 'channel_partner_name', 'distributor_name',
    'vendor_name', 'rate_type', 'flat_rate', 'tier_threshold', 'tier_rate',
    'quota_amount', 'accelerator_threshold', 'accelerator_rate',
    'split_percentage', 'override_percentage', 'draw_amount',
    'draw_recovery_rule', 'bonus_rule', 'chargeback_rule', 'net_terms_rule',
    'non_commissionable_rule', 'exclusion_rule', 'approver_name',
    'approved_at', 'created_by', 'updated_by', 'version_notes',
    # Derived reconciliation fields
    'reconciliation_line_id', 'reconciliation_period', 'match_status',
    'match_confidence', 'variance_type', 'discrepancy_reason', 'dispute_id',
    'dispute_status', 'dispute_owner', 'dispute_opened_at', 'dispute_due_date',
    'dispute_age_days', 'recovery_status', 'recovered_amount',
    'outstanding_amount', 'aging_bucket', 'evidence_count', 'last_action_at',
    'resolution_notes'
}

KEY_ALIASES = {
    'supplier': 'manufacturer_supplier_name',
    'vendor': 'manufacturer_supplier_name',
    'distributor': 'distributor_vendor_carrier_payer_name',
    'payer': 'payer_name',
    'payee': 'payee_name',
    'customer': 'customer_account_name',
    'customer_name': 'customer_account_name',
    'customer_account': 'customer_account_name',
    'end_customer': 'end_customer_name',
    'ship_to': 'ship_to_name',
    'bill_to': 'bill_to_name',
    'sales_rep': 'sales_rep_name',
    'rep': 'sales_rep_name',
    'rep_name': 'sales_rep_name',
    'rep_firm': 'rep_firm_name',
    'product': 'product_name',
    'sku': 'product_sku',
    'price': 'unit_price',
    'unit_price': 'unit_price',
    'gross': 'gross_amount',
    'amount': 'gross_amount',
    'quantity': 'quantity',
    'qty': 'quantity',
    'invoice_number': 'invoice_number',
    'order_number': 'order_number',
    'invoice_date': 'invoice_date',
    'order_date': 'order_date',
    'payment_date': 'payment_date',
    'statement_date': 'statement_date',
    'due_date': 'due_date',
    'payment_terms': 'payment_terms',
    'net_terms_days': 'net_terms_days',
    'currency': 'currency',
    'exchange_rate': 'exchange_rate',
    'line_number': 'line_number',
    'product_family': 'product_family',
    'product_category': 'product_category'
}

EXTRACTION_PROMPT = f"""
You extract structured commission reconciliation records from uploaded document text.
Return ONLY a JSON array of objects. No prose, no markdown fences.
Each object must have exactly these top-level keys:
- title: string, the primary entity the buyer tracks. For payout statements use payer_name or payee_name. For orders/invoices use distributor_vendor_carrier_payer_name, customer_account_name, or manufacturer_supplier_name. NEVER use document type or category like "Invoice" or "Payout Statement".
- status: string, one of: {', '.join(sorted(ALLOWED_STATUSES))}
- details: object with any other extracted fields using canonical names from the list below. This must be a JSON object, not a JSON string.
- due_date: string ISO-8601 date or null. due_date MUST be top-level, never inside details.

Canonical fields for orders/invoices:
source_document_id, source_type, order_number, invoice_number, order_date, invoice_date, booking_date, shipment_date, due_date, payment_terms, net_terms_days, distributor_vendor_carrier_payer_name, manufacturer_supplier_name, customer_account_name, end_customer_name, ship_to_name, bill_to_name, sales_rep_name, sales_rep_id, rep_firm_name, split_rep_1_name, split_rep_1_id, split_rep_1_percent, split_rep_2_name, split_rep_2_id, split_rep_2_percent, product_sku, product_name, product_family, product_category, quantity, unit_price, gross_amount, discount_amount, net_sales_amount, commissionable_sales_amount, tax_amount, shipping_amount, currency, exchange_rate, line_number, external_event_id, global_event_id, order_status, invoice_status, source_file_name, source_row_number.

Canonical fields for payout statements/remittances:
statement_id, payer_name, payee_name, payer_type, statement_date, payment_date, period_start, period_end, payment_reference, payment_method, currency, statement_total, prior_balance, carryover_balance, current_charges, line_number, referenced_order_number, referenced_invoice_number, referenced_order_date, referenced_invoice_date, referenced_customer_account_name, referenced_product_sku, referenced_product_name, quantity_paid, gross_sales_amount, commissionable_sales_amount, commission_rate_paid, commission_amount_paid, expected_commission_amount, variance_amount, variance_percent, adjustment_amount, adjustment_code, adjustment_description, deduction_amount, deduction_code, deduction_description, chargeback_amount, chargeback_code, chargeback_description, fee_amount, fee_code, tax_withheld_amount, net_paid_amount, payment_terms, due_date, paid_after_due_date_flag, remittance_currency, exchange_rate, statement_line_status, statement_notes, source_file_name, source_row_number.

Return [] if nothing meaningful is found.
"""

def _slugify(s):
    return str(s).strip().lower().replace(' ', '_').replace('-', '_')

def _normalize_key(raw_key):
    key = _slugify(raw_key)
    return KEY_ALIASES.get(key, key)

def _normalize_row(row):
    normalized = {}
    for raw_key, val in row.items():
        if raw_key is None:
            continue
        canonical = _normalize_key(raw_key)
        if canonical in CANONICAL_FIELDS:
            normalized[canonical] = val
        else:
            normalized[_slugify(raw_key)] = val
    return normalized

def _iso_date(value):
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    try:
        return datetime.date.fromisoformat(s[:10]).isoformat()
    except Exception:
        pass
    for fmt in (
        '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d',
        '%d-%b-%Y', '%b %d, %Y', '%d %b %Y'
    ):
        try:
            return datetime.datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    return None

def _extract_title(details, raw_row=None):
    title_fields = [
        'payer_name', 'payee_name', 'distributor_vendor_carrier_payer_name',
        'manufacturer_supplier_name', 'customer_account_name',
        'end_customer_name', 'sales_rep_name', 'rep_firm_name',
        'channel_partner_name', 'distributor_name', 'vendor_name'
    ]
    for field in title_fields:
        val = details.get(field)
        if val is not None and str(val).strip():
            return str(val).strip()
    if raw_row:
        for val in raw_row.values():
            if val is not None and str(val).strip():
                return str(val).strip()
    return 'Unnamed Record'

def _default_status(details, source_type):
    if source_type in ('csv', 'excel', 'tabular'):
        required_any = [
            'payer_name', 'payee_name', 'distributor_vendor_carrier_payer_name',
            'manufacturer_supplier_name', 'customer_account_name',
            'product_sku', 'product_name', 'invoice_number', 'order_number',
            'statement_id'
        ]
        if any(details.get(key) for key in required_any):
            return 'received'
        return 'needs_review'
    return 'needs_review'

def _records_from_rows(rows, source_type='csv'):
    records = []
    for row in rows:
        if not row:
            continue
        normalized = _normalize_row(row)
        details = dict(row)
        details.update(normalized)
        title = _extract_title(normalized, row)
        due_date = _iso_date(
            normalized.get('due_date')
            or normalized.get('invoice_date')
            or normalized.get('payment_date')
            or normalized.get('statement_date')
        )
        status = _default_status(normalized, source_type)
        records.append({
            'title': title,
            'status': status,
            'details': details,
            'due_date': due_date
        })
    return records

def _looks_like_csv(text):
    try:
        csv.Sniffer().sniff(text[:2048], delimiters=',;\t|')
        return True
    except Exception:
        return False

def _parse_csv_text(text):
    sample = text[:2048]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=',;\t|')
        reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    except Exception:
        reader = csv.DictReader(io.StringIO(text))
    rows = []
    for row in reader:
        if any(v is not None and str(v).strip() for v in row.values()):
            cleaned = {k.strip(): v for k, v in row.items() if k is not None}
            rows.append(cleaned)
    return rows

def _validate_records(records):
    valid = []
    for record in records:
        if not isinstance(record, dict):
            continue
        title = str(record.get('title') or 'Unnamed Record').strip()
        status = str(record.get('status') or 'needs_review')
        if status not in ALLOWED_STATUSES:
            status = 'needs_review'
        details = record.get('details')
        if not isinstance(details, dict):
            details = {}
        due_date = record.get('due_date')
        if due_date is None and 'due_date' in details:
            due_date = details.pop('due_date')
        due_date = _iso_date(due_date)
        valid.append({
            'title': title,
            'status': status,
            'details': details,
            'due_date': due_date
        })
    return valid

def _fallback_text_records(text):
    if _looks_like_csv(text):
        rows = _parse_csv_text(text)
        if rows:
            return _records_from_rows(rows, source_type='csv')
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    title = lines[0][:200] if lines else 'Unnamed Record'
    return [{
        'title': title,
        'status': 'needs_review',
        'details': {'raw_text': text[:5000]},
        'due_date': None
    }]

def _get_deepseek_client():
    return OpenAI(
        api_key=os.environ['DEEPSEEK_API_KEY'],
        base_url='https://api.deepseek.com'
    )

def _extract_with_llm(text):
    try:
        client = _get_deepseek_client()
        messages = [
            {'role': 'system', 'content': EXTRACTION_PROMPT},
            {'role': 'user', 'content': text[:30000]}
        ]
        response = client.chat.completions.create(
            model='deepseek-v4-flash',
            messages=messages
        )
        content = response.choices[0].message.content.strip()
        if content.startswith('```'):
            lines = content.splitlines()
            if lines and lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].startswith('```'):
                lines = lines[:-1]
            content = '\n'.join(lines)
        data = json.loads(content)
        return _validate_records(data)
    except Exception:
        return _fallback_text_records(text)

def _extract_records_from_mixed(text, source_type):
    if _looks_like_csv(text):
        rows = _parse_csv_text(text)
        if rows:
            return _records_from_rows(rows, source_type='csv')
    if os.environ.get('DEEPSEEK_API_KEY'):
        return _extract_with_llm(text)
    return _fallback_text_records(text)

def extract_text(file_bytes):
    try:
        import pdfplumber, io
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = ""
            for p in pdf.pages:
                text += (p.extract_text() or "") + "\n"
            if text.strip():
                return text
    except Exception:
        pass
    return file_bytes.decode("utf-8", errors="ignore")


def process_file(file_bytes: bytes) -> list[dict]:
    """
    Accept file bytes for PDF, Excel, CSV, or plain text.
    Always returns a list of record dicts with keys:
    title, status, details, due_date.
    """
    if not file_bytes:
        return []

    # Try PDF first.
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            texts = []
            for page in pdf.pages:
                page_text = page.extract_text() or ''
                texts.append(page_text)
            full_text = '\n'.join(texts).strip()
        if full_text:
            return _extract_records_from_mixed(full_text, 'pdf')
    except Exception:
        pass

    # Try Excel workbook next.
    try:
        wb = openpyxl.load_workbook(
            io.BytesIO(file_bytes),
            data_only=True,
            read_only=True
        )
        for ws in wb.worksheets:
            rows = list(ws.iter_rows(values_only=True))
            if not rows:
                continue
            headers = [
                str(c).strip() if c is not None else f'column_{i}'
                for i, c in enumerate(rows[0])
            ]
            data = []
            for row in rows[1:]:
                d = {}
                for i, val in enumerate(row):
                    if i < len(headers):
                        d[headers[i]] = val
                data.append(d)
            if data:
                return _records_from_rows(data, source_type='excel')
    except Exception:
        pass

    # Fall back to text / CSV decode.
    try:
        text = file_bytes.decode('utf-8', errors='ignore')
        if text.strip():
            return _extract_records_from_mixed(text, 'text')
    except Exception:
        pass

    # Last resort: return a single invalid-format record with raw content.
    raw = file_bytes[:1000].decode('latin-1', errors='ignore')
    return [{
        'title': 'Unnamed Record',
        'status': 'invalid_format',
        'details': {'raw_text': raw},
        'due_date': None
    }]
