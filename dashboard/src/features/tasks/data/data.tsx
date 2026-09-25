import {Clock, CircleCheckBig, TriangleAlert} from 'lucide-react'

export const labels = [
  {
    value: 'bug',
    label: 'Bug',
  },
  {
    value: 'feature',
    label: 'Feature',
  },
  {
    value: 'documentation',
    label: 'Documentation',
  },
]

// Severity tiers drive badge color. Every status maps to exactly one tier:
//   critical -> red (destructive)   e.g. expired, denied, failed
//   warning  -> amber (warning)     e.g. expiring soon, needs review
//   good     -> green (success)     e.g. valid, approved, done
//   neutral  -> gray (secondary)    e.g. pending, queued, n/a
export type Severity = 'critical' | 'warning' | 'good' | 'neutral'

export const severityToBadgeVariant: Record<Severity, 'destructive' | 'warning' | 'success' | 'secondary'> = {
  critical: 'destructive',
  warning: 'warning',
  good: 'success',
  neutral: 'secondary',
}

// PRODUCT_CUSTOMIZE: replace this list with the real statuses this product
// produces (must match exactly what the backend poller writes to
// records.status). Every status must declare a severity tier above. Default
// values below are generic placeholders only — do not ship as-is.
// __STATUSES_BLOCK_START__
export const statuses: {
  label: string
  value: string
  icon: typeof TriangleAlert
  severity: Severity
}[] = [
  { label: 'Draft', value: 'draft:neutral', icon: Clock, severity: 'neutral' as Severity },
  { label: 'Active', value: 'active:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Expired', value: 'expired:neutral', icon: Clock, severity: 'neutral' as Severity },
  { label: 'Superseded', value: 'superseded:neutral', icon: Clock, severity: 'neutral' as Severity },
  { label: 'Archived', value: 'archived:neutral', icon: Clock, severity: 'neutral' as Severity },
  { label: 'Missing Plan', value: 'missing_plan:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Version Mismatch', value: 'version_mismatch:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Needs Review', value: 'needs_review:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Approved', value: 'approved:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Received', value: 'received:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Missing', value: 'missing:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Late', value: 'late:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Duplicate', value: 'duplicate:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Invalid Format', value: 'invalid_format:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Partially Ingested', value: 'partially_ingested:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Fully Ingested', value: 'fully_ingested:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Unmatched Payer', value: 'unmatched_payer:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Unmatched Payee', value: 'unmatched_payee:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Period Mismatch', value: 'period_mismatch:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Currency Mismatch', value: 'currency_mismatch:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Total Mismatch', value: 'total_mismatch:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Flagged', value: 'flagged:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Valid', value: 'valid:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Expected', value: 'expected:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Paid As Expected', value: 'paid_as_expected:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Overpaid', value: 'overpaid:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Short Paid', value: 'short_paid:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Underpaid', value: 'underpaid:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Missing Payment', value: 'missing_payment:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Missing Statement Line', value: 'missing_statement_line:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Unmatched Order', value: 'unmatched_order:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Unmatched Payout', value: 'unmatched_payout:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Timing Difference', value: 'timing_difference:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Unpaid', value: 'unpaid:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Past Due', value: 'past_due:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Partially Paid', value: 'partially_paid:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Duplicate Payment', value: 'duplicate_payment:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Duplicate Line', value: 'duplicate_line:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Unauthorized Deduction', value: 'unauthorized_deduction:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Unauthorized Chargeback', value: 'unauthorized_chargeback:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Unauthorized Fee', value: 'unauthorized_fee:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Unexpected Adjustment', value: 'unexpected_adjustment:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Incorrect Rate', value: 'incorrect_rate:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Incorrect Tier', value: 'incorrect_tier:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Incorrect Split', value: 'incorrect_split:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Incorrect Override', value: 'incorrect_override:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Net Terms Discrepancy', value: 'net_terms_discrepancy:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Tax Withholding Discrepancy', value: 'tax_withholding_discrepancy:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Currency Difference', value: 'currency_difference:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Data Mismatch', value: 'data_mismatch:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Disputed', value: 'disputed:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Resolved', value: 'resolved:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Recovered', value: 'recovered:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Partially Recovered', value: 'partially_recovered:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Not Recovered', value: 'not_recovered:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Written Off', value: 'written_off:neutral', icon: Clock, severity: 'neutral' as Severity },
  { label: 'Escalated', value: 'escalated:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Closed', value: 'closed:neutral', icon: Clock, severity: 'neutral' as Severity },
  { label: 'New', value: 'new:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Evidence Needed', value: 'evidence_needed:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Ready To Send', value: 'ready_to_send:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Sent', value: 'sent:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Acknowledged', value: 'acknowledged:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Under Review', value: 'under_review:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Rejected', value: 'rejected:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Partially Approved', value: 'partially_approved:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Aged 30', value: 'aged_30:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Aged 60', value: 'aged_60:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Aged 90 Plus', value: 'aged_90_plus:critical', icon: TriangleAlert, severity: 'critical' as Severity },
]
// __STATUSES_BLOCK_END__
