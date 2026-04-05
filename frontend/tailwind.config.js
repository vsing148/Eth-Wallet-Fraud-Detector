/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            // You can add custom theme extensions here if needed, 
            // but we used arbitrary values like [#00e676] in the code
            // which Tailwind handles automatically!
        },
    },
    plugins: [],
}