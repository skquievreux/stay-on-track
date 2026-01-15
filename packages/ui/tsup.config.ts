import { defineConfig } from 'tsup';
import { copyFileSync, mkdirSync, existsSync } from 'fs';
import { dirname, join } from 'path';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['cjs', 'esm'],
  dts: true,
  splitting: true,
  sourcemap: true,
  clean: true,
  treeshake: true,
  external: ['react', 'react-dom', 'lucide-react'],
  esbuildOptions(options) {
    options.banner = {
      js: '"use client";', // Next.js App Router Kompatibilität
    };
  },
  // CSS-Dateien nach Build kopieren
  onSuccess() {
    const srcCss = 'src/styles/tokens.css';
    const distCss = 'dist/styles/tokens.css';
    
    if (existsSync(srcCss)) {
      // Zielverzeichnis erstellen
      const distDir = dirname(distCss);
      if (!existsSync(distDir)) {
        mkdirSync(distDir, { recursive: true });
      }
      
      // CSS-Datei kopieren
      copyFileSync(srcCss, distCss);
      console.log('✅ CSS-Datei kopiert: dist/styles/tokens.css');
    }
  },
});
