
let themeMode = !localStorage.getItem('themeMode') ? 'dark' : localStorage.getItem('themeMode')
document.querySelector('body').setAttribute('data-bs-theme', themeMode)
document.getElementById('theme_selector_label').innerText = themeMode === 'dark' ? 'Modo Oscuro' : 'Modo Claro'
document.getElementById('theme_selector').checked = themeMode === 'dark';

function ThemeSelector(){
   const selector =  document.getElementById('theme_selector').checked
   if (selector){
       localStorage.setItem('themeMode', 'dark')
       document.getElementById('theme_selector_label').innerText = 'Modo Oscuro'
   }
   else {
       localStorage.setItem('themeMode', 'light')
       document.getElementById('theme_selector_label').innerText = 'Modo Claro'
   }
   location.reload()
}