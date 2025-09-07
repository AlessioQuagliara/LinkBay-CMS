// backup - original tailwind.config.js
module.exports = {
  content: [
    './views/**/*.ejs',
    './server/**/*.{js,ejs}',
    './src/**/*.{js,ts,jsx,tsx,ejs}',
  ],
  theme: {
    extend: {
      colors: {
        primary: 'var(--color-primary)'
      }
    }
  },
  plugins: [],
  safelist: [
  /^bg-/, /^text-/, /^from-/, /^to-/, /^hover:bg-/, /^hover:text-/, /^border-/, /^ring-/,
  'bg-red-600','hover:bg-red-700','text-white','bg-white','bg-gray-900','text-gray-900','text-gray-700','text-gray-600','bg-red-700','from-red-500','to-orange-500','bg-gradient-to-r','bg-gradient-to-br',
  /^bg-(red|gray|white|green|yellow|blue|orange)-/,
  /^text-(red|gray|white|green|yellow|blue|orange)-/,
  /^hover:bg-(red|gray|white|green|yellow|blue|orange)-/
  ]
};
