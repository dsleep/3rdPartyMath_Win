


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

Write-Host "Selected" $key.Value

$SubModules = "eigen", "glog", "libiconv", "libxml2", "suitesparse", "opencv", "suitesparse"

$3rdPartyPath = Resolve-Path -Path "..\3rdParty" 

Write-Host "***** 3rd Party Path Installation Path: " $3rdPartyPath

#"C:\Program Files\CMake\bin\cmake.exe" -G "Visual Studio 15 2017 Win64" -BbuildVS2017 -Hsource -DCMAKE_INSTALL_PREFIX="D:/SFM4S/3rdParty/glog" -DCMAKE_INSTALL_LIBDIR="lib/win64/vc15" 

foreach ($SubModule in $SubModules)
{
	Write-Host "CREATING PROJECT FOR:" $SubModule
	
	Push-Location
	Set-Location ./$SubModule
		
	$ModulePath = (Resolve-Path -Path ".").Path 
	$ModulePath = $ModulePath + "\preparebuild.ps1"
	
	Write-Host "-> Running Script" $ModulePath
	
#	Start-Process -FilePath "C:\Program Files\CMake\bin\cmake.exe" -ArgumentList "/c dir `"%systemdrive%\program files`""
	
	#Invoke-Command -FilePath $ModulePath
	#Invoke-Command -ComputerName . -FilePath "D:\SFM4S\3rdPartyMath_Win\eigen\preparebuild.ps1"

	& $ModulePath 
	
	Pop-Location
}

