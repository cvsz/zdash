# zDash Dashboard Visual Refresh Prompt Pack
## Figma Community Reference + Logo + Banner + Social Media

Generated: `2026-05-30T11:59:44+00:00`  
Repo target: `cvsz/zdash`  
Primary Figma reference: `https://www.figma.com/community/file/1642481897281072423`  
Secondary live reference: `https://iron-footer-06550759.figma.site/`

Use these references for visual direction only. Do **not** copy proprietary assets, exact layouts, logos, illustrations, screenshots, or brand marks.

---

# 1. Meta Master Coding Agent Prompt

```text
You are a senior frontend architect, product designer, design-system engineer, QA lead, accessibility reviewer, and release engineer.

Repository:
cvsz/zdash

Task:
Update the zDash dashboard UI to a premium modern dark SaaS / AI cloud operations control-panel style inspired by this Figma Community reference:
https://www.figma.com/community/file/1642481897281072423

Also use this live reference for visual direction:
https://iron-footer-06550759.figma.site/

Important:
- Use references as inspiration only.
- Do not copy protected assets, exact layouts, exact text, exact icons, logos, illustrations, or brand marks.
- Create an original zDash design system.

============================================================
0. ABSOLUTE SAFETY RULES
============================================================

Do not enable:
- live trading
- real broker execution
- real IoT/device actions
- real social posting
- real infrastructure mutation
- secret export
- raw shell relay
- destructive automation
- paid-service requirements

Preserve:
- DRY_RUN=true defaults
- Guardian/risk checks
- kill switch
- drawdown guard
- RBAC
- tenant isolation
- audit logging
- approval gates
- typed confirmation gates
- provider mock/safe mode
- backend port 8005
- frontend port 5173

Never expose secrets through:
- frontend code
- VITE_* variables
- logs
- generated reports
- screenshots
- examples
- .env files

============================================================
1. FIRST INSPECTION
============================================================

Run from repo root:

git status --short
git branch --show-current
cat AGENTS.md || true
cat README.md || true
cat Makefile || true
cat frontend/package.json || true
cat frontend/vite.config.ts || true
find frontend/src -maxdepth 4 -type f | sort
grep -R "Dashboard\|Sidebar\|Topbar\|Layout\|Card\|Metric\|Navigation\|Status\|Safety" -n frontend/src || true

If Figma access is available:
1. Open the Figma Community file.
2. Duplicate it into the design workspace if needed.
3. Inspect pages, frames, tokens, components, color styles, typography styles, shadows, radii, spacing, layout, grid, and responsive behavior.
4. Extract only design principles and token inspiration.
5. Do not copy the actual design directly.

If browser/Playwright is available:
1. Start zDash frontend on port 5173.
2. Capture current dashboard screenshots.
3. Open the live reference URL.
4. Capture reference screenshots.
5. Compare visual hierarchy, spacing, layout, cards, navigation, motion, and responsive behavior.

If either reference is unavailable:
Continue with the design system defined below.

============================================================
2. TARGET VISUAL SYSTEM
============================================================

Design mood:
- premium
- dark
- futuristic but professional
- AI operations command center
- enterprise SaaS
- Cloudflare-style operational clarity
- secure automation
- release-gated control panel
- high-trust infrastructure UI

Core UI language:
- deep dark background
- subtle radial gradient glows
- glassmorphism cards
- clean border highlights
- compact professional sidebar
- high-contrast command topbar
- polished metric cards
- safety status banners
- provider cards
- phase progress grid
- activity timeline
- report/release panels
- responsive dashboard layout

Design tokens:

Background:
#05070D
#080B12
#0B1020

Surface:
rgba(15, 23, 42, 0.72)
rgba(15, 23, 42, 0.92)

Border:
rgba(148, 163, 184, 0.16)

Text:
#F8FAFC
#CBD5E1
#94A3B8
#64748B

Accent:
#22D3EE
#3B82F6
#8B5CF6

State:
#22C55E success
#F59E0B warning
#EF4444 danger
#38BDF8 info

Radius:
cards 18px to 24px
buttons 12px to 16px
badges 999px

Effects:
soft shadow
inner border highlight
radial glow background
hover lift
subtle active state
prefers-reduced-motion support

============================================================
3. REQUIRED DASHBOARD UPDATES
============================================================

Update the UI while preserving existing routes and data behavior.

Required areas:
1. App shell
2. Sidebar navigation
3. Top command bar
4. Main dashboard page
5. Safety banner
6. Metric cards
7. Provider status cards
8. Phase progress grid
9. Event timeline
10. Validation/release panel
11. Reports links
12. Loading states
13. Empty states
14. Error states
15. Mobile responsive layout

Minimum visible safety states:
- DRY_RUN ACTIVE
- LIVE_TRADING_ACK=false
- RISK_GUARDIAN_ENABLED=true
- SOCIAL_AUTO_POST_ENABLED=false
- IOT_DRY_RUN=true
- MT5_ENABLED=false
- Provider Safe Mode
- Audit Ready
- Release Gate

High-risk actions:
- disabled by default
- show reason
- require admin permission
- require typed confirmation
- show audit-event preview
- show rollback path if applicable

============================================================
4. COMPONENT PLAN
============================================================

Create or update equivalent components:

frontend/src/components/ui/AppShell.tsx
frontend/src/components/ui/Sidebar.tsx
frontend/src/components/ui/Topbar.tsx
frontend/src/components/ui/GlassCard.tsx
frontend/src/components/ui/MetricCard.tsx
frontend/src/components/ui/StatusBadge.tsx
frontend/src/components/ui/SafetyBanner.tsx
frontend/src/components/ui/CommandButton.tsx
frontend/src/components/ui/EventTimeline.tsx
frontend/src/components/ui/PhaseProgressGrid.tsx
frontend/src/components/ui/DataPanel.tsx
frontend/src/components/ui/ProviderCard.tsx
frontend/src/components/ui/ReleaseGateCard.tsx

Rules:
- If equivalent components already exist, update them.
- Avoid duplicate component systems.
- Keep props backward-compatible where practical.
- Keep dashboard data sources intact.
- Do not break tests.

============================================================
5. ACCESSIBILITY REQUIREMENTS
============================================================

Must pass:
- keyboard navigation
- visible focus states
- readable contrast
- semantic buttons/links
- status color also has text
- no motion-only meaning
- responsive mobile layout
- reduced-motion media query
- no tiny unreadable text

============================================================
6. TESTING REQUIREMENTS
============================================================

Run the strongest available commands:

make frontend-test
make frontend-build
make validate-fast

If Makefile commands are unavailable:

cd frontend
npm install --legacy-peer-deps --no-audit --fund=false
npm test
npm run build

Add or update tests if practical:
- dashboard renders
- safety banner visible
- dry-run badge visible
- high-risk action disabled by default
- provider safe mode visible
- mock fallback visible when backend unavailable
- mobile layout does not crash
- no secret-like VITE variables displayed

============================================================
7. REQUIRED REPORT
============================================================

Create or update:

docs/reports/dashboard-figma-community-visual-refresh-report.md

Report content:
- Figma Community reference used
- Live reference used
- Files changed
- Components changed
- Design tokens changed
- Screenshots captured or unavailable
- Safety states preserved
- Accessibility checks
- Validation commands and results
- Known risks
- Next actions
- Release decision READY/HOLD

============================================================
8. FINAL RESPONSE FORMAT
============================================================

Done.

Changed files:
- ...

Design updates:
- ...

Safety preserved:
- ...

Validation:
- command: passed/failed/not run

Screenshots:
- path or unavailable

Release decision:
- READY/HOLD
- reason

Next commands:
- ...
```

---

# 2. Logo Prompt

```text
Create a professional logo for "zDash", an AI cloud operations dashboard and safety-first automation control panel.

Brand keywords:
AI operations, cloud control panel, secure automation, dashboard, command center, dry-run safety, enterprise SaaS, futuristic but trustworthy.

Logo direction:
- modern abstract "Z" mark
- subtle dashboard/grid motif
- cloud/edge/network signal hints
- shield or safety geometry integrated subtly
- clean vector style
- high contrast
- works as app icon and header logo
- no copied brand marks

Style:
premium dark tech, minimal geometric, neon cyan + blue + violet accent, matte black background, crisp vector edges, balanced negative space.

Palette:
#05070D, #22D3EE, #3B82F6, #8B5CF6, #F8FAFC

Create variations:
1. full wordmark: zDash
2. icon-only Z mark
3. monochrome
4. square app icon
5. transparent background

Negative prompt:
no cartoon, no clutter, no stock logo look, no cryptocurrency coin cliché, no copied Cloudflare/OpenAI/GitHub/Figma/Canva marks, no unreadable tiny text.
```

---

# 3. Website / Dashboard Hero Banner Prompt

```text
Design a hero banner for "zDash" — Safety-First AI Operations Control Panel.

Headline:
Safety-First AI Operations Control Panel

Subheadline:
Monitor phases, providers, risk guards, dry-run workflows, audit logs, and release readiness from one production-grade dashboard.

Visual direction:
premium dark SaaS hero, futuristic command center, glassmorphism dashboard cards, glowing network lines, cloud-edge infrastructure feel, security/risk shield motif, phase progress widgets, audit timeline preview, dry-run safety badge, modern gradient lighting, high contrast.

Layout:
left side headline and CTA buttons
right side dashboard mockup with metric cards
background dark radial gradient
accents cyan, blue, violet

Badges:
DRY_RUN ACTIVE
Guardian Enabled
Audit Ready
Release Gate
Provider Safe Mode

Aspect ratios:
website hero 1920x900
LinkedIn banner 1584x396
X/Twitter banner 1500x500
YouTube banner 2560x1440 safe area centered

Negative prompt:
no copied UI from other brands, no fake customer logos, no API keys, no cluttered text, no low-contrast typography.
```

---

# 4. Social Media Creative Prompt

```text
Create a premium social media post for zDash.

Topic:
Final Release Readiness for AI Operations

Core message:
zDash brings dry-run safety, provider control, audit logs, phase tracking, and release gates into one AI operations dashboard.

Visual:
dark futuristic SaaS dashboard, glass cards, phase progress grid, safety status badges, cyan/blue/violet gradient glow, clean enterprise layout, high contrast typography.

Post text:
zDash
AI Ops Control Panel
Dry-run by default. Audit-ready. Release-gated.

Badge text:
Guardian ON
DRY_RUN ACTIVE
32-Phase Roadmap
Provider Safe Mode

Formats:
Instagram portrait 1080x1350
Instagram square 1080x1080
X/Twitter post 1600x900
LinkedIn post 1200x1200

Negative prompt:
no copied brand logos, no excessive tiny text, no clutter, no unrealistic trading claims, no API keys or code secrets.
```

---

# 5. Caption Pack

## LinkedIn

```text
zDash is moving toward final-release readiness.

The focus:
- dry-run safety by default
- provider-safe integrations
- release gates
- audit logs
- phase traceability
- production fail-closed checks

Built for AI operations teams that need control, visibility, and safer automation.
```

## X / Twitter

```text
zDash final-release mode:

Dry-run by default.
Guardian enabled.
Provider-safe.
Audit-ready.
Release-gated.

AI Ops needs control before automation.
```

## Community Post

```text
zDash is being upgraded into a production-grade AI operations control panel with safety-first defaults, phase tracking, provider controls, audit logs, and final-release readiness checks.
```

---

# 6. Canva Command Prompt

```text
/canva create brand kit concept for zDash:
logo: modern abstract Z mark
colors: dark base, cyan, blue, violet
style: premium AI cloud SaaS
assets: website hero banner, LinkedIn banner, Instagram post, YouTube thumbnail
message: Safety-First AI Operations Control Panel
```

---

# 7. Figma Command Prompt

```text
/figma create dashboard redesign system for zDash:
reference file: https://www.figma.com/community/file/1642481897281072423
secondary reference: https://iron-footer-06550759.figma.site/
mood: premium dark SaaS, AI cloud control panel, glassmorphism
pages: Design Tokens, Components, Dashboard, Reports, Safety Center, Release Gate
components: sidebar, topbar, metric card, safety banner, phase grid, event timeline, provider card, command button
output: responsive desktop and mobile frames
```

---

# 8. GitHub / Codex Command Prompt

```text
/github update repo cvsz/zdash frontend dashboard visual refresh:
use premium dark SaaS design inspired by:
- https://www.figma.com/community/file/1642481897281072423
- https://iron-footer-06550759.figma.site/

preserve safety defaults and dry-run behavior
update design tokens, dashboard shell, cards, badges, timeline, phase grid, provider cards, release panel, and responsive layout
add docs/reports/dashboard-figma-community-visual-refresh-report.md
run frontend tests/build
do not commit secrets
```
