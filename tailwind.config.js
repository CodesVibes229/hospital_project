module.exports = {
  content: [
    './frontend/templates/**/*.html',
    './frontend/static/js/**/*.js',
    './frontend/static/css/**/*.css'
  ],
  theme: {
    extend: {
        backgroundImage: {
        'header-bg': "url('/static/images/header-bg.jpg')",
        'logo-bg': "url('/static/images/logo-bg.jpg')",
        },
    },
  },
  plugins: [],
};