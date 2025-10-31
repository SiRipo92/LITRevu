module.exports = {
  content: [
    "../../templates/**/*.html",            // global theme templates
    "../../accounts/templates/**/*.html",   // app templates
    "../../reviews/templates/**/*.html",    // app templates
    "./**/*.js",                            // any JS files inside static_src
    "./**/*.css"                            // any CSS partials you make
  ],
  theme: {
  extend: {},
  screens: {
      xs: "360px",  // very small phones
      sm: "480px",  // standard smartphones
      md: "768px",  // tablets (portrait)
      lg: "1024px", // laptops / small desktops
      xl: "1280px", // large desktops
      "2xl": "1536px", // wide monitors
    },
  },
  plugins: [],
};