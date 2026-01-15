---
title: "SOP: Integrating @squievreux/ui Design System"
type: "implementation"
audience: "developer"
status: "approved"
priority: "critical"
version: "1.0.0"
created: "2025-12-30"
updated: "2025-12-30"
tags: ["standard-procedure", "ui", "onboarding"]
---

# Standard Operating Procedure (SOP): Integrating @squievreux/ui

## Executive Summary
This procedure outlines the mandatory steps to integrate the centralized Design System (`@squievreux/ui`) into application repositories. Adherence to this guide ensures visual consistency and maintainability across the ecosystem.

---

## 1. Authentication Configuration

The package is published as a **Public Scoped Package** on **npm**. 
No tokens or authentication are required to install the package in local development or CI environments.

---

## 2. Dependencies

Install the UI package and its peer dependencies using your package manager:

```bash
# Install package
pnpm add @squievreux/ui

# Ensure peer dependencies are present (if not automatically installed)
pnpm add lucide-react
```

---

## 3. Tailwind CSS Integration

To enable the design tokens and ensure the library's styles are included in the build, update `tailwind.config.ts`:

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    // ⬇️ CRITICAL: Add this line to scan the UI package for utility classes
    "./node_modules/@squievreux/ui/dist/**/*.{js,mjs}"
  ],
  theme: {
    extend: {
      // Map CSS Variables to Tailwind Colors
      colors: {
        primary: {
          DEFAULT: "hsl(var(--q-color-primary))",
          hover: "hsl(var(--q-color-primary-hover))",
          active: "hsl(var(--q-color-primary-active))",
        },
        secondary: {
          DEFAULT: "hsl(var(--q-color-secondary))",
          hover: "hsl(var(--q-color-secondary-hover))",
          active: "hsl(var(--q-color-secondary-active))",
        }
      }
    },
  },
  plugins: [],
};
export default config;
```

---

## 4. Global Styles

/* Global Styles */
@tailwind base;
@tailwind components;
@tailwind utilities;


---

## 5. Usage Guidelines

### 5.1 Icons
**Rule:** Always use the `Icon` wrapper component to maintain consistent sizing relative to the text scale.

```tsx
import { Icon } from '@squievreux/ui';
import { Rocket } from 'lucide-react';

// ✅ CORRECT:
<Icon icon={Rocket} size="md" />

// ❌ INCORRECT:
<Rocket className="w-5 h-5" />
```

### 5.2 Version Management
The package uses Semantic Versioning.
- **Bug Fixes:** Automatic patch updates (`^0.1.x`) are safe.
- **New Features:** Require minor updates.
- **Updates:** Run `pnpm update @squievreux/ui` to fetch the latest version.
