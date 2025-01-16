import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve, basename, extname } from 'path'
import fs from 'fs'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      input: (() => {
        const extensionDir = resolve(__dirname, 'src/extension')

        const entries: Record<string, string> = {}

        // Process files in src/extension
        if (fs.existsSync(extensionDir)) {
          const extensionFiles = fs.readdirSync(extensionDir)

          extensionFiles.forEach((file) => {
            const name = basename(file, extname(file))
            entries[`extension/${name}`] = resolve(extensionDir, file)
          })
        }

        // Add the main entry (e.g., popup or main application)
        entries.main = resolve(__dirname, 'index.html')

        console.log('Generated Rollup input entries:', entries)
        return entries
      })(),
      output: {
        // Customize the naming convention for the output files
        entryFileNames: (chunkInfo) => {
          const moduleId = chunkInfo.facadeModuleId

          if (moduleId?.includes('/src/extension/')) {
            const fileName = basename(moduleId)
            return `extension/${fileName}`
          }

          return 'assets/[name].js'
        },
        assetFileNames: 'assets/[name].[hash][extname]',
      },
    },
  },
})
