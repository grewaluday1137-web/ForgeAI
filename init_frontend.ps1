# Initialize Frontend Script for ForgeAI
Set-Location -Path "E:\Projects\ForgeAI"

Write-Host "Creating Next.js application..."
npx -y create-next-app@15.0.0 apps/web --typescript --tailwind --eslint --app --no-src-dir --import-alias "@/*" --use-npm --yes

Set-Location -Path "E:\Projects\ForgeAI\apps\web"

Write-Host "Installing TanStack Query and Zustand..."
npm install @tanstack/react-query zustand

Write-Host "Installing Prettier..."
npm install -D prettier eslint-config-prettier eslint-plugin-prettier

Write-Host "Initializing shadcn/ui..."
npx -y shadcn@latest init -d

Write-Host "Creating requested folder structure..."
New-Item -ItemType Directory -Force -Path "hooks"
New-Item -ItemType Directory -Force -Path "services"
New-Item -ItemType Directory -Force -Path "types"
New-Item -ItemType Directory -Force -Path "styles"

Write-Host "Frontend initialization complete!"
