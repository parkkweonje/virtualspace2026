---
id: 2
title: "Object zoom-through transitions: hand off only once the target covers the frame, and drop noise/texture filters during deep zoom"
status: open
type: open-source
skill: [hyperframes-animation]
proposes_skill: []
target_file: []
siblings_checked: "no family registry; hyperframes family — hyperframes-animation added (transitions/css-scale.md 'Zoom Through' and rules/viewport-change.md own this), hyperframes-keyframes excluded (camera keyframe mechanics are correct; the gap is transition handoff policy), hyperframes-creative excluded (style, not timing)"
area: "transitions/css-scale.md Zoom Through; rules/viewport-change.md"
date: 2026-10-21
session_context: "Three hand-drawn 40s motion graphics with match-cut zooms into objects (an eye pupil, a jar mouth, a sun, a well opening, a candle flame, a helmet slit, a stone)"
parked_until:
resolved:
resolution:
reference:
commands_verified: none
---

**Issue:** The catalog's Zoom Through gives a fixed overlap (incoming starts at
T + 0.15). For an object-targeted zoom (camera dives into a small shape whose colour
should become the next scene), every first draft cross-faded too early: with a
power2.in log-scale zoom the target only covers the frame in the last ~5% of the
tween, so the next scene appeared over a half-zoomed previous scene (muddy double
exposure), seen in at least five transitions across three films. Separately, SVG
feTurbulence/feDisplacementMap "crayon" textures blew up into large blotches at
S > ~3, because the filter is rasterised in local units before the CSS scale.
Fixes that worked: compute the scale at which the target's half-height/half-width
exceeds 540/960 px, start the incoming fade at that moment (≈ zoom end − 0.1s,
fade 0.25–0.35s), and toggle a class that disables texture filters while S > 2.2.

**Suggested improvement:** In transitions/css-scale.md add an "object zoom-through"
variant: required end scale S ≥ max(540/halfHeight, 960/halfWidth) of the target;
incoming fade starts when S(t) crosses that value, not at a fixed offset; a matching
colour (target fill = incoming background or a flood layer) closes the gap. In
rules/viewport-change.md note that SVG noise/displacement filters scale with the
camera and should be switched off above a small zoom factor.

**Principle:** A transition's handoff time should be derived from the visual
condition it depends on (the target filling the frame), not from a fixed offset that
only holds for full-frame scene transitions; and any effect computed in local units
must be re-evaluated when a camera scales its container by orders of magnitude.
