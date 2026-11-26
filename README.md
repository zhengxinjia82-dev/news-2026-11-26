# News — Thursday 26 November 2026

[![make.fun](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/zhengxinjia82-dev/news-2026-11-26/rank.svg)](https://make.fun/bounty/news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/zhengxinjia82-dev/news-2026-11-26/reward.svg)](https://make.fun/bounty/news-image-20261126)

A one-page newspaper front page for Thursday 26 November 2026: **18 stories
from 5 regions and 11 fields**, all of which happened or were first reported
on that day. Filed early in the day — before Europe and the Americas woke —
so the timeline covers 00:00–06:00 UTC so far.

- 3 big headlines with code-drawn illustrations and stat banners (Kim's
  tactical-nuclear push, the Bank of Korea's rate lift to 3.25%, Taiwan and
  Vietnam answering Trump's tariff salvo)
- 10 illustrated secondary stories, each with a stat banner
- 5 one-line briefs
- UTC timeline, dot-matrix world map with 13 numbered pins, numbers bar, and
  a DATE CHECK box that leaves out older news (the Houthi Ras Tanura claim,
  the US tariffs on 14 partners, the FCC's SpaceX clearance, Ukraine's crypto
  law and the Chen Jining graft probe were all 24–25 Nov) and items not yet
  happened (Taiwan votes Sat 28 Nov; OPEC+ meets Sun 29 Nov; the Macy's
  parade is 9am ET).

Every story carries a verification badge (CONFIRMED = 2+ outlets, REPORTED =
one outlet, CLAIM = one side's word, OFFICIAL = on record) and its source.
All illustrations are original code-drawn art; no external images.

## How to run

```sh
python3 draw.py   # renders entry.png (1024x1024)
```

`main.ts` copies the drawn image to `/output/entry.png`:

```sh
MAKEFUN_OUTPUT_DIR=out node main.ts
```

`stories.json` holds the structured story data behind the page.
