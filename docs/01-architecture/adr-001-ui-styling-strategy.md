---
title: "ADR 001: UI Styling Strategy via Tailwind Content Scanning"
type: "architecture"
audience: "developer"
status: "accepted"
priority: "high"
version: "1.0.0"
created: "2025-12-31"
updated: "2025-12-31"
reviewers: ["@user"]
related: []
tags: ["ui", "tailwind", "architecture"]
---

# ADR 001: UI Styling Strategy via Tailwind Content Scanning

## Status
Accepted

## Date
2025-12-31

## Context
When distributing the `@squievreux/ui` package, conflicts arose regarding CSS delivery. Initially, an `@import` of a compiled CSS file was suggested, but this file was often missing or out of sync, leading to build failures in consuming applications (e.g., `vibecoder-architect-reviewer`). We needed a mechanism that respects the consumer's theme and minimizes bundle size.

## Decision
We decided to relying on **Tailwind CSS Content Scanning** at the consumer level. The `@squievreux/ui` package will **not** export a standalone CSS bundle. Instead, consuming applications must add the package's distribution path to their `tailwind.config.js` `content` array.

```javascript
// tailwind.config.js in consumer app
module.exports = {
  content: [
    // ...
    "./node_modules/@squievreux/ui/dist/**/*.{js,mjs}",
  ],
  // ...
}
```

## Consequences

### Positive
- **Tree Shaking**: Only the CSS classes actually used in the application are generated, reducing final bundle size.
- **Theming**: Components automatically inherit the consuming application's theme configuration (colors, spacing, etc.).
- **Simplicity**: Removes the need for complex CSS build/extraction pipelines within the UI package itself.

### Negative
- **Onboarding**: Requires manual configuration in `tailwind.config.js` for every new consumer.

### Mitigations
- Clear documentation instructions added to `@squievreux/ui/README.md`.
