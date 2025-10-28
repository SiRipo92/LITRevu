module.exports = {
  content: [
    "../../templates/**/*.html",            // global theme templates
    "../../accounts/templates/**/*.html",   // app templates
    "../../reviews/templates/**/*.html",    // app templates
    "./**/*.js",                            // any JS files inside static_src
    "./**/*.css"                            // any CSS partials you make
  ],
  theme: { extend: {} },
  plugins: [],
};