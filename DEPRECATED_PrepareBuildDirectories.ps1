

#Selection Arrays only 2015, 2017, 2019
$VersionArray = "14.0", "15.0", "16.0"
$ReadableVersion = "Visual Studio 14 2015 Win64", "Visual Studio 15 2017 Win64", "Visual Studio 16 2019`" -A `"x64"
$VSLibSubFolders = "vc14", "vc15", "vc16"
$VSBuildSubFolder = "buildVS2015", "buildVS2017", "buildVS2019"

#need to find this path
$CMakePath = "C:\Program Files\CMake\bin\cmake.exe"

If(!(test-path $CMakePath -PathType Leaf))
{
	Write-Host "Could not find cmake please update CMakePath in PrepareBuildDirectories.ps1"
	Exit
}
else
{
	Write-Host "Found CMake"
}

Write-Host "----------------------------------"
Write-Host "This Will Prepare the 3rd Party Build Directories"
Write-Host "Based on the desired Visual Studio Version you have"
Write-Host "----------------------------------"

Write-Host "----------------------------------"
Write-Host "Listing Visual Studio Installs..."
Write-Host "----------------------------------"


$FoundVS = New-Object System.Collections.Generic.List[System.Object]
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
	
	if ( !$VSCheck) 
	{ 
		Write-Host ($Iter+1) ":Did not find" $ReadableVersion[$Iter] 
		$FoundVS.Add("NOT FOUND")
		$Iter++
	}
	else
	{
		Write-Host ($Iter+1) ":Found Visual Studio" $ReadableVersion[$Iter] "AT" $VSCheck		
		$FoundVS.Add($VSCheck)
		$Iter++
	}
	
}

$key = Read-Host -Prompt 'Please Select One'
$SelectionIndex = ([int]$key) - 1
#Write-Host "Selected Index" $SelectionIndex

#kinda ugly using that readable string as the cmake vs arguemnt
$CMakeVSString = $ReadableVersion[$SelectionIndex]
$CMakeLibInstall = "lib/win64/" + $VSLibSubFolders[$SelectionIndex]
$VSMakeBuildFolder = $VSBuildSubFolder[$SelectionIndex]
$VSBinPath = $FoundVS[$SelectionIndex] + "Common7\IDE\devenv.com"

Write-Host "=== VISUAL STUDIO BUILD INFO =====" $key.Value
Write-Host "VS Exeuction Path:" $VSBinPath
Write-Host "CMake VS Param:" $CMakeVSString
Write-Host "CMake VS LibInstall Param:" $CMakeLibInstall
Write-Host "CMake Build Ouput Folder: " $VSMakeBuildFolder


#Could use Issues of build order though
#$SubModules = Get-ChildItem | ?{ $_.PSIsContainer } | % { $_.Name }
$SubModules = "eigen", "gflags", "glog", "libiconv", "libxml2", "opencv", "suitesparse", "ceres", "libjpeg-turbo"
#$SubModules = "libjpeg-turbo"

#make 3rd party path
$Verify3rdParty = "..\3rdParty"
If(!(test-path $Verify3rdParty))
{
      New-Item -ItemType Directory -Force -Path $Verify3rdParty
}
$3rdPartyPath = (Resolve-Path -Path "..\3rdParty").Path
$3rdPartyForwardPath = $3rdPartyPath -replace "\\", "/"

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

