module.exports = {
    loaders: [
          {
              test: /\.yaml$/,
              loader: 'yaml'
          }
      ],
  /*
  ** Headers of the page
  */
  head: {
    title: 'Mandáty.cz',
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: 'Frontend for Mandáty.cz' }
    ],
    script: [
        {src: "/js/piwik.js"},
        {src: "https://stackpath.bootstrapcdn.com/bootstrap/4.1.1/js/bootstrap.min.js"}
    ],
    link: [
      { rel: 'icon', type: 'image/x-icon', href: '/favicon.svg' },
      { rel: 'stylesheet', href: 'https://stackpath.bootstrapcdn.com/bootswatch/4.1.1/united/bootstrap.min.css'},
      { rel: 'stylesheet', href: 'https://maxcdn.bootstrapcdn.com/font-awesome/latest/css/font-awesome.min.css'}
    ]
  },
  /*
  ** Customize the progress bar color
  */
  loading: { color: '#3B8070' },
  /*
  ** Build configuration
  */
  build: {
    /*
    ** Run ESLint on save
    */
    extend (config, { isDev, isClient }) {
      if (isDev && isClient) {
        config.module.rules.push({
          enforce: 'pre',
          test: /\.(js|vue)$/,
          loader: 'eslint-loader',
          exclude: /(node_modules)/
        })
      }
    }
  }
}
