---
title: "GLSL: язык шейдеров в глубине"
created: 2026-04-20
modified: 2026-04-20
type: reference
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/shaders
  - type/reference
  - level/intermediate
related:
  - "[[shader-programming-fundamentals]]"
  - "[[spir-v-and-compilation]]"
  - "[[vertex-and-fragment-shaders-by-example]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[shader-programming-fundamentals]]"
primary_sources:
  - url: "https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.html"
    title: "Khronos GLSL 4.60 Specification"
    accessed: 2026-04-20
  - url: "https://www.khronos.org/files/opengles_shading_language.pdf"
    title: "OpenGL ES Shading Language 3.20"
    accessed: 2026-04-20
reading_time: 28
difficulty: 4
---

## Полный обзор языка (deep expansion)

GLSL — C-подобный язык со specific adaptations для GPU programming.

### Базовые типы

**Scalar:** `bool`, `int`, `uint` (32-bit), `float` (32-bit), `double` (desktop только).

**Vector:** `vec2/3/4` (float), `ivec2/3/4` (int), `uvec2/3/4` (uint), `bvec2/3/4` (bool).

**Matrix:** `mat2/3/4` (квадратные), `mat2x3`, `mat3x4` и т.д. (non-square).

**Sampler:** `sampler2D`, `sampler3D`, `samplerCube`, `samplerCubeShadow`, `sampler2DArray`, `samplerBuffer`, `sampler2DMS` (multisampled).

**Image:** `image2D`, `image3D` — compute shader atomic access.

### Swizzling

```glsl
vec4 v = vec4(1.0, 2.0, 3.0, 4.0);
v.x       // 1.0
v.xyz     // vec3(1.0, 2.0, 3.0)
v.bgra    // reverse: vec4(3.0, 2.0, 1.0, 4.0)
v.xyxy    // repeated: vec4(1.0, 2.0, 1.0, 2.0)
v.xy = vec2(10.0, 20.0);  // lvalue swizzle assign
```

Equivalent aliases: `xyzw = rgba = stpq`. Comfortable для different contexts (geometry vs colours vs texture coords).

### Operators

- Element-wise arithmetic: `+`, `-`, `*`, `/`, `%` (int only).
- Vector multiplication `vec * vec` = element-wise! Для dot product — `dot(v1, v2)`.
- Matrix multiplication: `mat * vec` transform vector, `mat * mat` compose transforms. Column-major.
- Comparison returns bvec: `lessThan(v1, v2)`, `equal(v1, v2)`, `any(bv)`, `all(bv)`.

### Built-in functions (categorized)

**Trigonometry:** `sin, cos, tan, asin, acos, atan, atan2`.

**Exponential:** `pow, exp, log, exp2, log2, sqrt, inversesqrt`.

**Common math:** `abs, sign, floor, ceil, fract, mod, round, roundEven, trunc, min, max, clamp, mix, step, smoothstep`.

**Vector:** `length, distance, dot, cross, normalize, reflect, refract, faceforward`.

**Matrix:** `matrixCompMult, outerProduct, transpose, determinant, inverse`.

**Texture:** `texture(sampler, uv)`, `textureLod(sampler, uv, lod)`, `textureGrad`, `texelFetch` (no filtering), `textureSize`, `textureQueryLod`.

**Derivatives (fragment only):** `dFdx(v), dFdy(v)` — differences between adjacent fragments. `fwidth(v) = abs(dFdx) + abs(dFdy)`.

**Atomic (compute):** `atomicAdd, atomicMin, atomicMax, atomicAnd, atomicOr, atomicXor, atomicExchange, atomicCompSwap`.

### Storage qualifiers

- `in` — input (from previous stage или vertex attribute).
- `out` — output (to next stage или framebuffer).
- `uniform` — constant per-draw, same для всех invocations.
- `buffer` — Shader Storage Buffer Object (SSBO), read/write.
- `shared` — compute shader local shared memory (workgroup-scoped).
- `const` — compile-time constant.

### Precision qualifiers (mobile critical)

- `highp` — 32-bit float. Default в vertex stage.
- `mediump` — 16-bit half-float. Default в fragment.
- `lowp` — 10-bit fixed. Deprecated, treated as mediump.

Правильная precision choice halves register usage vs all-highp. Use `highp` только где нужно: world-space positions, normals с large magnitude.

### Layout qualifiers

```glsl
// Attributes и varying locations
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;
layout(location = 0) out vec4 fragColor;

// Descriptor set bindings (Vulkan)
layout(set = 0, binding = 0) uniform UBO { ... } ubo;
layout(set = 0, binding = 1) uniform sampler2D u_texture;

// Push constants
layout(push_constant) uniform Push { mat4 mvp; } push;

// UBO memory layout
layout(std140) uniform MyUBO { ... };  // padding rules
layout(std430) buffer MySSBO { ... };  // tighter

// Compute work group size
layout(local_size_x = 16, local_size_y = 16) in;
```

### Interface blocks

```glsl
// UBO
layout(binding = 0) uniform SceneData {
    mat4 view;
    mat4 projection;
    vec4 cameraPos;
} scene;

// SSBO
layout(binding = 1, std430) readonly buffer ParticleData {
    Particle particles[];
} particles;

// Varying block
out VertexOutput {
    vec3 normal;
    vec2 uv;
    vec3 worldPos;
} vsOut;
```

### Control flow

Standard C: `if-else`, `for`, `while`, `do-while`, `switch-case`, `break`, `continue`, `return`.

**GPU-specific:** `discard` (fragment only) — skip this fragment, no framebuffer write.

Divergent control flow penalizes warp execution — all threads execute все branches, предикатных off.

### Preprocessor

Standard C macros:
```glsl
#version 460 core
#pragma debug(on)
#define NUM_LIGHTS 4
#define PI 3.14159265

#ifdef VULKAN
  // Vulkan-specific code
#else
  // GL ES-specific code
#endif

#extension GL_KHR_ray_query : require
```

### Shader stages-specific built-ins

**Vertex shader:**
- Inputs: attribute `in` variables.
- Outputs: `gl_Position` (mandatory clip-space position), varyings.
- Built-in: `gl_VertexIndex`, `gl_InstanceIndex`.

**Fragment shader:**
- Inputs: interpolated varyings, `gl_FragCoord` (pixel position), `gl_PointCoord` (point sprites), `gl_FrontFacing` (front vs back).
- Outputs: `out` colour variables, optionally `gl_FragDepth`.
- Built-in: `discard`.

**Compute shader:**
- Inputs: `gl_GlobalInvocationID`, `gl_LocalInvocationID`, `gl_WorkGroupID`, `gl_WorkGroupSize`.
- Outputs: через image writes или SSBO writes.
- Shared memory access.

### Common patterns

**MVP transform:**
```glsl
gl_Position = projection * view * model * vec4(position, 1.0);
```

**Normal transform (correct for non-uniform scaling):**
```glsl
mat3 normalMatrix = transpose(inverse(mat3(model)));
v_normal = normalize(normalMatrix * normal);
```

**Basic Blinn-Phong:**
```glsl
vec3 N = normalize(v_normal);
vec3 L = normalize(-lightDir);
vec3 V = normalize(cameraPos - v_worldPos);
vec3 H = normalize(L + V);

float NdotL = max(dot(N, L), 0.0);
float NdotH = max(dot(N, H), 0.0);

vec3 diffuse = albedo * NdotL;
vec3 specular = vec3(0.3) * pow(NdotH, 32.0);
fragColor = vec4(diffuse + specular, 1.0);
```

**Reflection направление:**
```glsl
vec3 reflectionDir = reflect(-V, N);
vec3 envColor = texture(u_envMap, reflectionDir).rgb;
```

**Refraction (для glass):**
```glsl
vec3 refractionDir = refract(-V, N, 1.0 / 1.5);  // IOR glass = 1.5
vec3 refractColor = texture(u_envMap, refractionDir).rgb;
```

**Discarding alpha-test fragments:**
```glsl
vec4 color = texture(u_albedo, v_uv);
if (color.a < 0.5) discard;
```

**Screen-space derivatives для normal mapping без tangent:**
```glsl
vec3 dp1 = dFdx(worldPos);
vec3 dp2 = dFdy(worldPos);
vec2 duv1 = dFdx(v_uv);
vec2 duv2 = dFdy(v_uv);

vec3 dp2perp = cross(dp2, N);
vec3 dp1perp = cross(N, dp1);
vec3 T = dp2perp * duv1.x + dp1perp * duv2.x;
vec3 B = dp2perp * duv1.y + dp1perp * duv2.y;

float invmax = inversesqrt(max(dot(T, T), dot(B, B)));
mat3 TBN = mat3(T * invmax, B * invmax, N);
```

### Common mistakes

- **Missing `#version`:** compilation fails.
- **Wrong precision для highp требующих values:** mediump world-space position overflows at large coordinates (>65k).
- **Dividing by zero:** NaN propagation, silent bug.
- **Unnormalized uniforms:** light direction должен быть normalized перед use.
- **Writing gl_FragDepth:** disables early-Z, major performance hit.
- **Using `discard` без need:** disables early-Z.
- **Dynamic indexing вne-uniform:** может cause lowered performance.
- **Deep control flow:** register pressure increases.

### GLSL versioning

- **GLSL ES 1.00** (OpenGL ES 2.0) — basic, no interface blocks.
- **GLSL ES 3.00** (ES 3.0) — interface blocks, attribute arrays.
- **GLSL ES 3.10** (ES 3.1) — compute shaders, SSBOs.
- **GLSL ES 3.20** (ES 3.2) — geometry, tessellation shaders.
- **GLSL 4.60** (Vulkan) — full desktop features for Vulkan.

На Android practical: ES 3.20 для GL, 4.60 для Vulkan.

---

# GLSL: язык шейдеров в глубине

Reference на основные конструкции GLSL (и GLSL ES). Actionable синтаксис и сematika.

---

## Типы

### Skalar types

| Type | Description |
|---|---|
| `bool` | Boolean |
| `int` | 32-bit signed integer |
| `uint` | 32-bit unsigned (GLSL 3.0+) |
| `float` | 32-bit IEEE float |
| `double` | 64-bit (desktop only, не mobile) |

### Vector types

```glsl
vec2 v2;  // 2 floats
vec3 v3;  // 3 floats
vec4 v4;  // 4 floats
ivec3 iv; // integer vectors
uvec2 uv; // unsigned integer
bvec4 bv; // boolean
```

### Matrix types

```glsl
mat2 m2;  // 2x2
mat3 m3;  // 3x3
mat4 m4;  // 4x4
mat3x4 m; // non-square (rare)
```

Column-major layout по default (см. [[matrices-for-transformations]]).

### Texture samplers

```glsl
uniform sampler2D u_diffuse;      // 2D texture
uniform sampler2DArray u_array;    // texture array
uniform samplerCube u_cubemap;     // cubemap (for IBL / reflections)
uniform sampler3D u_volume;        // 3D texture
uniform sampler2DShadow u_shadow; // depth comparison
```

---

## Qualifiers

### Storage qualifiers

- **`in`** — input to stage (from previous pipeline stage or vertex attributes).
- **`out`** — output of stage.
- **`uniform`** — constant across all invocations within one draw.
- **`buffer`** — SSBO (Shader Storage Buffer Object) — large R/W storage.

### Precision qualifiers (mobile)

- **`highp`** — 32-bit float.
- **`mediump`** — 16-bit float.
- **`lowp`** — 10-bit fixed (legacy).

Always declare precision on mobile; default может сильно отличаться между драйверами.

### Memory qualifiers

- **`readonly`** — read-only access to buffer/image.
- **`writeonly`** — write-only.
- **`coherent`** — synchronized across shader invocations.
- **`volatile`** — atomic access.

---

## Swizzling

Access vector components arbitrary order:

```glsl
vec4 c = vec4(1.0, 2.0, 3.0, 4.0);
vec3 rgb = c.rgb;    // (1, 2, 3) — same as c.xyz
vec3 bgr = c.bgr;    // (3, 2, 1) — reversed
vec2 xx = c.xx;      // (1, 1) — repeated
vec4 wrdy = c.wxyz;  // (4, 1, 2, 3)
```

Aliases: `xyzw`, `rgba`, `stpq` — эквивалентны, different semantic hints.

---

## Built-in functions

### Math

```glsl
sqrt(x)       // √x
pow(x, y)     // x^y
exp(x)        // e^x
log(x)        // ln(x)
abs(x)        // |x|
mod(x, y)     // x - y*floor(x/y)
clamp(x, min, max)
mix(x, y, t)  // lerp: x*(1-t) + y*t
smoothstep(edge0, edge1, x)  // smooth 0→1 transition
step(edge, x) // 0 if x<edge else 1
```

### Geometric

```glsl
length(v)     // |v|
distance(a, b) // |a - b|
dot(a, b)     // scalar product
cross(a, b)   // vector product (3D)
normalize(v)  // v / |v|
reflect(I, N) // I - 2 dot(I,N) N
refract(I, N, eta)
faceforward(N, I, Nref)  // flip N if looking away
```

### Matrix

```glsl
transpose(m)
inverse(m)
determinant(m)
// операторы: * (matrix*matrix, matrix*vec), +, -
```

### Texture

```glsl
texture(sampler, uv)                // 2D sample
texture(sampler, uv, bias)
textureLod(sampler, uv, lod)        // explicit LOD
textureGrad(sampler, uv, dx, dy)    // specified derivatives
textureGather(sampler, uv)          // 2x2 neighborhood
```

### Atomic (compute shaders)

```glsl
atomicAdd(counter, 1);
atomicMin(val, x);
atomicCompSwap(val, expected, desired);
```

### Derivatives (fragment only)

```glsl
dFdx(x)  // derivative в x-direction
dFdy(x)
fwidth(x) // abs(dFdx) + abs(dFdy)
```

---

## Control flow

Standard: `if/else`, `for`, `while`, `break`, `continue`, `return`, `discard`.

**Warning:** branching может вызывать warp divergence — penalty. Preference branchless (см. [[gpu-architecture-fundamentals#Divergence penalty]]):

```glsl
// Bad: divergent
if (condition) {
    color = vec3(1,0,0);
} else {
    color = vec3(0,1,0);
}

// Better: branchless
color = mix(vec3(0,1,0), vec3(1,0,0), float(condition));
```

---

## Built-in variables

### Vertex shader

```glsl
in int gl_VertexID;        // current vertex index
in int gl_InstanceID;       // for instanced rendering
out vec4 gl_Position;       // clip space position (MANDATORY output)
```

### Fragment shader

```glsl
in vec4 gl_FragCoord;       // (pixel_x, pixel_y, depth, 1/w)
in bool gl_FrontFacing;     // is fragment on front-facing triangle
out vec4 fragColor;         // define your own output
out float gl_FragDepth;     // modify depth (disables early-Z)
discard;                    // drop this fragment (disables early-Z)
```

---

## Compute shader

```glsl
layout(local_size_x = 16, local_size_y = 16) in;

void main() {
    uvec3 id = gl_GlobalInvocationID;
    // process pixel at (id.x, id.y)
}
```

Parameters:
- `gl_WorkGroupSize` — local workgroup dimensions.
- `gl_NumWorkGroups` — number of workgroups.
- `gl_WorkGroupID` — current workgroup.
- `gl_LocalInvocationID` — within workgroup.
- `gl_GlobalInvocationID` — absolute.

---

## Layout qualifiers

### Location (for varyings, uniforms)

```glsl
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;
layout(location = 0) out vec3 v_normal;
```

### Binding (for resources)

```glsl
layout(binding = 0) uniform UBO { ... };
layout(set = 0, binding = 1) uniform sampler2D tex;
```

### Std140 / std430

Для buffer layouts — packing rules:

```glsl
layout(std140, binding = 0) uniform UBO {
    mat4 model;    // 64 bytes
    vec3 lightPos; // 12 bytes, padded до 16
    float time;    // 4 bytes
};
```

std140 — more forgiving (fits all UBO usage), std430 — tighter (SSBO only).

---

## Particle advice

- **Mediump** precision whenever possible (mobile).
- **Minimize uniform count** — они тратят registers.
- **Use built-in functions** — hardware-accelerated.
- **Avoid `discard`** unless necessary (kills early-Z).
- **Simplify control flow** — prefer branchless.

---

## Связь

[[shader-programming-fundamentals]] — overview of stages.
[[spir-v-and-compilation]] — как GLSL становится GPU code.
[[vertex-and-fragment-shaders-by-example]] — applied.
[[agsl-runtime-shader-compose]] — AGSL — subset GLSL для Compose.

---

## Источники

- **Khronos GLSL 4.60 Spec.** [registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.html](https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.html).
- **OpenGL ES Shading Language 3.20 Spec.** [khronos.org/files/opengles_shading_language.pdf](https://www.khronos.org/files/opengles_shading_language.pdf).
- **Rost, R. (2009). OpenGL Shading Language.**

---

## Проверь себя

> [!question]- Почему на mobile preferred mediump?
> Mediump (16-bit) использует половину registers per variable vs highp (32-bit). Lower register pressure → больше warps помещается → better occupancy → higher performance. Для цветов, UV, local math — precision достаточна.

> [!question]- Почему avoid `discard`?
> Discard кills early-Z — hardware не может test depth перед fragment shader, если shader может discard. Fragment shader runs even для occluded pixels. Может удваивать cost.

---

## Ключевые карточки

Что такое swizzling?
?
Access vector components в произвольном порядке: `v.xyz`, `v.rgb`, `v.wzyx`. Синтаксический сахар. Aliases `xyzw`, `rgba`, `stpq`.

---

Что такое uniform?
?
Global variable в shader, constant across all invocations within draw. Set from CPU through descriptor sets / uniform buffer objects. Used для matrix, textures, lights.

---

## Куда дальше

| Направление | Куда |
|---|---|
| Примеры практики | [[vertex-and-fragment-shaders-by-example]] |
| Компиляция | [[spir-v-and-compilation]] |
| Android AGSL | [[agsl-runtime-shader-compose]] |

---

*Reference модуля M5.*
