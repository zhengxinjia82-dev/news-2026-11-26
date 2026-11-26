# Thursday 26 November 2026 — The World's News in One Day

[![make.fun](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/zhengxinjia82-dev/news-2026-11-26/rank.svg)](https://make.fun/bounty/news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/zhengxinjia82-dev/news-2026-11-26/reward.svg)](https://make.fun/bounty/news-image-20261126)

A one-page newspaper front page for the make.fun bounty **news-image-20261126**
($100, program/v1, deadline 2026-11-28T00:00Z). 1024×1024, ≤ 1 MiB, all drawings
hand-coded, no photos.

## What v2 covers

- **34 stories · 9 regions · 19 fields · all from this Thursday**
  - 3 big headlines, 10 illustrated features, 21 one-line briefs.
  - 9 pure-geography regions: E. Asia 6 · S. Asia 3 · SE Asia 2 · Middle East 1 ·
    Europe 11 · Africa 4 · N. America 5 · S. America 1 · Oceania 1.
  - 19 fields: nuclear, war, trade, economy, justice, technology, health,
    diplomacy, markets, sport, energy, business, politics, migration, labour,
    disaster, society, space, crime.
- Headlines: Kim orders wider tactical nuclear deployment (KCNA/Reuters);
  Russia hits two grain ships off Odesa (Reuters); Trump proposes tariffs on
  14 partners (Reuters).
- UTC timeline with 6 events spread 01:00–11:56 UTC; a 6-number day-in-numbers
  bar; a dot-matrix world map with 13 numbered pins (3 headlines + 10 features);
  every illustrated story carries a bold data banner.
- Every story carries a verification badge (CONFIRMED / OFFICIAL / REPORTED /
  CLAIM) and a source. HOW SURE legend uses exactly the 4 standard grades.

## DATE CHECK

Deliberately left out as older news: Cairo tanker fire kills 31 (Wed 25 Nov);
Macy's parade postponed (Wed 25 Nov); Houthis claim Ras Tanura hit (Wed 25 Nov);
FCC clears 1m SpaceX satellites (Wed 25 Nov); Chen Jining graft probe
(Tue 24 Nov); Poundland falls into administration (Wed 25 Nov).
Not yet: Spain votes Sun 29 Nov · Taiwan Sat 28 Nov.
Every story in the main text happened, or was first reported, on Thursday
26 November 2026; every DATE CHECK item was itself date-verified.

## How to run

```sh
python3 draw.py        # renders entry.png (1024x1024, deterministic)
MAKEFUN_OUTPUT_DIR=out node main.ts   # copies entry.png to out/entry.png
```

`draw.py` reads only `stories.json` and the DejaVu fonts; two runs produce
byte-identical PNGs. `main.ts` uses Node 22 stdlib only and verifies the PNG
magic bytes before copying.
