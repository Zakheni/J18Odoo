# Document Digitization — User Guide

**Module:** zakheni_document_digitize  
**Applies to:** Odoo 18  
**Role:** Accounts Payable Clerk / Invoicing User / Document Operator  

---

## 1. Overview

The Document Digitization module (`zakheni_document_digitize`) uses **OCR** (Optical Character Recognition) and **AI extraction** to automatically read incoming invoices, receipts, and similar documents. Extracted data (vendor, date, total, line items) is mapped onto a vendor bill or receipt draft, dramatically reducing manual data entry.

---

## 2. Prerequisites

- *Documents / Digitization* app installed.
- Inbox mail server configured if you use email-based ingestion.
- Scanner or multi-function printer capable of saving to a network folder or sending email.
- (Optional) AI / ML service endpoint configured in **Settings → Digitization → AI Provider**.

---

## 3. Key Concepts

| Term | Definition |
|---|---|
| **OCR** | Optical Character Recognition — converts image/PDF text into machine-readable text. |
| **AI Extraction** | Uses a trained model to identify fields (vendor, invoice date, total, tax, line items). |
| **Validation Workflow** | A multi-step process where the system proposes a draft; a human reviews, corrects, and confirms. |
| **Confidence Score** | A percentage indicating how likely the extracted value is correct (threshold configurable). |
| **Auto-Create** | When confidence exceeds the threshold, the system creates the invoice or receipt automatically. |

---

## 4. Step-by-Step Instructions

### 4.1 Upload a Document for Digitization

**Method A — Email:**

1. Send the invoice PDF (or image) as an attachment to the configured inbox email address.
2. Odoo picks up the email, attaches the file to the Documents app, and queues it for digitization.

**Method B — Manual Upload:**

1. Go to **Documents → Documents**.
2. Click **Upload** and select the invoice or receipt file.
3. The document appears in the list with status *Pending Digitization*.

**Method C — Scan / Drag & Drop into Chatter:**

- Drag a PDF directly onto an existing Vendor Bill or Purchase Order chatter; the system will offer to digitize it.

### 4.2 Review Extracted Data

1. Go to **Digitization → Pending Extractions**.
2. Click on a document to open the extraction preview.
3. Review the fields the AI extracted:

   | Field | Example |
   |---|---|
   | **Vendor** | ABC Supplies (Pty) Ltd |
   | **Invoice Date** | 2026-06-15 |
   | **Due Date** | 2026-07-15 |
   | **Reference Number** | INV-4421 |
   | **Total (excl. tax)** | 12 500.00 |
   | **Tax Amount** | 1 750.00 |
   | **Total (incl. tax)** | 14 250.00 |
   | **Line Items** | SKU, Description, Qty, Unit Price |

4. The **Confidence Score** next to each field tells you how reliable the extraction is.

### 4.3 Correct / Confirm Extracted Values

1. Click into any field to override the extracted value.
2. If a line item is missing, click **Add a Line** to enter it manually.
3. To map the document to an existing vendor, select the vendor from the dropdown.
4. Once all fields are correct, click **Validate**.
   - If confidence is above threshold → the system **auto-creates** the vendor bill / receipt.
   - If confidence is below threshold → the document moves to *Needs Review* for manual approval.

### 4.4 Validate the Created Document

1. Go to **Invoicing → Vendor Bills** (or **Receipts**).
2. Locate the newly created bill — it will have a link back to the original digitized document.
3. Review the Journal Items and Tax lines.
4. Click **Confirm** or Post as usual.

---

## 5. Common Tasks

| Task | Steps |
|---|---|
| **Upload a batch of invoices** | Documents → Upload (multi-select) → each queues individually |
| **Re-run extraction on a failed document** | Open document → Actions → Re-Digitize |
| **Export extracted data to CSV** | Digitization → Pending Extractions → select → Export |
| **Train the AI on a new vendor layout** | Open extraction → click *Send Feedback* → mark correct values → model improves |
| **Change confidence threshold** | Settings → Digitization → Confidence Threshold |

---

## 6. Tips & Best Practices

- **PDF vs. image**: PDFs (text-based) give higher confidence than scanned images or photos. Always prefer native PDF when available.
- **Quality of scan**: Set scanner to 300 DPI minimum. Crooked pages reduce OCR accuracy.
- **Vendor master data**: Keep your vendor records up to date — the AI uses vendor name matching to improve line-item parsing.
- **Multi-page documents**: The system treats all pages as one document; make sure the total appears on the last page or that the AI can sum sub-totals correctly.
- **Training**: Each time you correct a field and click *Send Feedback*, the model learns. After 20–30 corrections for the same vendor template, accuracy typically reaches >90%.

---

## 7. Troubleshooting

| Symptom | Likely Cause | Solution |
|---|---|---|
| Document stuck at *Pending* | AI service not reachable | Check Settings → Digitization → Provider status; test the endpoint URL |
| Wrong vendor selected | Vendor name in OCR differs from record name | Manually correct vendor; send feedback to train the model |
| Line items not extracted | Table formatting not recognised | Add line items manually; flag the document for AI training |
| Low confidence (< 50%) on all fields | Poor scan quality or handwritten text | Re-scan at 300+ DPI; if handwriting, manual entry is required |
| Auto-creation skipped | Confidence below threshold | Manually validate in Pending Extractions or lower the threshold |

---

*End of Document Digitization User Guide*
