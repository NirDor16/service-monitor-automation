Write-Host "=== Running Python Environment Checks ==="

Write-Host "`nRunning API checks..."
python -m monitor.api_checker

Write-Host "`nRunning Network checks..."
python -m monitor.network_checker

Write-Host "`nRunning PyTest..."
python -m pytest

Write-Host "`nAll checks completed."
