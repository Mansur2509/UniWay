import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        surface: "hsl(var(--surface))",
        elevated: "hsl(var(--elevated))",
        text: "hsl(var(--text))",
        foreground: "hsl(var(--foreground))",
        card: "hsl(var(--card))",
        border: "hsl(var(--border))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
          hover: "hsl(var(--primary-hover))",
          button: "hsl(var(--button-primary))",
          "button-hover": "hsl(var(--button-primary-hover))"
        },
        navy: {
          DEFAULT: "hsl(var(--navy))",
          foreground: "hsl(var(--navy-foreground))"
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))"
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))"
        },
        success: "hsl(var(--success))",
        warning: "hsl(var(--warning))",
        danger: "hsl(var(--danger))",
        info: {
          DEFAULT: "hsl(var(--info))",
          foreground: "hsl(var(--info-foreground))"
        },
        recommendation: {
          DEFAULT: "hsl(var(--recommendation))",
          foreground: "hsl(var(--recommendation-foreground))"
        },
        event: {
          DEFAULT: "hsl(var(--event))",
          foreground: "hsl(var(--event-foreground))"
        },
        /* Named aliases for the task/content categories from the 026 design
           brief. Most intentionally reuse an existing hue rather than
           inventing a new one per category -- e.g. scholarship/verified both
           mean "confirmed, positive" (success); application/exam are neutral
           status information (info); essay/research are AI-assisted or
           academic-depth content (recommendation). `event` above is the one
           genuinely new hue. Aliasing keeps class names semantic
           (`text-scholarship`, `bg-deadline/10`) without multiplying hues. */
        scholarship: "hsl(var(--success))",
        verified: "hsl(var(--success))",
        deadline: "hsl(var(--accent))",
        application: "hsl(var(--info))",
        exam: "hsl(var(--info))",
        essay: "hsl(var(--recommendation))",
        research: "hsl(var(--recommendation))",
        focus: "hsl(var(--focus-ring))"
      },
      fontFamily: {
        sans: [
          "var(--font-inter)",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "sans-serif"
        ],
        display: ["var(--font-source-serif)", "Georgia", "Cambria", "Times New Roman", "serif"]
      },
      borderRadius: {
        xl: "var(--radius)"
      },
      boxShadow: {
        card: "0 1px 1px rgba(22, 31, 48, 0.05), 0 8px 24px rgba(22, 31, 48, 0.07)"
      },
      transitionDuration: {
        fast: "var(--motion-fast)",
        normal: "var(--motion-normal)",
        slow: "var(--motion-slow)"
      },
      transitionTimingFunction: {
        academic: "var(--motion-ease-out)"
      }
    }
  },
  plugins: []
};

export default config;
