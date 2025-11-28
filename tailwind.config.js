module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/*.py",
  ],
  theme: {
    extend: {},
    screens: {
      xs: "360px",
      sm: "480px",
      md: "768px",
      lg: "1024px",
      xl: "1280px",
      "2xl": "1536px",
    },
  },
  plugins: [require("daisyui")],
}
