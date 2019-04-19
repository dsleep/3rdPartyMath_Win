$OutputPath = $3rdPartyPath + "\" + $CurrentModule
Write-Host "BUILDING MODULE: " $ModulePath "OUTPUT TO" $OutputPath
# run the process
Start-Process $CMakePath -ArgumentList "-G `"$CMakeVSString`" -B$VSMakeBuildFolder -Hsource -DCMAKE_INSTALL_PREFIX=`"$OutputPath`" -DCMAKE_INSTALL_LIBDIR=`"$CMakeLibInstall`" " -Wait