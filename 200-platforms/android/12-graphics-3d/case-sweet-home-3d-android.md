---
title: "Case study: Sweet Home 3D — open-source interior design"
created: 2026-04-20
modified: 2026-04-20
type: case-study
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/case-study
  - type/case-study
  - level/intermediate
related:
  - "[[case-planner-5d]]"
  - "[[case-ikea-place-ar]]"
  - "[[engine-comparison-matrix]]"
  - "[[build-3d-home-planner-from-scratch]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[android-graphics-3d-moc]]"
primary_sources:
  - url: "https://www.sweethome3d.com/"
    title: "Sweet Home 3D official"
    accessed: 2026-04-20
  - url: "https://github.com/ralic/sweethome-3d"
    title: "Sweet Home 3D GitHub mirror"
    accessed: 2026-04-20
reading_time: 10
difficulty: 3
---

# Case study: Sweet Home 3D

## История проекта

Sweet Home 3D — французская альтернатива Planner 5D, с противоположной философией (open-source, offline-first):

- **2006 — Emmanuel Puybaret** начинает проект в Eteks company.
- **2006 — v1.0** — Java-based, desktop only. GPL license.
- **2010 — 1M downloads** от SourceForge.
- **2012 — community contributors** добавляют features.
- **2014 — Android port** published. Limited subset of desktop features.
- **2017 — 10M+ downloads cumulative.**
- **2019 — Yafaray rendering** replaces Sunflow для photorealism.
- **2021 — glTF 2.0 import/export.**
- **2023 — 20M+ downloads, 40+ languages.**
- **2026 — still active development.** Monthly releases.

Financial sustainability:
- Free под GPL.
- Donations via PayPal.
- Paid iOS version ($5-10) subsidizes development.
- Enterprise custom development.

Developer count: ~1-2 core + community contributors. Prove что small team может sustain significant open-source project long-term.



**Sweet Home 3D** — open-source interior design software. Desktop с 2006 (Eteks), Android port позже. Alternative architecture: Java-based, offline-first, open-source. Contrast к Planner 5D's cloud-heavy model.

---

## Product

- **2D floor plan editor.** Draw walls, rooms, doors, windows.
- **3D view.** Navigate as first-person.
- **Furniture catalog** — 1000+ included objects.
- **Import standard formats** (OBJ, 3DS, Collada, glTF 2.0 recent).
- **Photorealistic rendering** — via external Sunflow (2006-era, slow) or Yafaray (newer, ~2× faster).
- **Multi-language** (40+ languages).
- **FREE** — GPL license.

Android port — simplified, but core functionality preserved.

---

## Tech stack

### Core engine

- **Java** основной язык.
- **Java 3D** (Sun Microsystems, then Oracle) primary 3D library. Desktop.
- **OpenGL ES** on Android.

### Android port

- Java code reused extensively.
- OpenGL ES 2.0/3.0 rendering.
- Same file format как desktop — interop.

---

## Architectural choice: offline-first

Unlike Planner 5D (cloud-heavy), Sweet Home 3D — **entirely local**:
- Scene files stored on device.
- No cloud sync.
- No account needed.
- Renderer runs на device.

Pros:
- **Privacy** — nothing leaves device.
- **No internet dependency.**
- **Free.**

Cons:
- **No sync across devices.**
- **Rendering slow** on mobile (CPU-based Sunflow/Yafaray).
- **Limited collaboration.**

Different target audience (privacy/budget-conscious users vs feature-rich mainstream).

---

## Technical problems

### Problem 1: Large scene performance

Complex houses с 20+ light sources — bogs down. 3D view barely 15 FPS on old phones.

Mitigation: simplified shader set (no PBR, basic Blinn-Phong). LOD manual.

### Problem 2: Photorealistic render

Sunflow: ray tracer, minutes per image на mobile CPU. Slow but functional.

Yafaray: faster, but still minutes. Real-time impossible.

На modern mobile — maybe 30 sec per 1080p image.

### Problem 3: File format interop

Sweet Home 3D `.sh3d` format — proprietary but documented. Can import OBJ, 3DS, newer formats via plugins.

glTF 2.0 support added ~2021 — matches industry standard.

---

## APK metrics

- **Size:** ~50-70 MB (includes furniture catalog).
- **Rendering:** CPU-based, slow.
- **Battery:** 10-15% per hour (light use).

---

## Lessons

1. **Offline-first is valid architecture.** Privacy, no-internet benefits real users.

2. **Open-source longevity** — Sweet Home 3D с 2006, still active. Viable alternative to SaaS.

3. **Limited performance** на mobile — trade-off для cross-platform codebase. Java 3D не tailored mobile TBR.

4. **Import standardization** — glTF 2.0 late but essential для interop.

5. **CPU-based photorealistic** possible, just slow. Ray tracing on mobile is experimental.

---

## Comparison

| Aspect | Planner 5D | IKEA Place | Sweet Home 3D |
|---|---|---|---|
| **License** | Proprietary | Proprietary | GPL (open) |
| **Business model** | Freemium | Free (drives sales) | Free + donations |
| **Cloud** | Heavy | Light | None |
| **Platform** | Android/iOS/Web | Android/iOS | Android/Desktop |
| **Offline** | Partial | No (AR needs camera) | Full |
| **3D engine** | Custom C++/NDK | Custom + ARCore | Java 3D + OpenGL |
| **Rendering** | Real-time + cloud photorealistic | Real-time AR | Real-time + CPU photorealistic |
| **Target user** | Mainstream consumers | IKEA shoppers | Privacy/free-conscious |

---

## Adapting ideas

Для новой offline-first app:
- **Don't use Java 3D** — deprecated. Use [[filament-architecture-deep|Filament]] или [[godot-4-on-android-renderer|Godot]].
- **Keep offline-first principle** if privacy important.
- **Consider open-sourcing** для community contributions.
- **Support standard formats** (glTF 2.0) из start.

---

## Связь

[[case-planner-5d]] — cloud-heavy alternative.
[[case-ikea-place-ar]] — AR-focused alternative.
[[engine-comparison-matrix]] — why NOT Java 3D in 2026.
[[build-3d-home-planner-from-scratch]] — capstone drawing on все cases.

---

## Источники

- **Sweet Home 3D official.** [sweethome3d.com](https://www.sweethome3d.com/).
- **GitHub mirror.** [github.com/ralic/sweethome-3d](https://github.com/ralic/sweethome-3d).

---

*Case study модуля M15.*
