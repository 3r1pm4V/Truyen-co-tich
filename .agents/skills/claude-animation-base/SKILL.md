---
name: claude-animation-base
description: Starter kit and animation director guide for creating hand-painted 2D cartoon animations in code using p5.js and p5.brush. Features boiling ink linework, watercolor washes, 31 acted emotions, transitions, camera moves, and strict cartoon animation principles (anticipation, squash and stretch, follow-through, moving holds, overshoot). Use when the user asks for hand-painted animations, cartoons, short animated films made with code, p5.js/p5.brush artwork, or character animation with rich emotional acting.
---

# Claude Animation Base (Hand-Painted Cartoon Animation Kit)

Starter kit, instructions, and asset library for animating hand-painted cartoons in **p5.js** and **p5.brush** through code.

## The Three Core Goals

1. **Handmade**: Video looks like someone painted it by hand, frame by frame. Brush strokes (`wash`), ink outlines (`inkLine`), 12fps boiling linework (`BOIL`), soft pigment palettes, flat 2D.
2. **Alive**: Something is always moving and happening. Faces act dynamically instead of snapping, idles breathe, characters have weight and scale.
3. **One Piece**: One coherent short film, not a random pile of clips. Storyboarded first, color arcs, linked scenes, continuous screen direction and transitions.

---

## Animation Principles & Rules

Read [ANIMATION_GUIDE.md](./ANIMATION_GUIDE.md) for the complete reference.

### 1. Medium & Rendering
- **Paint everything with p5.brush**: Characters get flat `wash` color plus an ink outline (`inkLine`). Backgrounds get soft watercolor `fill` shapes. Never use raw p5 shapes (`rect`, `ellipse`, `fill()`).
- **Boiling linework**: Jitter is reseeded 12 times a second (`BOIL`), giving that classic living hand-drawn feel.
- **Flat 2D**: No 3D perspective projection. Characters turn through drawn key views (front $\rightarrow$ 3/4 $\rightarrow$ side $\rightarrow$ back 3/4 $\rightarrow$ back). Depth is established through scale, overlap, and atmospheric color.

### 2. No Text & Show-Don't-Tell
- No subtitles or text signs repeating the narrative. Characters react through painted emote marks (`!`, `?`, zzz, sweat, heart, lightbulb).

### 3. Timing: Model the Viewer
- **Reads**: For each shot, list in order what the viewer must understand. Each item is a *read*.
- **One read at a time**: Give the eye time to find the focal point, register the event, and react before the next event occurs.
- **Fast actions, slow meanings**: Action moves quickly with anticipation, but the payoff/reaction holds long enough for the viewer to absorb.

### 4. Classical Animation Dynamics
- **Anticipation**: Small movement in reverse before any large movement.
- **Squash and Stretch**: Volume preservation (`sq`) upon impact and velocity.
- **Drag & Follow-through**: Limbs and head lag the torso, secondary motion on hair, clothes, and accessories.
- **Moving holds & Overshoot**: Actions overshoot target by 5–10% and settle into an alive moving hold (`feel()`).

---

## Production Workflow

1. **Storyboard**: Write the sequence of shots, listing reads, camera framing, emotion beats, and transitions.
2. **Setup Project**:
   ```bash
   npm install
   ```
3. **Develop Scenes**: Build scenes in `src/scenes/` using `core.js`, `clawd.js` (or custom characters), and `timeline.js`.
4. **Render Stills & Preview**:
   - Open `studio.html` to scrub through frames interactively.
   - Run `node render.mjs --clip --out=out/video.mp4` to export the finished MP4.
