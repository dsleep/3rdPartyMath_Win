$OutputPath = $3rdPartyPath + "\" + $CurrentModule
Write-Host "BUILDING MODULE: " $ModulePath "OUTPUT TO" $OutputPath
# run the process
Start-Process $CMakePath -ArgumentList "-G `"$CMakeVSString`" -B$VSMakeBuildFolder -Hsource -DCMAKE_INSTALL_PREFIX=`"$OutputPath`" -DLIB_INSTALL_DIR=`"$CMakeLibInstall`"" -Wait