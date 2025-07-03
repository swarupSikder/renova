/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './**/templates/**/*.html',
    './static/src/**/*.{js,ts}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#f97316', // orange-500
      },
    },
  },
  plugins: [],
};