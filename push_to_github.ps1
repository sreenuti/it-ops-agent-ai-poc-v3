# PowerShell script to push to GitHub
# Run this after creating the repository on GitHub

$repoName = "it-ops-agent-poc-v3"
$username = "sreenuti"  # Update with your GitHub username if different

Write-Host "Setting up remote repository..." -ForegroundColor Cyan

# Add remote (update username if needed)
git remote add origin "https://github.com/$username/$repoName.git"

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host "Repository URL: https://github.com/$username/$repoName" -ForegroundColor Green
} else {
    Write-Host "Push failed. Please check:" -ForegroundColor Red
    Write-Host "1. Repository exists on GitHub" -ForegroundColor Yellow
    Write-Host "2. You have push access" -ForegroundColor Yellow
    Write-Host "3. You're authenticated (may need to enter credentials)" -ForegroundColor Yellow
}

