---
title: "Case study: IKEA Place — AR furniture shopping"
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
  - "[[arcore-fundamentals]]"
  - "[[arcore-depth-api]]"
  - "[[ar-occlusion-rendering]]"
  - "[[ar-lighting-estimation]]"
  - "[[case-planner-5d]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[arcore-fundamentals]]"
primary_sources:
  - url: "https://www.magazinescience.com/en/technology/how-ikea-place-revolutionised-furniture-shopping-with-custom-mobile-app-development"
    title: "How IKEA Place revolutionised furniture shopping"
    accessed: 2026-04-20
  - url: "https://www.pocket-lint.com/phones/news/google/143961-ikea-s-augmented-reality-try-before-you-buy-app-comes-to-android-thanks-to-arcore"
    title: "IKEA Place ARCore integration"
    accessed: 2026-04-20
reading_time: 12
difficulty: 4
---

# Case study: IKEA Place

## Business context

IKEA — мировой лидер в flat-pack furniture. Target audience — homeowners decorating/furnishing. Key challenge: **return rate от online purchases** — особенно high для bulky furniture (sofa "не подходит в комнату", "cвет цвет отличается").

IKEA Place AR solves:
1. **Size uncertainty** — accurate 98% dimensional scaling.
2. **Colour matching** — lighting estimation showing real-look color.
3. **Aesthetic compatibility** — virtual sofa в actual room context.

ROI от IKEA's perspective:
- ~$10M investment в app development (estimated).
- 11× conversion lift measured.
- 20% return rate reduction для AR-assisted purchases.
- Substantial ROI positive.

## Timeline

- **2013 — Apple acquires PrimeSense** (ToF sensor tech). IKEA internally experiments.
- **2016 — iOS 11 announced с ARKit.**
- **2017 — IKEA Place launches** на iOS. Multi-month development.
- **2018 — Android version** with ARCore.
- **2019 — Depth API occlusion.** 2× conversion improvement.
- **2020 — Light estimation environmental HDR.**
- **2022 — renamed IKEA Kreativ** включающий room scanning.
- **2024 — AI-powered room design** suggestions.
- **2026 — continued growth.** 60M+ installs cumulative.

Development team: IKEA digital division + external consulting (Space10, Area 17). Not a huge team — focused experience.



**IKEA Place** — AR shopping app, launched 2017 (iOS) / 2018 (Android ARCore). Revolutionary: pre-purchase "try на space" furniture. Bench mark для AR shopping:
- **11× higher purchase intent** from users who used AR vs browsed 2D catalog (multiple studies).
- **2000 true-scale 3D models** of IKEA furniture.
- **98% dimensional accuracy** — virtual sofa is size of real sofa.

---

## Product

Flow:
1. Browse catalog.
2. Select item → "View in My Room".
3. Point camera — ARCore detects floor/walls.
4. Tap to place → furniture appears correctly sized.
5. Walk around, view from angles.
6. Buy → redirect to IKEA website.

---

## Technical stack (public info)

### Android
- Native app.
- **ARCore** для tracking, plane detection, depth.
- **Custom 3D renderer** (likely Filament-like, or own).
- True-scale 3D models — ensuring dimensional accuracy.

### iOS
- **ARKit** equivalent.
- Parallel dev team.

### Shared
- IKEA product catalog backend.
- 3D model pipeline (Blender-based optimization).

---

## Key technical decisions

### True-scale models

Furniture modeled exactly к real dimensions. User tests: "Does diван fit in room?" — accurate answer.

Asset pipeline:
- Artists model с exact IKEA dimensions.
- QA dimensional check vs real product.
- Optimize на LOD levels для mobile.

### ARCore Depth integration

Added 2019 Depth API → occlusion rendering. Sofa correctly hidden behind real table. **Before:** 5× conversion uplift. **After depth:** 11× uplift. Double improvement от one feature.

### Lighting estimation

ARCore Environmental HDR → diner behaves realistic в indoor light. Especially noticeable для glossy surfaces (chairs with metal legs reflect real scene).

### Catalog delivery

2000 models × complexity ~ several GB если packed in APK. Solution:
- **Base APK** — essentials (common items).
- **On-demand download** — other items fetched when selected.
- Play Asset Delivery (см. [[asset-loading-streaming]]).

Keeps install size reasonable (~30-50 MB base).

---

## Production optimizations

### LOD

Each furniture — 3 LODs. При AR view, objects typically 1-3 m → LOD 1 (medium) used.

### Draw call batching

Scene обычно 1-3 furniture + room. Low draw count, easy 60 FPS.

### Thermal mitigation

AR session drains battery и heats phone. After 30 min — throttling kicks в.

Mitigation:
- 30 FPS AR (camera feed 30 Hz anyway — 60 FPS virtual overkill).
- Disable plane detection after placement.
- Progressive quality reduction на thermal state.

Session stays sustainable ~1 hour.

### Tracking recovery

User moves camera too fast → tracking lost. UX:
- Freeze AR rendering.
- Show message "Hold steady, re-tracking..".
- Resume automatically.

Prevents jittery experience.

---

## Business metrics (public)

- **11× higher purchase intent** (users placing furniture in AR).
- **20% reduction** в returns (customers see fit before ordering).
- **Increased engagement** — 3× longer session time than 2D catalog.
- **ROI positive** — estimated investment $10M, returns substantially positive.

Makes AR a business case, not just feature.

---

## Lessons

1. **AR quality matters.** Depth API alone gave 2× conversion uplift. Worth performance cost.

2. **True-scale accuracy** — core value proposition. Compromise here = loss of trust.

3. **Not all furniture needs AR.** IKEA prioritized high-ticket items (sofas, beds, wardrobes) для AR experience.

4. **Catalog delivery critical.** Asset packs avoid inflated APK.

5. **Cross-platform shared pipeline** (iOS ARKit + Android ARCore). Single asset source → both platforms.

---

## Adapting для own AR app

Recipe for AR shopping MVP:
- **Android stack:** SceneView + ARCore + Filament underneath.
- **Models:** glTF 2.0 true-scale.
- **Catalog:** Play Asset Delivery.
- **Depth API + Lighting Estimation:** enable для quality.
- **Battery:** disable plane detection after placement, 30 FPS target.

~6-12 months для MVP с small team vs IKEA's multi-year dev.

---

## Связь

[[arcore-fundamentals]] — ARCore base.
[[arcore-depth-api]] — 11× conversion uplift source.
[[ar-occlusion-rendering]] — implementation.
[[ar-lighting-estimation]] — realistic shading.
[[case-planner-5d]] — interior design alternative (non-AR primary).
[[case-sweet-home-3d-android]] — open-source.
[[build-3d-home-planner-from-scratch]] — capstone.

---

## Источники

- **Magazine Science: IKEA Place analysis.** [magazinescience.com](https://www.magazinescience.com/en/technology/how-ikea-place-revolutionised-furniture-shopping-with-custom-mobile-app-development).
- **Pocket-lint: IKEA Place ARCore.** [pocket-lint.com](https://www.pocket-lint.com/phones/news/google/143961-ikea-s-augmented-reality-try-before-you-buy-app-comes-to-android-thanks-to-arcore).

---

*Case study модуля M15.*
