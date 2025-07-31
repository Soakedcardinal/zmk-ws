# Configuration - UPDATE THESE
# Get config from environment
$owner = $env:GITHUB_OWNER ?? "soakedcardinal"
$repo = $env:GITHUB_REPO ?? "zmk-config" 
$token = $env:GITHUB_TOKEN

# Headers
$headers = @{
    "Authorization" = "token $token"
    "Accept" = "application/vnd.github.v3+json"
}

try {
    # Get latest workflow run
    Write-Host "Getting latest workflow run..." -ForegroundColor Green
    $runsUrl = "https://api.github.com/repos/$owner/$repo/actions/runs"
    $runs = Invoke-RestMethod -Uri $runsUrl -Headers $headers
    
    if ($runs.workflow_runs.Count -eq 0) {
        Write-Host "No workflow runs found" -ForegroundColor Red
        exit 1
    }
    
    $runId = $runs.workflow_runs[0].id
    Write-Host "Found run: $runId" -ForegroundColor Green
    
    # Get artifacts
    $artifactsUrl = "https://api.github.com/repos/$owner/$repo/actions/runs/$runId/artifacts"
    $artifacts = Invoke-RestMethod -Uri $artifactsUrl -Headers $headers
    
    if ($artifacts.artifacts.Count -eq 0) {
        Write-Host "No artifacts found" -ForegroundColor Red
        exit 1
    }
    
    $artifact = $artifacts.artifacts[0]
    $artifactName = $artifact.name
    $downloadUrl = $artifact.archive_download_url
    
    Write-Host "Downloading artifact: $artifactName" -ForegroundColor Green
    
    # Download artifact
    $zipPath = "$artifactName.zip"
    Invoke-WebRequest -Uri $downloadUrl -Headers $headers -OutFile $zipPath
    
    # Create/clean release directory
    if (Test-Path "release") { Remove-Item "release" -Recurse -Force }
    New-Item -ItemType Directory -Path "release" -Force | Out-Null
    
    # Extract
    Write-Host "Extracting to release folder..." -ForegroundColor Green
    Expand-Archive -Path $zipPath -DestinationPath "release" -Force
    
    # Cleanup
    Remove-Item $zipPath
    
    Write-Host "Success! Check the ./release/ folder" -ForegroundColor Green
    Get-ChildItem "release"
    
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}