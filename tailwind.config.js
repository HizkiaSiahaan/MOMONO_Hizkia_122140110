// tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}", // atau path sesuai struktur project kamu
  ],
  theme: {
    extend: {
      colors: {
        emerald: {
          DEFAULT: '#10B981',
        },
        eggshell: '#F9F5ED',
      },
    },
  },
  plugins: [],
}
