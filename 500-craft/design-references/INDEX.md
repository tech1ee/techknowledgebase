# DESIGN.md Reference Library

AI-optimized design specs extracted from real company websites.
Each file contains 9 sections: Visual Theme, Colors, Typography, Components, Layout, Elevation, Do's/Don'ts, Responsive, Agent Prompts.

## Available References

| Brand | Best For | Size |
|-------|----------|------|
| airbnb | Travel marketplace, warm coral, photography-driven | 14KB |
| apple | Premium consumer, white space, SF Pro, cinematic | 20KB |
| claude | AI assistant, warm terracotta, clean editorial | 20KB |
| cursor | AI code editor, sleek dark, gradient accents | 19KB |
| figma | Collaborative tools, vibrant multi-color, playful | 12KB |
| framer | Website builder, bold black/blue, motion-first | 18KB |
| linear.app | Dark mode, keyboard-first, dense UI, indigo accent | 22KB |
| notion | Warm minimalism, content editing, sidebars | 18KB |
| raycast | Productivity launcher, dark chrome, gradient accents | 18KB |
| spotify | Music streaming, vibrant green on dark, bold type | 13KB |
| stripe | Payment UI, purple gradients, weight-300 elegance | 20KB |
| supabase | Open-source Firebase, dark emerald, code-first | 15KB |
| superhuman | Fast email, premium dark, keyboard-first, purple glow | 19KB |
| tesla | Electric automotive, radical subtraction, near-zero UI | 22KB |
| uber | Mobility, bold black/white, tight type, urban energy | 19KB |
| vercel | Frontend deployment, black/white precision, Geist font | 19KB |

## Usage

```
Read ~/Documents/tech/500-craft/design-references/<brand>/DESIGN.md
```

## Add New Brand

```bash
cd ~/Documents/tech/500-craft/design-references
npx getdesign@latest add <brand> --out ./<brand>/DESIGN.md
```

## List All Available Brands

```bash
npx getdesign@latest list
```

## Update All

```bash
bash ~/Documents/tech/500-craft/design-references/update.sh
```
