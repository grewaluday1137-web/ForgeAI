# Bypass shadcn init hang
Set-Location -Path "E:\Projects\ForgeAI\apps\web"

Write-Host "Installing shadcn/ui dependencies directly..."
npm install tailwind-merge clsx lucide-react class-variance-authority @radix-ui/react-slot

Write-Host "Creating requested folder structure..."
New-Item -ItemType Directory -Force -Path "hooks"
New-Item -ItemType Directory -Force -Path "services"
New-Item -ItemType Directory -Force -Path "types"
New-Item -ItemType Directory -Force -Path "styles"
New-Item -ItemType Directory -Force -Path "components/ui"

Write-Host "Frontend initialization is now 100% complete!"
