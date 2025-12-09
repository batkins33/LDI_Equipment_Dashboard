# BA Sandbox

> **Status: Archived** — Apps migrated to TANGENT_FORGE (December 2025)

This repository was used for small experiments with document analysis and Google Workspace add-ons. Active development has moved to the TANGENT_FORGE monorepo.

---

## Migration History

The following projects were migrated on 2025-12-08:

| Original | Migrated To | Description |
|----------|-------------|-------------|
| `brand-color-harmonizer/` | `TANGENT_FORGE/products/brand-color-harmonizer/` | Google Slides add-on for brand color enforcement |
| `invoice-sorter/` | `TANGENT_FORGE/products/invoice-sorter/` | AP automation for invoice routing |
| `rubric-to-comment-ai/` | `TANGENT_FORGE/products/rubric-to-comment-ai/` | Google Docs add-on for AI grading feedback |
| `manifest_extraction_toolkit/` | `TANGENT_FORGE/products/sitesync/manifests/` | EPA manifest OCR extraction (construction) |
| `essaycoach-hybrid/` | (realized as `prompt-finder`) | Concept evolved into PathForge product |

---

## Historical Context

This repo originally contained:

- **Receipt Analyzer** — OCR pipeline for receipt processing (evolved into ReceiptIQ)
- **Lindamood Ticket Analyzer** — Construction ticket processing (evolved into SiteSync/TruckTickets)
- **WM Invoice Parser** — Early invoice extraction tests
- **Manifest PDF tools** — EPA manifest handling

These concepts have been productized and organized in TANGENT_FORGE under:
- `products/receiptiq/`
- `products/sitesync/`
- `products/invoice-sorter/`

---

## See Also

- [TANGENT_FORGE Repository](https://github.com/tangentforge/TANGENT_FORGE)
- [TANGENT_FORGE DEV_INDEX](../../../TANGENT_FORGE/canonical/DEV_INDEX.md)
