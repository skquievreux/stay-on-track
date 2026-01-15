---
title: "Using @squievreux/ui in External Projects"
type: "implementation"
audience: "developer"
status: "approved"
priority: "high"
version: "1.0.0"
created: "2025-12-30"
updated: "2025-12-30"
tags: ["setup", "configuration", "ui", "design-system"]
---
# Using @squievreux/ui in External Projects
## Prerequisites
- [Node.js 20+]
- [pnpm or npm]  
## Step 1: Installation
Install the package using your package manager from the public npm registry:
```bash
# pnpm (recommended)
pnpm add @squievreux/ui
# npm
npm install @squievreux/ui
```
## Step 3: Styling Integration (Tailwind CSS)

To ensure the library's styles are included in the build and to use the design tokens, you **must** configure Tailwind CSS to scan the package files.

Modify your `tailwind.config.ts`:

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    // 👇 IMPORTANT: Include the package in content scan
    "./node_modules/@squievreux/ui/dist/**/*.{js,mjs}"
  ],
  theme: {
    extend: {
      // Map CSS variables to Tailwind colors
      colors: {
        primary: "hsl(var(--q-color-primary))",
        secondary: "hsl(var(--q-color-secondary))",
      }
    },
  },
  plugins: [],
};
export default config;
```
## Step 4: Component Usage
Imports components directly from the package. Note that you need to pass `lucide-react` icons to the `Icon` component.
```tsx
import { Icon } from '@squievreux/ui';
import { Rocket, Settings } from 'lucide-react';
export default function Dashboard() {
  return (
    <div className="p-4">
      <h1>Welcome</h1>
      
      {/* Standard Icon (20px) */}
      <Icon icon={Rocket} /> 
      
      {/* Large Colored Icon using Tailwind classes */}
      <Icon 
        icon={Settings} 
        size="xl" 
        className="text-primary hover:text-primary-hover transition-colors" 
      />
    </div>
  );
}
```
## Troubleshooting

### Issue: Package not found during install
**Solution:**
1. Verify the package name is correct: `@squievreux/ui`.
2. Ensure you are connected to the official npm registry (`https://registry.npmjs.org/`).

### Issue: Styles missing / Icons unstyled
**Symptoms:** Icons appear but have wrong sizes or colors don't work.
**Solution:**
1. Verify the `content` array in `tailwind.config.ts` includes the correct path: `"./node_modules/@squievreux/ui/dist/**/*.{js,mjs}"`
