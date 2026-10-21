---
id: 1
title: "GSAP x/y tweened on the same SVG node as an svgOrigin scale/rotation shifts its resting position, so precomputed camera zoom targets miss"
status: open
type: open-source
skill: [hyperframes-animation, hyperframes-keyframes]
proposes_skill: []
target_file: []
siblings_checked: "no family registry; hyperframes family — hyperframes-animation added (adapters/gsap-transforms-and-perf.md is the GSAP transform home), hyperframes-keyframes added (owns seek-safe GSAP camera/punch-in keyframes), hyperframes-core excluded (core SKILL.md 'Agent pitfalls' covers CSS-vs-GSAP transform conflicts only, not SVG svgOrigin composition)"
area: "GSAP adapter — SVG transforms; viewport-change / coordinate-target-zoom camera recipes"
date: 2026-10-21
session_context: "Building three 40s hand-drawn Bible motion graphics in HyperFrames (woman-at-the-well, david-and-goliath) with deep zoom-through transitions into an object (water jar mouth, a stone) whose screen position was computed from its static SVG transform"
parked_until:
resolved:
resolution:
reference:
commands_verified: none
---

**Issue:** Twice in one session an opening zoom-through landed ~45-60px off its
target (the screen filled with the wrong colour). Both times the target `<g>` had
an entrance tween mixing `y` (or `x`) with `scale`/`rotation` plus `svgOrigin` on
the SAME element (`fromTo(g, {scale:.6, y:-60, svgOrigin:"0 0"}, {scale:1, y:0, ...})`;
`fromTo(stone, {y:-320, rotation:-40, svgOrigin:"0 0"}, {y:0, rotation:0, ...})`).
At rest the node sat lower than its static transform implied, so the camera math
(T = -offset × S from viewport-change) aimed at a stale point. Splitting the work —
an outer node for x/y, an inner node for scale/rotation with svgOrigin — or dropping
the svgOrigin tween fixed it both times; the same split was then applied pre-emptively
to a flying sling stone and to stones moved into a pouch.

**Suggested improvement:** In `adapters/gsap-transforms-and-perf.md` (and the camera
rules viewport-change / coordinate-target-zoom), add a rule: never tween x/y and an
svgOrigin-anchored scale/rotation on the same SVG node; nest a translate wrapper and a
rotate/scale wrapper. In the camera rules, add a verification step: snapshot the frame
right after the zoom's handoff and confirm the target colour fills it, because an
off-target zoom passes lint and `check` cleanly.

**Principle:** When an animation library composes several transform channels with a
custom origin on one node, the node's resting position is no longer readable from its
static markup; keep translation and origin-anchored rotation/scale on separate nodes
whenever any other code computes that node's position.
