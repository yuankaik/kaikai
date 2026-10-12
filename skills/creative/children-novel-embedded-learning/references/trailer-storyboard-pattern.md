# Trailer & Storyboard Pattern for Children's Novels

When converting a children's novel into multimedia to attract young readers, two artifacts deliver high impact without requiring GPU/rendering infrastructure.

## 1. Animated HTML Trailer

Self-contained single-file HTML that plays like a movie teaser in any browser.

**Structure:**
- 8-10 "shots" auto-advancing with timed transitions (~60-90s total)
- Canvas-based particle system (bubbles, light rays, floating characters)
- Dark themed background with ocean/space atmosphere
- CSS @keyframes for text reveals, fades, glows

**Key patterns:**
- CSS animations triggered by JavaScript class toggling (not on page load)
- `requestAnimationFrame` loop for continuous particle/fish movement
- Progress dots + click/keyboard navigation for manual control
- Replay button resets ALL scenes (requires reflow hack for CSS animation restart)
- Parallax depth: different animation speeds for foreground/background elements

**Typical shots for a fantasy children's novel:**
1. Ink drop → title reveal
2. Key quote from story
3. Environment introduction (underwater, forest, space)
4. Welcome message
5. Character introductions (silhouettes + names + roles)
6. World elements showcase (creatures, magic items)
7. Power/leveling progression
8. Dedication page
9. Final title card with subtitle

**Design constraints:**
- Child-friendly: colorful, not scary, sense of wonder
- No external dependencies (use system fonts or single CDN font)
- Responsive (CSS clamp, media queries for mobile)
- Ocean palette: deep navy #0a1628, teal #1a5276, aqua #2ecc71, gold #f39c12

## 2. Storyboard Illustration Prompts

20 key scenes with bilingual AI image-generation prompts, ready to copy-paste into any tool.

**Per-scene format:**
1. Scene number + title
2. Chapter reference
3. Chinese visual description (composition, action, emotion, key details)
4. English AI prompt (50-100 words, optimized for Midjourney/DALL-E/ComfyUI, includes style keywords)
5. Character appearance notes for that scene
6. Color palette + mood
7. Suggested aspect ratio

**Style guide section (at top):**
- Art style: Japanese anime / Ghibli watercolor / soft lighting
- Color palette: unified across all scenes
- Character reference: consistent descriptions for recurring characters

**Quick-start appendix:**
- Midjourney: `--ar 3:4 --style expressive --niji 6`
- DALL-E: aspect ratio settings
- ComfyUI/Stable Diffusion: recommended models, CFG, steps
- Character consistency tips across multiple images

## When to Use

- The target reader is a child (8-12 years old)
- You want to generate interest before the child reads the full book
- No GPU or rendering software available
- Need portable deliverables (HTML opens anywhere, MD prompts work with any image tool)

## User Preference: Office > HTML for Presentations

**kai哥 prefers PowerPoint/Office format over HTML for trailers and presentations.** When the user asks for a book trailer or visual preview, offer OfficeCLI (iOfficeAI/OfficeCLI) to generate a .pptx deck as the primary option. HTML trailers are a fallback if OfficeCLI is unavailable. Storyboard illustration prompts (.md) remain useful for feeding into AI image generators separately.

## Post-Delivery

- Open the HTML trailer in a browser, let the child watch → gauge interest
- If interested, generate images from the storyboard prompts → create an illustrated edition
- Combine illustrated pages + text into a new PDF with the novel layout CSS
