"""Enrichment layer: validate and enrich targets against public registries.

Currently the CMS NPPES **NPI Registry** — a free, public, no-auth API. This
turns a raw AcuityMD export into a *validated* target list: bad NPIs caught,
specialties confirmed, practice addresses and phone numbers filled in.
"""
