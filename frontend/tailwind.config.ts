import TypographyPlugin from "@tailwindcss/typography";
import FormPlugin from "@tailwindcss/forms";
import ContainerQueriesPlugin from "@tailwindcss/container-queries";
import { type Config } from "tailwindcss";

const config: Config = {
	content: ["./src/**/*.{ts,tsx}"],
	theme: {
		extend: {
			colors: {
				// Primary - Temu Orange (Main brand color)
				primary: {
					50: '#FFF0E6',
					100: '#FFE2CC',
					200: '#FFC599',
					300: '#FFA766',
					400: '#FF8A33',
					500: '#FF6D00',  // Main Temu orange
					600: '#E65500',
					700: '#B34300',
					800: '#803000',
					900: '#4D1D00',
				},
				// Accent - Vibrant Orange variants (For highlights and CTAs)
				accent: {
					50: '#FFF3E6',
					100: '#FFE7CC',
					200: '#FFCF99',
					300: '#FFB766',
					400: '#FF9F33',
					500: '#FF7C1A',  // Lighter orange for accents
					600: '#F75B1C',  // Temu brand orange variant
					700: '#E65500',
					800: '#B34300',
					900: '#803000',
				},
				// Success - MTN Yellow (Mobile Money)
				success: {
					50: '#FFFBEB',
					100: '#FFF7CC',
					200: '#FFEF99',
					300: '#FFE666',
					400: '#FFDE33',
					500: '#FFCC00',
					600: '#E6B800',
					700: '#B38F00',
					800: '#806600',
					900: '#4D3D00',
				},
				// Error Red
				error: {
					500: '#EF4444',
					600: '#DC2626',
				},
				// Info - Kept blue for informational elements
				info: {
					500: '#3B82F6',
					600: '#2563EB',
				},
			},
			fontFamily: {
				sans: ['Inter', 'system-ui', 'sans-serif'],
				mono: ['Roboto Mono', 'monospace'],
			},
			fontSize: {
				'hero': ['3rem', { lineHeight: '1.1', fontWeight: '700' }],
				'display': ['2.25rem', { lineHeight: '1.2', fontWeight: '700' }],
			},
			spacing: {
				'18': '4.5rem',
				'112': '28rem',
				'128': '32rem',
			},
			borderRadius: {
				'xl': '0.75rem',
				'2xl': '1rem',
				'3xl': '1.5rem',
			},
			boxShadow: {
				'card': '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
				'card-hover': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
				'xl-colored': '0 20px 25px -5px rgb(0 102 255 / 0.1), 0 8px 10px -6px rgb(0 102 255 / 0.1)',
			},
			animation: {
				'fade-in': 'fadeIn 0.5s ease-in-out',
				'slide-up': 'slideUp 0.3s ease-out',
				'bounce-slow': 'bounce 3s infinite',
				'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
			},
			keyframes: {
				fadeIn: {
					'0%': { opacity: '0' },
					'100%': { opacity: '1' },
				},
				slideUp: {
					'0%': { transform: 'translateY(10px)', opacity: '0' },
					'100%': { transform: 'translateY(0)', opacity: '1' },
				},
			},
		},
	},
	plugins: [TypographyPlugin, FormPlugin, ContainerQueriesPlugin],
};

export default config;
