# 🌍 Kenya County Economic Tracker

County-level economic health tracker for all 47 Kenya counties — uses satellite nighttime light (VIIRS) following IMF machine-learning methodology to close the lag in sub-Saharan survey data.

## Research Basis
- **IMF Working Paper 2026/020** — "Nowcasting Economic Growth with Machine Learning and Satellite Data" (Fotopoulou et al., January 2026). Demonstrates random forest + nighttime satellite data outperforms traditional quarterly GDP models.
- **PLOS One 2025** — "Shedding light on development: Leveraging the new nightlights data to measure economic progress" — VIIRS + DMSP harmonized NTL data across 34 Sub-Saharan African countries, 2004-2019.
- **Henderson, Storeygard & Weil (NBER 2009)** — "Measuring Economic Growth from Outer Space" — established the NTL-GDP correlation at subnational levels.
- **KNBS Kenya County Data** — Kenya National Bureau of Statistics county-level indicators.

## Why This Matters
Kenya's statistical system updates county-level data annually at best. In SSA, the average interval between nationally representative surveys is **6.5 years**. Satellite data provides near-real-time economic proxies. This tool applies that methodology at the county level for the first time in a deployable Kenyan app.

## Current Status
DEMO with synthetic data representative of county-level patterns. Real implementation uses NASA Black Marble VIIRS data via Google Earth Engine.

---
*© 2026 Gabriel Mahia / AI Kung Fu LLC · MIT License*
