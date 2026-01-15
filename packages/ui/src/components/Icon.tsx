import { LucideIcon, LucideProps } from 'lucide-react';

/**
 * Standardisierte Icon-Größen
 * Basierend auf 4px Grid-System
 */
export type IconSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';

/**
 * Mapping von Size-Token zu Tailwind-Klassen
 */
export const iconSizes: Record<IconSize, string> = {
    xs: 'h-3 w-3',      // 12px - Badges, inline
    sm: 'h-4 w-4',      // 16px - Compact buttons
    md: 'h-5 w-5',      // 20px - DEFAULT
    lg: 'h-6 w-6',      // 24px - Cards
    xl: 'h-8 w-8',      // 32px - Features
    '2xl': 'h-10 w-10', // 40px - Hero sections
};

/**
 * Pixel-Werte für programmatische Nutzung
 */
export const iconSizesPx: Record<IconSize, number> = {
    xs: 12,
    sm: 16,
    md: 20,
    lg: 24,
    xl: 32,
    '2xl': 40,
};

export interface IconProps extends Omit<LucideProps, 'size'> {
    /** Lucide Icon Component */
    icon: LucideIcon;
    /** Vordefinierte Größe */
    size?: IconSize;
    /** Zusätzliche CSS-Klassen */
    className?: string;
    /** Accessible Label */
    label?: string;
}

/**
 * Icon Component
 * 
 * Wrapper für Lucide Icons mit standardisierten Größen und Styling.
 * 
 * @example
 * ```tsx
 * import { Icon } from '@squievreux/ui';
 * import { Music } from 'lucide-react';
 * 
 * <Icon icon={Music} size="lg" className="text-primary" />
 * ```
 */
export function Icon({
    icon: LucideIcon,
    size = 'md',
    className = '',
    label,
    strokeWidth = 1.75,
    ...props
}: IconProps) {
    const sizeClass = iconSizes[size];

    return (
        <LucideIcon
            className={`shrink-0 ${sizeClass} ${className}`.trim()}
            strokeWidth={strokeWidth}
            aria-label={label}
            aria-hidden={!label}
            {...props}
        />
    );
}

export default Icon;
