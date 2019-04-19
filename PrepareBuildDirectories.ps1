


$VersionArray = "14.0", "15.0"
$ReadableVersion = "Visual Studio 14 2015 Win64", "Visual Studio 15 2017 Win64"

$FoundVS = New-Object System.Collections.Generic.List[System.Object]

$CMakePath = "C:\Program Files\CMake\bin\cmake.exe"

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

$CMakeVSString = "Visual Studio 15 2017 Win64"
$CMakeLibInstall = "lib/win64/vc15"
$VSMakeBuildFolder = "buildVS2017"
$VSBinPath = $FoundVS[([int]$key.Value) - 1] + "Common7\IDE\devenv.com"

#Could use Issues of build order though
#$SubModules = Get-ChildItem | ?{ $_.PSIsContainer } | % { $_.Name }
#$SubModules = "eigen", "glog", "libiconv", "libxml2", "opencv", "suitesparse", "ceres"
$SubModules = "eigen", "glog", "libiconv", "libxml2", "opencv", "suitesparse"

$3rdPartyPath = (Resolve-Path -Path "..\3rdParty").Path

Write-Host "***** 3rd Party Path Installation Path: " $3rdPartyPath
Write-Host "***** SubModules to build: " $SubModules

foreach ($SubModule in $SubModules)
{
	Write-Host "CREATING PROJECT FOR:" $SubModule
	
	Push-Location
	Set-Location ./$SubModule
	
	$CurrentModule = $SubModule
		
	$ModulePath = (Resolve-Path -Path ".").Path 
	$ModulePath = $ModulePath + "\preparebuild.ps1"
	
	Write-Host "-> Running Script" $ModulePath	

	Try
	{
		& $ModulePath 
		
		#build install solution
		$SolutionName = (Get-ChildItem $VSMakeBuildFolder -Filter *.sln | Select-Object -First 1).Name
		Write-Host "SOLUTION NAME: $VSMakeBuildFolder\$SolutionName" 
		Start-Process $VSBinPath -ArgumentList "$VSMakeBuildFolder\$SolutionName /build Release /project INSTALL" -Wait
	}
	Catch [System.Management.Automation.CommandNotFoundException]
	{
		Write-Host "NO BUILD SCRIPT AT " + $ModulePath	
	}
	
	Pop-Location
}

