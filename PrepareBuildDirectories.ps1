


$VersionArray = "14.0", "15.0"
$ReadableVersion = "2015", "2017"

$FoundVS = New-Object System.Collections.Generic.List[System.Object]

Write-Host "----------------------------------"
Write-Host "This Will Prepare the 3rd Party Build Directories"
Write-Host "Based on the desired Visual Studio Version you have"
Write-Host "----------------------------------"

Write-Host "----------------------------------"
Write-Host "Listing Visual Studio Installs..."
Write-Host "----------------------------------"

$Iter = 0
foreach ($Version in $VersionArray)
{
	$VSCheck = $null
	
	Try 
	{
		$VSCheck = Get-ItemPropertyValue -Path Registry::HKLM\SOFTWARE\Wow6432Node\Microsoft\VisualStudio\SxS\VS7 -Name $Version  
	}
	Catch [System.Management.Automation.PSArgumentException]
	{
		#Write-Host "Registry Key Property missing" 
	}
	
	if (!$VSCheck) 
	{ 
		#Write-Host "variable is null" 
	}
	else
	{
		Write-Host ($Iter+1) ":Found Visual Studio" $ReadableVersion[$Iter] "AT" $VSCheck
		
		$FoundVS.Add($VSCheck)
		$Iter++
	}
	
}

Write-Host "Please Select One:"

$key = [Console]::ReadKey()