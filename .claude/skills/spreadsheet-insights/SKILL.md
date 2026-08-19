---
name: spreadsheet-insights
description: Analyze spreadsheet or table data the user pastes in and explain what it shows — the headline, the trend, outliers, key totals and averages, data-quality issues, and what to look at next. Use this when the user pastes rows, a CSV, or a table, or says analyze this spreadsheet, what does this data say, summarize these numbers, or find the trends in this data.
---

# Spreadsheet Insights

When this skill runs, turn the user's pasted spreadsheet data into a plain-language read on what it actually says.

## Process

1. Work out what each column is and what the rows represent. If a column is ambiguous, say so rather than assume.
2. Lead with ONE headline sentence: the single most important thing this data shows.
3. Describe the trend — what is going up, down, or flat over time (only if the data has a time dimension).
4. Flag outliers and anomalies: the biggest movers, anything unusual, and any concentration (one row or category dominating the total).
5. Report the key numbers — totals, averages, min/max — calculated ONLY from the rows provided. Name the columns each number came from.
6. Note data-quality problems: blank cells, inconsistent units or formats, duplicates, or too few rows to be reliable.
7. End with "What to look at next" and "What I couldn't tell from this data."

## Rules

- Use ONLY the data the user pastes in. Never invent, estimate, or fill in a missing value, and never fabricate a number the rows do not support.
- You cannot connect to a live Google Sheet, Excel file, database, or the web. Never imply you can — you only see what was pasted.
- Show your arithmetic for any non-trivial calculation, and tell the user to verify exact figures against their own sheet. You reason over data; you are not a calculator of record.
- If the data is too small, too messy, or missing a column needed to answer, say so plainly instead of forcing an answer.
- Correlation is not cause. Note what moves together; do not claim one caused another unless the user's context says so.
- Do not make the business decision. Surface what the data says and the questions it raises.

## Output format

### Headline
One sentence: the most important thing in this data.

### The Trend
Up, down, or flat over time, with the numbers.

### Outliers & Anomalies
Biggest movers, unusual points, concentration.

### Key Numbers
Totals, averages, min/max — with the columns they came from.

### Data Quality Notes
Blanks, inconsistent formats, duplicates, small samples.

### What To Look At Next
2-4 specific questions this data raises.

### What I Couldn't Tell From This Data
What's missing to answer it, and which column would fix that.

If the user has not pasted any data, ask for it (with the header row) before analyzing anything.
