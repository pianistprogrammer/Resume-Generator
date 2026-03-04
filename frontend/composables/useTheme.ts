export const useTheme = () => {
  const isDark = useState('theme-dark', () => true)

  const toggleTheme = () => {
    isDark.value = !isDark.value
    updateHtmlClass()
  }

  const setTheme = (dark: boolean) => {
    isDark.value = dark
    updateHtmlClass()
  }

  const updateHtmlClass = () => {
    if (process.client) {
      // Force remove and add to ensure reactivity
      document.documentElement.classList.remove('dark', 'light')

      if (isDark.value) {
        document.documentElement.classList.add('dark')
        localStorage.setItem('theme', 'dark')
      } else {
        document.documentElement.classList.add('light')
        localStorage.setItem('theme', 'light')
      }

      // Force a repaint by toggling a data attribute
      document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
    }
  }

  const initTheme = () => {
    if (process.client) {
      const savedTheme = localStorage.getItem('theme')
      if (savedTheme === 'light') {
        isDark.value = false
      } else {
        isDark.value = true
      }
      updateHtmlClass()
    }
  }

  return {
    isDark,
    toggleTheme,
    setTheme,
    initTheme
  }
}
