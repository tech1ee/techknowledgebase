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
reading_time: 20
difficulty: 4
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
