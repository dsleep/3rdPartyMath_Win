Push-Location $PSScriptRoot

#Could use Issues of build order though
$SubModules = Get-ChildItem | ?{ $_.PSIsContainer } | % { $_.Name }

foreach ($SubModule in $SubModules)
{
	Write-Host "CLEAN PROJECT FOR:" $SubModule
		
	Push-Location
	Set-Location ./$SubModule
	
	$CurrentModule = $SubModule		
	
	$BuildFolders = Get-ChildItem -Filter "build*" | ?{ $_.PSIsContainer } | % { $_.Name }
	
	foreach ($DeleteFolder in $BuildFolders)
	{
		Remove-Item $DeleteFolder -Recurse -Force
	}
	
	Write-Host $BuildFolders
	
	Pop-Location
}

Pop-Location