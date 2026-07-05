# Finish Frontend Script for ForgeAI
Set-Location -Path "E:\Projects\ForgeAI\apps\web"

Write-Host "Installing TanStack Query and Zustand (with legacy-peer-deps)..."
npm install @tanstack/react-query zustand --legacy-peer-deps

Write-Host "Initializing shadcn/ui..."
npx -y shadcn@latest init -d

Write-Host "Creating requested folder structure..."
New-Item -ItemType Directory -Force -Path "hooks"
New-Item -ItemType Directory -Force -Path "services"
New-Item -ItemType Directory -Force -Path "types"
New-Item -ItemType Directory -Force -Path "styles"

Write-Host "Frontend initialization complete! You can test it by running 'npm run dev' inside the apps/web directory."
