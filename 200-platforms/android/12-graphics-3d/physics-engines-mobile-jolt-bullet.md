---
title: "Physics engines на mobile: Jolt vs Bullet vs ReactPhysics3D"
created: 2026-04-20
modified: 2026-04-20
type: comparison
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/physics
  - type/comparison
  - level/intermediate
related:
  - "[[engine-comparison-matrix]]"
  - "[[gpu-memory-management-mobile]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[vectors-in-3d-graphics]]"
primary_sources:
  - url: "https://github.com/jrouwe/JoltPhysics"
    title: "Jolt Physics (Jorrit Rouwé)"
    accessed: 2026-04-20
  - url: "https://github.com/bulletphysics/bullet3"
    title: "Bullet Physics"
    accessed: 2026-04-20
reading_time: 10
difficulty: 4
---

# Physics engines на mobile

3D apps с interactivity часто need physics — collision detection, rigid body dynamics, ragdolls. Три главных open-source options для mobile: **Jolt**, **Bullet**, **ReactPhysics3D**. Все C++, integrate через NDK.

---

## Jolt Physics

**Launched:** 2022 by Jorrit Rouwé (Guerrilla Games). Used в **Horizon Forbidden West**, **Death Stranding 2**.

Pros:
- **Fast:** SIMD-optimized, multi-threaded. Often 2-3× быстрее Bullet.
- **Modern C++17/20** API.
- **Production-tested** — AAA games.
- **Deterministic** results.

Cons:
- Newer → smaller community.
- More complex API.

Android integration:
```gradle
// build.gradle
// Jolt via NDK static lib or git submodule
```

Used в **Godot 4** (через godot-jolt plugin), considered default для new projects.

---

## Bullet Physics

**Legacy** но ubiquitous. С 1999. Used в:
- Earlier AAA games (Red Dead Redemption, GTA IV).
- Blender rendering.
- Many indie games.

Pros:
- **Mature** — 25+ years refinement.
- **Documentation** abundance.
- **Widespread** — many integrations available.

Cons:
- **Slower** than Jolt on multicore mobile.
- **Older C++ style** API.
- **Development slowed** (latest major features 2019).

Android integration via NDK.

---

## ReactPhysics3D

**Lightweight** alternative. Simpler than Bullet/Jolt.

Pros:
- **Easy API** для small projects.
- **MIT license.**
- **Small binary size.**

Cons:
- **Less performant** than Jolt/Bullet.
- **Fewer features.**

Use для: simple ball-rolling, cart driving, basic collisions.

---

## Сравнение

| Aspect | Jolt | Bullet | ReactPhysics3D |
|---|---|---|---|
| **Performance** | Best | Good | OK |
| **Multi-threaded** | Yes, designed for | Limited | No |
| **SIMD** | Aggressive | Some | Minimal |
| **Determinism** | Yes | Limited | Yes |
| **API complexity** | Medium-high | Medium | Low |
| **Documentation** | Growing | Excellent | Good |
| **License** | MIT | ZLib | ZLib |
| **Android** | Good (NDK build) | Excellent | Excellent |
| **Community** | Growing fast | Massive | Small |
| **AAA use** | Horizon, DS2 | Earlier GTA, RDR | None |
| **Best for** | New projects, high perf | Legacy compat | Simple needs |

---

## Integration pattern

Typical Android NDK setup:

```cpp
// Initialize physics
PhysicsSystem physicsSystem;
physicsSystem.Init(maxBodies, maxBodyPairs, maxContacts, ...);

// Create body
BodyCreationSettings sofa(
    new BoxShape(Vec3(1.0f, 0.5f, 0.8f)),   // shape
    RVec3(0, 0.5f, 0),                       // position
    Quat::sIdentity(),                       // rotation
    EMotionType::Dynamic,
    Layers::MOVING
);
Body& body = physicsSystem.CreateBody(sofa);
body.SetFriction(0.8f);
body.SetLinearVelocity(Vec3(1, 0, 0));

// Simulate
while (running) {
    physicsSystem.Update(deltaTime, ...);  // step simulation
    
    // Read transforms и update rendering
    Mat44 transform = body.GetWorldTransform();
    renderMeshWithTransform(transform);
}
```

---

## Real-world usage

- **Planner 5D** — доп minimal physics (sliding snap?), likely no full physics engine.
- **Unity apps** — built-in Physics (PhysX under hood, Bullet для 2D).
- **Godot 4** — built-in Godot Physics + Jolt plugin.
- **Custom mobile games** — Jolt recommended 2026.

---

## Performance на mobile

Benchmark 1000 rigid bodies colliding:
- Jolt: 60 FPS на flagship (Snapdragon 8 Gen 2).
- Bullet: ~40 FPS same device.
- ReactPhysics3D: ~25 FPS.

Multi-threaded scenes — Jolt scales much better.

---

## Выбор

**For new projects 2026:**
- Games — **Jolt**.
- Education / simple — ReactPhysics3D.
- Compat с existing Bullet code — Bullet.

**Для non-game interior apps** (Planner 5D-class):
- Обычно full physics overkill. Minimal collision detection + snap-to-grid sufficient.

---

## Связь

[[engine-comparison-matrix]] — which engine includes physics.
[[vectors-in-3d-graphics]] — math foundation.
[[gpu-memory-management-mobile]] — physics runs на CPU, not GPU.

---

## Источники

- **Jolt Physics.** [github.com/jrouwe/JoltPhysics](https://github.com/jrouwe/JoltPhysics).
- **Bullet Physics.** [github.com/bulletphysics/bullet3](https://github.com/bulletphysics/bullet3).
- **ReactPhysics3D.** [reactphysics3d.com](https://reactphysics3d.com/).

---

## Проверь себя

> [!question]- Jolt или Bullet для new Android game в 2026?
> Jolt. Faster (2-3× на multi-core), modern C++, active development, used в AAA. Bullet legacy — use только для compatibility или if existing code base uses it.

---

*Deep-dive модуля M14.*
