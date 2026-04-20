---
title: "Vertex и fragment shaders на практике"
created: 2026-04-20
modified: 2026-04-20
type: tutorial
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/shaders
  - type/tutorial
  - level/intermediate
related:
  - "[[shader-programming-fundamentals]]"
  - "[[glsl-language-deep]]"
  - "[[lighting-models-lambert-phong-blinn]]"
  - "[[pbr-physically-based-rendering]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[glsl-language-deep]]"
reading_time: 18
difficulty: 4
---

# Vertex и fragment shaders на практике

Три практических примера от простого Lambert до PBR. Каждый полный (vertex + fragment) и запускается на Filament / Vulkan / OpenGL ES на Android.

---

## Example 1: flat-shaded triangle

Simplest case — отрисовать треугольник с constant color.

### Vertex shader

```glsl
#version 460
layout(location = 0) in vec3 position;

layout(push_constant) uniform Push {
    mat4 mvp;
} push;

void main() {
    gl_Position = push.mvp * vec4(position, 1.0);
}
```

### Fragment shader

```glsl
#version 460
layout(location = 0) out vec4 fragColor;

void main() {
    fragColor = vec4(1.0, 0.5, 0.2, 1.0);  // orange
}
```

Каждый fragment одного и того же цвета. Zero computation — rasterizer dominates.

---

## Example 2: Lambert diffuse shading

Добавляем normal и direction light — basic Lambert.

### Vertex shader

```glsl
#version 460
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;

layout(push_constant) uniform Push {
    mat4 mvp;
    mat4 model;
} push;

layout(location = 0) out mediump vec3 v_normal;

void main() {
    gl_Position = push.mvp * vec4(position, 1.0);
    
    // Transform normal to world space
    v_normal = mat3(push.model) * normal;
}
```

### Fragment shader

```glsl
#version 460
layout(location = 0) in mediump vec3 v_normal;

layout(set = 0, binding = 0) uniform Scene {
    vec3 lightDir;  // already in world space, unit
    vec3 lightColor;
    vec3 ambientColor;
    vec3 materialAlbedo;
} scene;

layout(location = 0) out vec4 fragColor;

void main() {
    vec3 N = normalize(v_normal);
    
    // Lambert: max(dot(N, L), 0)
    float NdotL = max(dot(N, -scene.lightDir), 0.0);
    
    vec3 diffuse = scene.materialAlbedo * scene.lightColor * NdotL;
    vec3 ambient = scene.materialAlbedo * scene.ambientColor;
    
    fragColor = vec4(diffuse + ambient, 1.0);
}
```

Комментарии:
- `v_normal` — `mediump` precision (половина cost, visually OK для normals).
- Перенормализуем в fragment shader (после interpolation).
- `-scene.lightDir` — свет «к» источнику, не «от».
- Ambient — simple constant чтобы dark sides не были полностью чёрными.

---

## Example 3: Simplified PBR (metallic-roughness)

Production-quality Filament-style PBR (упрощённая версия).

### Vertex shader

```glsl
#version 460
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;
layout(location = 2) in vec2 uv;

layout(push_constant) uniform Push {
    mat4 mvp;
    mat4 model;
    vec3 cameraPos;
} push;

layout(location = 0) out vec3 v_worldPos;
layout(location = 1) out mediump vec3 v_normal;
layout(location = 2) out mediump vec2 v_uv;
layout(location = 3) out vec3 v_viewDir;

void main() {
    vec4 worldPos4 = push.model * vec4(position, 1.0);
    v_worldPos = worldPos4.xyz;
    v_normal = mat3(push.model) * normal;
    v_uv = uv;
    v_viewDir = normalize(push.cameraPos - worldPos4.xyz);
    
    gl_Position = push.mvp * vec4(position, 1.0);
}
```

### Fragment shader

```glsl
#version 460
layout(location = 0) in vec3 v_worldPos;
layout(location = 1) in mediump vec3 v_normal;
layout(location = 2) in mediump vec2 v_uv;
layout(location = 3) in vec3 v_viewDir;

layout(set = 0, binding = 0) uniform sampler2D u_albedoMap;
layout(set = 0, binding = 1) uniform sampler2D u_metallicRoughnessMap;

layout(set = 0, binding = 2) uniform Scene {
    vec3 lightDir;
    vec3 lightColor;
    vec3 ambientColor;
} scene;

layout(location = 0) out vec4 fragColor;

const float PI = 3.14159265;

// Disney BRDF: simplified GGX + Schlick Fresnel
float distributionGGX(vec3 N, vec3 H, float roughness) {
    float a2 = roughness * roughness * roughness * roughness;
    float NdotH = max(dot(N, H), 0.0);
    float NdotH2 = NdotH * NdotH;
    float denom = NdotH2 * (a2 - 1.0) + 1.0;
    return a2 / (PI * denom * denom);
}

vec3 fresnelSchlick(float cosTheta, vec3 F0) {
    return F0 + (1.0 - F0) * pow(1.0 - cosTheta, 5.0);
}

float geometrySmith(float NdotV, float NdotL, float roughness) {
    float r = (roughness + 1.0);
    float k = (r * r) / 8.0;
    float ggx1 = NdotV / (NdotV * (1.0 - k) + k);
    float ggx2 = NdotL / (NdotL * (1.0 - k) + k);
    return ggx1 * ggx2;
}

void main() {
    // Sample material
    vec3 albedo = texture(u_albedoMap, v_uv).rgb;
    vec2 mr = texture(u_metallicRoughnessMap, v_uv).gb;
    float roughness = mr.x;
    float metallic = mr.y;
    
    vec3 N = normalize(v_normal);
    vec3 V = normalize(v_viewDir);
    vec3 L = normalize(-scene.lightDir);
    vec3 H = normalize(V + L);
    
    float NdotL = max(dot(N, L), 0.001);
    float NdotV = max(dot(N, V), 0.001);
    float HdotV = max(dot(H, V), 0.001);
    
    // F0: base reflectivity
    vec3 F0 = mix(vec3(0.04), albedo, metallic);
    
    // Cook-Torrance BRDF
    float NDF = distributionGGX(N, H, roughness);
    float G = geometrySmith(NdotV, NdotL, roughness);
    vec3 F = fresnelSchlick(HdotV, F0);
    
    vec3 specular = (NDF * G * F) / (4.0 * NdotV * NdotL);
    
    // Diffuse (only non-metallic surfaces have diffuse)
    vec3 kD = (1.0 - F) * (1.0 - metallic);
    vec3 diffuse = kD * albedo / PI;
    
    // Direct lighting
    vec3 direct = (diffuse + specular) * scene.lightColor * NdotL;
    
    // Ambient (simple)
    vec3 ambient = albedo * scene.ambientColor;
    
    fragColor = vec4(direct + ambient, 1.0);
}
```

Comments:
- Cook-Torrance BRDF — industry standard (см. [[pbr-physically-based-rendering]]).
- Schlick Fresnel approximation — fast, good enough для real-time.
- Smith geometry term — self-shadowing microfacets.
- Full PBR (с IBL, shadows, multi-light) — significantly bigger.

---

## Connecting on CPU side (Kotlin)

```kotlin
// Create pipeline with these shaders
val vertShaderModule = loadShader("shaders/pbr.vert.spv")
val fragShaderModule = loadShader("shaders/pbr.frag.spv")

val stages = arrayOf(
    VkPipelineShaderStageCreateInfo(vertShaderModule, "main", VK_SHADER_STAGE_VERTEX_BIT),
    VkPipelineShaderStageCreateInfo(fragShaderModule, "main", VK_SHADER_STAGE_FRAGMENT_BIT),
)

// ... pipeline layout with push_constant и descriptor set
// ... vkCreateGraphicsPipelines
```

---

## Performance notes

- Example 1: Simplest. ~60 FPS на любом GPU.
- Example 2: Lambert. ~60 FPS, minimal overhead vs Example 1.
- Example 3: PBR. ~60 FPS на flagship, лimited FPS на low-end.

Profiling-wise (AGI):
- Example 1: 100% vertex-bound or CPU-bound.
- Example 2: balanced.
- Example 3: fragment-bound (texture samples + math).

---

## Связь

[[shader-programming-fundamentals]] — model.
[[glsl-language-deep]] — syntax reference.
[[lighting-models-lambert-phong-blinn]] — Example 2 theory.
[[pbr-physically-based-rendering]] — Example 3 theory.

---

## Проверь себя

> [!question]- Зачем `mediump` для normals?
> 16-bit precision достаточна для normals (unit vectors). Экономит registers, ускоряет FMA. `highp` только для positions в world space.

---

## Куда дальше

| Направление | Куда |
|---|---|
| PBR theory | [[pbr-physically-based-rendering]] |
| Compilation | [[spir-v-and-compilation]] |
| Jitter mitigation | [[shader-compilation-jitter-mitigation]] |

---

*Tutorial модуля M5.*
