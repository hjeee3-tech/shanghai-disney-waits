# Shanghai Disneyland wait times logger

Personal project: records Shanghai Disneyland attraction wait times every 5 minutes
(08:00–22:30 KST) to build a time-of-day queue guide for a trip on 2026-10-09.

- `collect.py` — fetches wait times and appends to `data/YYYY-MM-DD.csv` (times in China Standard Time)
- `.github/workflows/collect.yml` — runs the collector on a schedule until 2026-10-17

Data source: [Powered by Queue-Times.com](https://queue-times.com/)
