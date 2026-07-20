# Accessibility protocol

Target: WCAG 2.2 AA.

Automated checks cover semantic component behavior and axe analysis of the PatchGraph. The interface provides a skip link, landmarks, semantic headings, visible focus, minimum 44×44 px controls, non-color status text, light/dark themes, and reduced-motion handling.

The PatchGraph has Beginner, Structural, and Diagnostic views; keyboard cable traversal; zoom/fit/reset controls; port-direction text; arrowheads; signal labels; cable line patterns; active modes; feedback explanations; and a synchronized HTML cable table. The SVG is never the only representation.

Manual release protocol:

1. Complete create-rig, photo review, run selection, patch inspection, and export flows using keyboard only.
2. Test VoiceOver/Safari and NVDA/Firefox landmarks, headings, forms, status announcements, tabs, and cable table.
3. Verify focus remains visible at 200% zoom and reflow at 320 CSS px.
4. Verify dark/light contrast and that cable classes are distinguishable with monochrome display.
5. Verify reduced-motion preference removes nonessential animation.
6. Inspect generated PDFs for reading order; use the text-first companion when full tagging is unavailable.

Manual screen-reader and PDF tagging results are `NOT_COMPUTABLE` until performed by a human release reviewer.
