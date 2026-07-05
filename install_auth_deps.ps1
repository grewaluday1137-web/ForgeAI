Set-Location -Path "E:\Projects\ForgeAI\apps\web"
Write-Host "Installing Frontend Auth Dependencies..."
npm install react-hook-form @hookform/resolvers zod @radix-ui/react-label --legacy-peer-deps
Write-Host "Done! Note: It is best to restart your docker-compose containers to pick up the newly mounted node_modules!"
