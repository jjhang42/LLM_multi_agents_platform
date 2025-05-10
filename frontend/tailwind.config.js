/** @type {import('tailwindcss').Config} */
module.exports = {
	content: [
	  "./src/**/*.{js,ts,jsx,tsx}",
	  "./app/**/*.{js,ts,jsx,tsx}",
	  "./pages/**/*.{js,ts,jsx,tsx}",
	  "./components/**/*.{js,ts,jsx,tsx}",
	],
	theme: {
	  extend: {
		colors: {
		  mac: {
			bg: 'rgb(28,28,30)',         // macOS System Gray 6
			card: 'rgb(44,44,46)',       // System Gray 5
			border: 'rgb(58,58,60)',     // System Gray 4
			text: 'rgb(229,229,234)',    // System Gray 2
			muted: 'rgb(142,142,147)',   // System Gray 3
		  }
		}
	  },
	},
	darkMode: 'class',
	plugins: [],
  }
  