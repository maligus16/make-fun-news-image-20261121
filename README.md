# Saturday 21 November 2026 — The World in One Day

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/maligus16/make-fun-news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/maligus16/make-fun-news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

A one-page newspaper front page summing up Saturday 21 November 2026:
35 stories (3 leads + 10 drawn cards + 22 briefs), 7 regions, a world map
with numbered pins, a UTC timeline of the day, six big numbers and a
DATE CHECK box naming what was left out as other days' news.

## Files

- `entry.png` — the front page (1024×1024, rendered by `gen_image.py`)
- `main.ts` — the entrypoint: copies `entry.png` to `$MAKEFUN_OUTPUT_DIR`
  (default `/output`). No network, nothing deleted.
- `gen_image.py` — the renderer (Python 3 + Pillow, build time only).
  Every illustration is drawn in code; no photos, no copied artwork.
- `stories.json` — the 35 stories, the six big numbers, the UTC timeline
  and the DATE CHECK text. All counts (story total, region totals, brief
  numbers) are derived from this file at render time, so the masthead,
  the region bar and the numbered list always agree.

## Reproduce

```sh
python3 gen_image.py          # writes entry.png (byte-identical every run)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

## Sources

USGS · AFP · Reuters · AP · Kyiv Independent · ESA · ATP · FMC · UKMTO ·
market data. Every story was checked against reporting dated
21 November 2026; Friday-evening events are labelled Friday in the text,
and the DATE CHECK box lists the 18–20 November news that was left out.

<sub>Entered on [make.fun](https://make.fun/?ref=ftrr8fjx&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>
