param(
    [string]$proxy = "http://127.0.0.1:10808"
)

$ErrorActionPreference = "Stop"

$old_http_proxy  = $env:HTTP_PROXY
$old_https_proxy = $env:HTTPS_PROXY

try {
    $env:HTTP_PROXY  = $proxy
    $env:HTTPS_PROXY = $proxy

    winget upgrade --all `
        --accept-source-agreements `
        --accept-package-agreements `
        --proxy $proxy `
        --verbose-logs
}
finally {
    $env:HTTP_PROXY  = $old_http_proxy
    $env:HTTPS_PROXY = $old_https_proxy
}
