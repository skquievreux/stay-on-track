# @squievreux/ui

Zentrales Design-System Package für Quievreux Applications.
Beinhaltet standardisierte Icons (Lucide) und CSS Design Tokens.

## Installation

```bash
npm install @squievreux/ui
# oder
pnpm add @squievreux/ui
```

Voraussetzung: `.npmrc` mit GitHub Token konfiguriert.

## Integration (Tailwind CSS)

Anstatt ein CSS-File zu importieren, muss Tailwind CSS so konfiguriert werden, dass es den JavaScript-Code dieses Pakets nach Klassen scannt.

Füge dazu folgenden Pfad in deine `tailwind.config.js` unter `content` hinzu:

```javascript
module.exports = {
  content: [
    // ... andere Pfade
    "./node_modules/@squievreux/ui/dist/**/*.{js,mjs}"
  ],
  // ...
}
```

Dadurch wird nur das CSS generiert, das tatsächlich verwendet wird.

## Icons

Verwende die `Icon` Komponente für konsistente Größen:

```tsx
import { Icon } from '@squievreux/ui';
import { Music, Play } from 'lucide-react';

export function Player() {
  return (
    <div>
      <Icon icon={Music} size="md" />
      <Icon icon={Play} size="lg" className="text-primary" />
    </div>
  );
}
```

### Größen (Sizes)

| Token | Pixel | Tailwind  |
| ----- | ----- | --------- |
| `xs`  | 12px  | h-3 w-3   |
| `sm`  | 16px  | h-4 w-4   |
| `md`  | 20px  | h-5 w-5   |
| `lg`  | 24px  | h-6 w-6   |
| `xl`  | 32px  | h-8 w-8   |
| `2xl` | 40px  | h-10 w-10 |

## Development

```bash
pnpm install
pnpm build
```

## Lizenz

UNLICENSED
