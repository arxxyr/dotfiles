---
name: a-share-trend-entry
description: Analyze A-share bottom stabilization and trend-entry conditions with risk-first, data-driven checklists. Use when the user asks whether A shares, a specific stock, Zhongtian Technology 600522, Shanghai Composite 4000, CPO/optical communications, or an empty-position account is ready for bottom-fishing, trend buying, staged entry, or confirmation after a pullback.
---

# A-Share Trend Entry

## Purpose

Use this skill to decide whether a market or stock is only rebounding, forming a bottom, or ready for trend-entry buying. Always separate:

- **Bottom stabilization**: selling pressure is weakening.
- **Trend entry**: after stabilization, capital is pushing price higher with continuity.

Risk comes first. Do not frame any level, including Shanghai Composite 4000, as an automatic buy signal.

## Required Data

Before concluding, fetch or cite:

- Current A-share index data: Shanghai Composite, Shenzhen Component, ChiNext, STAR 50.
- Target stock price, open/high/low/close, volume, turnover amount, key MAs.
- Target sector behavior: e.g. CPO, optical communications, telecom equipment, AI/technology, broad China assets.
- Recent 1-month theme activity: main-line sectors, rotation sectors, defensive sectors, and one-day pulse themes.
- Latest related news and catalysts: company announcements, industry policy, orders/earnings, overseas mapping, regulatory/negative news, and geopolitical or macro events. Record source and timestamp.
- External risk: VIX, Nasdaq, S&P 500, PHLX Semiconductor, Hang Seng/Hang Seng Tech when relevant.
- Account context: empty position, existing position, margin account, leverage, available margin if known.

If the market is closed, state that the data is from the latest trading session.

## Workflow

1. **Establish account state**
   - If user says they are empty-position, prioritize optionality, patience, staged entry, and avoiding premature full allocation.
   - If using margin/leverage, reduce position guidance and put margin safety before opportunity.
   - If memory or files conflict with the user's latest explicit statement, prefer the latest explicit statement for this analysis.

2. **Index stabilization check**
   - Bottom stabilization requires at least 3 of 4:
     - Stops making new lows or shows 2 consecutive higher intraday lows.
     - After a high-volume selloff, subsequent sessions stop falling on shrinking volume.
     - Recovers key level by close, not only intraday. For the 4000 case: recover 4000 first; 4050 is stronger repair.
     - Market breadth improves: advancers outnumber decliners or weakness stops spreading.

3. **Theme activity pre-filter**
   - First rank recent 1-month themes by funding activity and continuity.
   - Separate:
     - **Main line**: repeated high turnover, multiple relays, sector breadth, and industry logic.
     - **Rotation/low-position relay**: active after main-line crowding, but less durable.
     - **Defensive/geopolitical hedge**: active when indexes weaken or external risk rises.
     - **One-day pulse**: event-driven spike without continuity; do not use for trend-entry unless it repeats.
   - Prefer stocks inside the main line or a confirmed relay. Avoid applying trend-entry rules to isolated one-day themes.

4. **News catalyst and trend validation**
   - Classify latest news into:
     - **Hard catalyst**: official policy, company announcement, confirmed large order, earnings revision, production capacity, or regulatory approval.
     - **Soft catalyst**: media interpretation, brokerage theme framing, industry rumors, conference expectations, or overseas mapping without direct company impact.
     - **Risk news**: regulatory inquiry, shareholder reduction, order cancellation, margin/liquidity pressure, sanctions/export control, earnings miss, accident, or litigation.
     - **Noise**: repeated old news, vague market talk, or news that has no direct impact on the target or its sector.
   - News can only upgrade or downgrade confidence; it must not override price, volume, sector breadth, or index risk.
   - A bullish catalyst is valid only if price-volume confirms: target stock holds gains, sector leaders follow, turnover is healthy, and the move does not fade intraday.
   - A bearish or risk catalyst has higher weight when VIX rises, indexes weaken, or the stock loses key support with volume.
   - If news is strong but the target stock and sector fail to respond, treat it as "priced in" or weak recognition, not as a trend-entry signal.
   - For Zhongtian Technology specifically, distinguish direct catalysts in optical fiber/cable, submarine cable, telecom infrastructure, power grid/new energy support, and energy storage from indirect CPO/optical-module mapping.

5. **Sector confirmation**
   - Trend entry requires sector continuity, not a one-day bounce.
   - Prefer 2 consecutive sessions of acceptance: leaders hold gains, breadth improves, and turnover is healthy.
   - Reject high-open-low-close days, broad intraday fades, and single-day volume spikes followed by exhaustion.

6. **External risk filter**
   - VIX > 25: discount bullish signals; no aggressive tech growth trend-entry unless domestic data is very strong.
   - VIX 20-25: cautious risk environment; require stricter index and sector confirmation.
   - Nasdaq/SOX continuing sharp declines: discount A-share technology/CPO/optical communication entries.
   - VIX falling and US technology stabilizing: improves right-side entry quality.
   - Use US markets as a reference filter, not a direct trading signal for A shares.

7. **Target-stock trigger classification**
   - **Left-side trial**: price reaches support area, selling pressure shrinks, key support does not break. Size small.
   - **Trend entry**: price reclaims a trigger level and does not fall back the next day; sector and index confirm.
   - **Strong confirmation**: breakout above prior high with closing hold, healthy volume, and sector breadth.
   - **Invalidation**: reclaim attempt fails with volume or price loses key support for 1-2 closes.

8. **Position framework**
   - Trial entry: 20%-30% max for empty-position accounts.
   - Trend entry: 40%-50% only after index + sector + stock confirm.
   - Add-on: 60%-70% only after trend repair is confirmed and pullbacks hold.
   - Do not advise full allocation, blind bottom-fishing, or leverage increase on the first break of a level.

## Output Format

Use this concise structure:

```text
Risk first:
- ...

Current state:
- Bottom stabilization: yes/no/partial, because ...
- Trend entry: yes/no/partial, because ...

Trigger checklist:
- Index:
- Theme activity:
- News/catalyst:
- Sector:
- External risk:
- Target stock:

Execution:
- Trial:
- Trend entry:
- Add-on:
- Invalidation:

Conclusion:
...

Only for reference, not investment advice.
```

## Zhongtian 600522 Case

For the 2026-06-07 Zhongtian Technology / Shanghai Composite 4000 conversation, read [references/zhongtian-600522-20260607.md](references/zhongtian-600522-20260607.md). Treat it as a dated case study; refresh all prices, index levels, VIX, and sector data before reuse.

For the 2026-06-07 recent 1-month A-share and US theme-activity research, read [references/theme-activity-20260607.md](references/theme-activity-20260607.md). Treat it as a dated sector-map case study; refresh rankings and market data before reuse.

For the reusable news/catalyst filter, read [references/news-catalyst-filter.md](references/news-catalyst-filter.md). Use it whenever the user asks whether fresh news changes the trend judgment.

For the 2026-06-07 SPCX listing-window / A-H slow-bottoming scenario, read [references/spcx-slow-bottom-scenario-20260607.md](references/spcx-slow-bottom-scenario-20260607.md). Treat it as a dated macro scenario; refresh A/H/US indexes, VIX, and related news before reuse.
