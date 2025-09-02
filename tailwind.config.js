module.exports = {
  content: ['./views/**/*.ejs', './src/**/*.{ts,tsx,js,jsx}'],
  theme: {
    extend: {
      colors: {
        primary: 'var(--color-primary)',
      },
      textColor: {
        primary: 'var(--color-primary)'
      },
      backgroundColor: {
        primary: 'var(--color-primary)'
      }
    },
  },
  plugins: [],
  // PurgeCSS / content will remove unused classes in production builds. If you generate classes dynamically
  // (eg. from tenant data), add them to the safelist below to avoid being purged.
  safelist: [
    /^bg-/,
    /^text-/,
    'bg-primary', 'text-primary'
  ]
};
