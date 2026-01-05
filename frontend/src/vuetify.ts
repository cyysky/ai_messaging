import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import '@mdi/font/css/materialdesignicons.css'

export default createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        dark: false,
        colors: {
          primary: '#5C6BC0',
          secondary: '#7E57C2',
          accent: '#26A69A',
          error: '#EF5350',
          info: '#42A5F5',
          success: '#66BB6A',
          warning: '#FFA726',
          background: '#FAFAFA',
          surface: '#FFFFFF',
          'on-background': '#1C1B1F',
          'on-surface': '#1C1B1F',
        },
      },
      dark: {
        dark: true,
        colors: {
          primary: '#7986CB',
          secondary: '#B39DDB',
          accent: '#4DB6AC',
          error: '#EF9A9A',
          info: '#64B5F6',
          success: '#81C784',
          warning: '#FFB74D',
          background: '#121212',
          surface: '#1E1E1E',
          'on-background': '#E6E1E5',
          'on-surface': '#E6E1E5',
        },
      },
    },
  },
  defaults: {
    VCard: {
      elevation: 2,
      rounded: 'lg',
    },
    VBtn: {
      rounded: 'lg',
    },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable',
    },
    VTextarea: {
      variant: 'outlined',
      density: 'comfortable',
    },
  },
})