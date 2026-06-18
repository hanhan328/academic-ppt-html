# Design System v2 — Quick Reference

## CDNs (already in shell)
- Tailwind CSS, Chart.js 4, Font Awesome 6.5

## Themes
Four themes: `dark` (default), `light`, `tech`, `warm`
Each theme provides: bg, bg_grad, text, text_sec, text_muted, card, card_border, primary, primary_bg, primary_glow, accent, accent_bg, success, warning, error, glass, nav_bg

## Typography
- Font: Inter (300-900 weights)
- DO NOT use font-sans/font-serif on individual elements (body inherits)
- Use font-bold/font-extrabold for headings only

## Layout Rules
- 16:9 viewport, NO scrollbars (overflow: hidden)
- Padding: 2.5rem 4rem on slides
- All content MUST fit in one viewport

## Glass Card Component
```
.glass {
    background: rgba(30,41,59,0.7);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(71,85,105,0.5);
    border-radius: 1rem;
}
```

## Slide Types Available

### Title Slide
- Large title (3.2rem), subtitle, meta info
- Decorative blur circles
- Badge: "学术论文演示"

### Outline Slide
- Numbered items with primary-colored badges
- Glass card container

### Bullets Slide
- Icon-prefixed bullet items with bullet-icon circles
- Title with icon-circle header

### Numbered Steps Slide
- Numbered badges (2.2rem squares)
- Step title + description

### Stat Cards Slide
- Grid of stat cards (label + value + desc)
- Hover effect with translateY

### Icon Cards Slide
- Grid of glass cards with FA icon, title, description
- Accent-colored icons

### Two-Column Slide
- Left/right glass panels with headers
- Chevron-right bullet icons

### Timeline Slide
- Horizontal timeline with node dots
- Connected by ::before pseudo-element track

### Figure Slide
- Centered image with border and shadow
- Caption in glass pill badge
- Figure ID badge top-left

### Multi-Figure Slide
- Grid layout (2-3 columns)
- Each image with sub-caption

### Table Slide
- Glass card container
- Styled data-table with hover effects
- Table ID badge

### Chart Slide
- Chart.js canvas in glass container
- IIFE wrapper for scope isolation

### Q&A Slide
- Large "Q & A" heading
- Three icon cards (code, PDF, email)
- Decorative circles

## Navigation
- Progress bar at top (3px, primary color with glow)
- Slide number badge top-right
- Bottom nav bar with dots + arrows
- Keyboard: ← → Space PageUp PageDown Home End
- Touch: swipe left/right

## Decorative Elements
- `.deco-circle`: Absolute positioned blur circles
- Primary glow colors for depth
- Accent color secondary circles

## Icon Usage Rules
- Every slide title has an icon-circle header
- Bullet items have small icon circles
- Numbered steps have primary-colored badges
- Stat cards use FA icons for labels
- Use TOPIC_ICONS mapping for context-appropriate icons

## Figure Placement Rules
- Figures are categorized by caption keywords: intro, method, experiment, data, ablation
- Intro figures placed after background slide
- Method figures placed after method/architecture slides
- Result figures placed after experiment/results slides
- Smart trimming preserves visual slides (1/3 of available slots)
