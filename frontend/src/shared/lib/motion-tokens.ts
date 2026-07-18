// Numeric mirror of the CSS custom properties in globals.css
// (--motion-fast/normal/slow, --motion-ease-out) for use inside motion/react
// transition objects, which take seconds/arrays rather than CSS strings.
// Keep these two files in sync by hand -- there are only 4 values.
export const MOTION_DURATION = { fast: 0.14, normal: 0.22, slow: 0.32 } as const;
export const MOTION_EASE_OUT = [0.16, 1, 0.3, 1] as const;
export const HERO_SEQUENCE_MAX_S = 0.6;
