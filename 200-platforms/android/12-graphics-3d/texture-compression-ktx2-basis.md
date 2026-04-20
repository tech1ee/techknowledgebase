---
title: "Texture compression: KTX2 и Basis Universal на Android"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/assets
  - type/deep-dive
  - level/intermediate
related:
  - "[[gltf-2-format-deep]]"
  - "[[gpu-memory-management-mobile]]"
  - "[[asset-loading-streaming]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[gltf-2-format-deep]]"
primary_sources:
  - url: "https://www.khronos.org/ktx/"
    title: "Khronos KTX 2.0 specification"
    accessed: 2026-04-20
  - url: "https://github.com/BinomialLLC/basis_universal"
    title: "Basis Universal encoder/transcoder"
    accessed: 2026-04-20
---

# Texture compression на mobile

Mobile apps с textures легко превышают 500 MB APK без compression. KTX2 + Basis Universal — современный стандарт 2026, reducing 5-10× от PNG with imperceptible quality loss, и transcoding на device в GPU-native format.

---

## Проблема

Raw 1024×1024 RGBA texture — 4 MB. Scene с 50 materials × 3 maps (albedo + normal + MR) = 600 MB. PNG сжимает до ~150 MB — still too much.

GPU native formats:
- **ETC1/ETC2** — open standard, supported all mobile GPUs. 4-bit (1 MB per 1024²).
- **ASTC** — modern standard, better quality. 4×4 to 12×12 blocks.
- **BC7** (Desktop) — similar to ASTC quality.

Каждый vendor/GPU supports different native formats. Нельзя ship one format для всех.

---

## Basis Universal

Binomial LLC разработали **Basis Universal** — compressed format, который **transcodes на device** в любой GPU-native format (ETC, ASTC, BC7) с minimal cost.

Benefits:
- One file for всех platforms.
- Small on disk (~80% saving vs PNG).
- Transcodes в GPU-native (zero runtime quality loss).
- Ubiquitous GPU support through target formats.

Two variants:
- **BasisLZ (ETC1S-based)** — highest compression, lower quality.
- **UASTC (UASTC-based)** — lower compression, higher quality.

---

## KTX 2.0

Khronos KTX 2.0 — container format для GPU textures. Can хранить:
- Uncompressed RGBA.
- Native GPU formats (ASTC, ETC2, BC7).
- Basis Universal супер-compressed.

KTX2 + Basis Universal — де-факто standard для glTF extension `KHR_texture_basisu`. glTF 2.0 + KTX2 → single-file solution для platform-independent textures.

---

## Toolchain

### Encode

```bash
basisu -uastc -output_file image.ktx2 input.png
# или
toktx --genmipmap --bcmp --assign_oetf srgb --t2 out.ktx2 input.png
```

### Integration в Android

**Filament** поддерживает KTX2 native через `gltfio` extension. Load glTF с `KHR_texture_basisu` → Filament decodes automatically.

**Custom Vulkan:**
```cpp
#include <ktx.h>

ktxTexture2* texture;
ktxTexture2_CreateFromNamedFile("tex.ktx2", KTX_TEXTURE_CREATE_LOAD_IMAGE_DATA_BIT, &texture);

// Transcode to GPU-native format
ktx_transcode_fmt_e target;
if (supports_astc) target = KTX_TTF_ASTC_4x4_RGBA;
else if (supports_etc2) target = KTX_TTF_ETC2_RGBA;

ktxTexture2_TranscodeBasis(texture, target, 0);

// Upload to VkImage
vkCmdCopyBufferToImage(...);
```

---

## Size savings real

1024×1024 texture:
- PNG: ~2 MB.
- KTX2 BasisLZ: ~200 KB (10×).
- KTX2 UASTC: ~800 KB (2.5× but better quality).
- ASTC 6×6: ~700 KB (native GPU, no transcoding).

Download size: KTX2 BasisLZ wins.
Runtime memory: ASTC = what's on GPU (1 MB); KTX2 transcodes → same 1 MB на GPU после transcode.

---

## When use what

**Standard textures (albedo, material maps):**
- KTX2 + UASTC (quality-critical).

**UI/HUD textures:**
- KTX2 + BasisLZ (smaller).

**Normal maps:**
- Requires high precision; UASTC recommended.

**HDR textures (environment maps):**
- KTX2 supports HDR через BC6H / ASTC HDR.

---

## Transcoding cost

~2-5 ms per megabyte на Android. Done once per texture, obviously async. For 100 MB textures → 200 ms total — acceptable during loading screen.

---

## Связь

[[gltf-2-format-deep]] — `KHR_texture_basisu` extension.
[[gpu-memory-management-mobile]] — how textures live в VRAM.
[[asset-loading-streaming]] — streaming pipeline.

---

## Источники

- **Khronos KTX 2.0.** [khronos.org/ktx](https://www.khronos.org/ktx/).
- **Basis Universal.** [github.com/BinomialLLC/basis_universal](https://github.com/BinomialLLC/basis_universal).

---

## Проверь себя

> [!question]- Зачем KTX2 если уже есть ETC2/ASTC?
> ETC2 и ASTC — vendor-specific: each GPU supports свой subset. Ship APK с всеми вариантами = 3× size. KTX2 + Basis = one file, transcoded to native GPU format on device. Universal.

---

## Куда дальше

| Направление | Куда |
|---|---|
| glTF integration | [[gltf-2-format-deep]] |
| Memory | [[gpu-memory-management-mobile]] |
| Loading | [[asset-loading-streaming]] |

---

*Deep-dive модуля M7.*
