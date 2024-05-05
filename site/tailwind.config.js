/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["totteringham/templates/*.html"],
  theme: {
    extend: {
      colors: {
        'afc-blue': '#063672',
        'afc-dark-red': '#DB0007',
        'afc-red': '#EF0107',
        'afc-gold': '#9C824A',
      }
    }
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
    // require('canvas-confetti'),
  ]
}
