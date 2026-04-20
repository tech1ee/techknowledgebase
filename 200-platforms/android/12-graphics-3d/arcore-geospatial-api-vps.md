---
title: "ARCore Geospatial API: глобальная локализация через VPS"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/ar
  - type/deep-dive
  - level/advanced
related:
  - "[[arcore-fundamentals]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[arcore-fundamentals]]"
primary_sources:
  - url: "https://developers.google.com/ar/develop/geospatial"
    title: "ARCore Geospatial API"
    accessed: 2026-04-20
reading_time: 10
difficulty: 4
---

# ARCore Geospatial API

**Geospatial API** — launched 2022, Google's breakthrough в global AR localization. Позволяет привязывать virtual content к конкретным координатам Земли (latitude + longitude + altitude + orientation). Precision 1-3 meters в areas covered Google Maps Street View.

Основа для city-scale AR experiences: AR navigation (walking directions поверх street), AR games (location-based content), AR tourism (history overlays на buildings).

---

## Visual Positioning System (VPS)

Under the hood — **VPS** (Visual Positioning System). Сравнивает camera view с Google's global Street View dataset. Computes precise location + orientation через computer vision.

Accuracy:
- **Standard localization:** GPS + compass, ~10-30 m.
- **VPS localization:** 1-3 m + accurate orientation.

VPS available в:
- North America, Europe, Japan, South Korea — most urban areas.
- Growing coverage globally.

---

## Enable

```kotlin
val config = Config(session).apply {
    geospatialMode = Config.GeospatialMode.ENABLED
}
session.configure(config)
```

Also required permissions: `ACCESS_FINE_LOCATION`, `CAMERA`.

---

## Earth object

```kotlin
val earth = session.earth
if (earth?.trackingState == TrackingState.TRACKING) {
    val cameraGeospatialPose = earth.cameraGeospatialPose
    val latitude = cameraGeospatialPose.latitude
    val longitude = cameraGeospatialPose.longitude
    val altitude = cameraGeospatialPose.altitude
    val heading = cameraGeospatialPose.heading  // degrees from true north
    
    // Accuracy estimates
    val horizontalAccuracy = cameraGeospatialPose.horizontalAccuracy
    val verticalAccuracy = cameraGeospatialPose.verticalAccuracy
    val headingAccuracy = cameraGeospatialPose.headingAccuracy
}
```

---

## Creating geospatial anchors

```kotlin
// Place content at specific lat/lng
val latitude = 37.7749
val longitude = -122.4194
val altitude = 100.0  // meters above WGS84 ellipsoid
val qx = 0.0; val qy = 0.0; val qz = 0.0; val qw = 1.0  // rotation

val anchor = earth.createAnchor(
    latitude, longitude, altitude,
    qx, qy, qz, qw
)
// anchor persists в world location
```

Content attached к this anchor appears в exact real location.

---

## Streetscape Geometry

VPS также provides **Streetscape Geometry** — 3D mesh of buildings и terrain в radius вокруг user:

```kotlin
val streetscapeGeometries = session.getAllTrackables(StreetscapeGeometry::class.java)
for (geom in streetscapeGeometries) {
    if (geom.trackingState != TrackingState.TRACKING) continue
    
    val mesh = geom.mesh  // 3D mesh данных
    val type = geom.type  // BUILDING, TERRAIN
    
    // Use для occlusion или collision
}
```

Virtual содержимое correctly occluded behind buildings. Critical for realistic city-scale AR.

---

## Use cases

### AR navigation

Places arrows/directions в real world fixed to streets. Google Maps AR use это.

### AR tourism

Historical buildings overlay с text, images, 3D reconstructions. Heritage sites.

### Location-based games

Pokemon Go-style games с precise positioning. Pokemon GO integrated Geospatial в 2022.

### Public art / events

Virtual art pieces at fixed locations. City exhibitions.

### Construction / surveying

Architects preview buildings на real plots.

---

## Limitations

- **VPS coverage required.** Rural areas без Street View → no precision.
- **Indoors:** VPS ineffective inside (relies on building exteriors visible).
- **Privacy:** Camera used для localization; needs user permission.
- **Network:** VPS typically online-only; offline unsupported.

---

## Related APIs

### Rooftop / Terrain anchors

```kotlin
earth.resolveAnchorOnRooftop(lat, lng, qx, qy, qz, qw, callback)
// Google estimates rooftop altitude, anchors to it
```

Good для content on building exteriors без knowing exact altitude.

---

## Real-world apps using Geospatial

- **Pokemon GO** — 2022 update adds VPS.
- **Google Maps AR walking directions.**
- **Niantic Lightship** — full platform сверху ARCore Geospatial.
- **Custom city AR apps** — tourism, gaming.

---

## Связь

[[arcore-fundamentals]] — ARCore context.
[[ar-occlusion-rendering]] — Streetscape Geometry used для occlusion.

---

## Источники

- **ARCore Geospatial API.** [developers.google.com/ar/develop/geospatial](https://developers.google.com/ar/develop/geospatial).

---

## Проверь себя

> [!question]- Чем VPS отличается от GPS?
> GPS — satellite triangulation, ±10-30 m accuracy, no orientation. VPS — visual matching с Street View dataset, ±1-3 m position + accurate orientation. VPS работает только в covered urban areas, indoors не работает.

---

*Deep-dive модуля M13.*
