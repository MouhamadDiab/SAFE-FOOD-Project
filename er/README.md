# Entity resolution status

The *original synthetic coursework sample* contained fabricated same-barcode OFF-USDA pairs. To avoid presenting these as real matches, this **real-data** project deliberately has zero USDA rows, so no independent OFF-USDA matching evaluation can be claimed. The R2RML mapping and Python materializer both preserve a placeholder link path for future real exact-barcode matches, but no precision/recall figure is reported.

A legitimate extension would download a small, licence-documented USDA FoodData Central Branded Foods sample, carry product identifiers and retrieval dates, construct gold matched/nonmatched pairs manually, then evaluate P/R. This work has not been performed in the supplied snapshot.
