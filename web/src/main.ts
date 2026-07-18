import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from '@/router'
import '@/style.css'
import { Capacitor } from '@capacitor/core'
import { SplashScreen } from '@capacitor/splash-screen'
import { StatusBar, Style } from '@capacitor/status-bar'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

app.mount('#app')

async function setupNativeUi(): Promise<void> {
	if (!Capacitor.isNativePlatform()) {
		return
	}

	try {
		await StatusBar.setOverlaysWebView({ overlay: false })
		await StatusBar.setStyle({ style: Style.Dark })
		await SplashScreen.hide()
	} catch {
		// Ignore native bridge setup errors to avoid blocking web startup.
	}
}

void setupNativeUi()
