# Expansion Plan: Cultural & Deific Entities

This document outlines the systematic expansion of the label generation pipeline to cover a broader scope of Shinto and Buddhist cultural data on Wikidata.

## 1. Engishiki & Jinmyōchō (Q1342448, Q11064932)
- **Primary Targets**: The **Engishiki** item and all entities it links to.
- **Jinmyōchō**: The **Engishiki Jinmyōchō** item and all constituent parts linked via the `has part(s)` (P527) property.
- **Recursive Scope**: Deep labeling for items linked from these parts to ensure complete coverage of the Engishiki historical record.

## 2. Institutional Ranking Systems
- **Japanese Court Rank (P14005)**: All entities representing historical court ranks.
- **Modern Shrine Ranking (P13723)**: All specific entities within the modern shrine ranking hierarchy.

## 3. Japanese Deities
- **Shinto Kami**: All items identified as Japanese deities or mythological entities.
- **Buddhist Deities**: All Buddhist figures associated with Japanese religious practice.
- **Contextual References**: Comprehensive labeling for entities associated with specific shrines, such as **Tsukiyomi Shrine (Q11516217)**.

## 4. Methodology
- **Systematic Processing**: Apply existing phonological and script-based transliteration pipelines (Devanagari, Cyrillic, Perso-Arabic, Toki Pona, etc.) to regularized naming patterns.
- **Adaptive Labeling**: Utilize context-aware heuristics and manual verification for unique titles, complex ranks, and specific deity names that fall outside standard shrine/temple suffixes.
