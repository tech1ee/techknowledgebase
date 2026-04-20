---
title: "Case study: MagicPlan — AR-based floor plan measurement"
created: 2026-04-20
modified: 2026-04-20
type: case-study
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/case-study
  - topic/ar
  - type/case-study
  - level/intermediate
related:
  - "[[case-planner-5d]]"
  - "[[case-ikea-place-ar]]"
  - "[[arcore-fundamentals]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[arcore-fundamentals]]"
primary_sources:
  - url: "https://www.magicplan.app/"
    title: "MagicPlan official"
    accessed: 2026-04-20
reading_time: 8
difficulty: 3
---

# Case study: MagicPlan

## Business context

MagicPlan решает концeretную workflow problem в home services industry:
- **Real estate agents** must produce floor plans для listings. Before: hire drafter or manual measurement ($50-200 per plan).
- **Contractors** для estimating jobs need accurate dimensions. Before: tape measure, hours per room.
- **Insurance adjusters** documenting damage. Before: manual photos + measurements.
- **Renovators** planning kitchens, bathrooms. Before: detailed plans from architect.

MagicPlan cuts all этих workflow от hours к minutes, с comparable accuracy.

Pricing:
- Free trial: few plans.
- Subscription: $9.99/month или $99/year.
- Business plan: $39/month.
- Enterprise: custom pricing.

Revenue estimated $20-30M/year. Team ~50 people (Sensopia, based Montreal).

## Historical timeline

- **2011 — MagicPlan launch** на iPhone. Before ARCore — custom CV.
- **2011-2016 — custom computer vision era.** OpenCV-based, gyroscope-enhanced.
- **2013 — Android port.**
- **2017 — ARCore integration.** Migration from custom CV.
- **2020 — AI-powered wall detection** automating user taps.
- **2022 — Estimate + invoice feature** для contractors.
- **2024 — 3D room visualization** для renovation planning.
- **2026 — 50M+ installs cumulative.**



**MagicPlan** (Sensopia) — AR-based floor plan creation и measurement. User scans room с phone camera → automatic 2D floor plan generation + 3D model. Target: real estate, contractors, insurance adjusters. Launched 2011, Android port 2013.

Unique — **input через AR** (scan real room), not drawing.

---

## Product

Flow:
1. Point camera at corner of room.
2. Walk around room slowly.
3. MagicPlan detects walls, corners automatically.
4. Tap each corner to confirm.
5. Generates 2D plan + 3D model.
6. Measurements accurate ±1%.

Use cases:
- **Real estate:** listing plans.
- **Contractors:** estimate work scope.
- **Insurance:** damage documentation.

---

## Tech stack

### Stack
- **Android NDK (C++)** для performance-critical geometry + AR processing.
- **JNI** bridge to Kotlin/Java UI layer.
- **ARCore** для plane detection, depth (newer versions).
- **Custom computer vision** initially (pre-ARCore 2017).

### Platforms
- Android с 2013.
- iOS с 2011.
- Windows, macOS web-based.

---

## Technical challenges

### Accurate measurements

Target ±1% accuracy на 5-10 m rooms. Requires:
- Reliable camera calibration.
- Good feature tracking (SLAM / VIO).
- Room corner identification.
- User input validation.

Decade of iteration to get here.

### Pre-ARCore era

Before 2017 (ARCore launch), MagicPlan used **own computer vision**:
- OpenCV-based feature detection.
- Custom SLAM algorithm.
- Gyroscope-aware (phones в 2011 had less sensor accuracy).

Migration to ARCore simplified stack significantly.

### 2D ↔ 3D conversion

2D plan auto-generates 3D model:
- Walls extruded to ceiling height.
- Doors/windows from room-scan metadata.
- Furniture can be dropped in via catalog.

Cross-platform consistency — same code generates same plan на Android/iOS.

### NDK использование

CPU-intensive operations в C++:
- Geometry math (vertex ops).
- CV algorithms (historical).
- AR post-processing.

Kotlin/Java handles UI, user flow. NDK для crunching.

---

## Performance

- **APK size:** ~200-300 MB (с catalog, ML models).
- **Scan time:** 2-5 minutes per room.
- **Plan generation:** instant после scan.
- **Measurement accuracy:** ±1%.
- **Battery:** ~20% per hour intensive AR scanning.

---

## Business metrics

- **1M+ installs** (Play Store).
- **В использовании real estate pros** в US.
- **Commercial tier** — paid plans, catalog.

---

## Lessons

1. **NDK justified** when CV/CP work dominant. Не только games.

2. **ARCore migration** — huge simplification для apps who had own CV. Standardization benefits.

3. **Accuracy — core value** для measurement apps. Testable, ad-hoc tolerance unacceptable.

4. **Gyroscope-first** design compensates varying camera quality.

5. **Platform consistency** critical для cross-platform measurement accuracy.

---

## Comparison к other cases

| Aspect | Planner 5D | IKEA Place | Sweet Home 3D | MagicPlan |
|---|---|---|---|---|
| **Primary input** | Manual drag-drop | AR placement | Manual | AR scan |
| **Primary output** | Design | Buy intent | Plan file | Measured plan |
| **Tech stack** | NDK engine | ARCore + Filament | Java 3D | NDK + ARCore |
| **Focus** | Design creation | Shopping | Design + privacy | Measurement |

---

## Связь

[[case-planner-5d]], [[case-ikea-place-ar]], [[case-sweet-home-3d-android]] — alternatives.
[[arcore-fundamentals]] — modern AR base.
[[android-graphics-3d-moc]] — curriculum context.

---

## Источники

- **MagicPlan official.** [magicplan.app](https://www.magicplan.app/).

---

*Case study модуля M15.*
