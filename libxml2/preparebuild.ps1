$OutputPath = $3rdPartyPath + "\" + $CurrentModule
Write-Host "BUILDING MODULE: " $ModulePath "OUTPUT TO" $OutputPath
# run the process
Start-Process $CMakePath -ArgumentList "-G `"$CMakeVSString`" -B$VSMakeBuildFolder -Hsource -DCMAKE_INSTALL_PREFIX=`"$OutputPath`" -DCMAKE_INSTALL_INCLUDEDIR=`"$OutputPath/include`" -DCMAKE_INSTALL_LIBDIR=`"$CMakeLibInstall`" -DLIBICONV_INCLUDE_DIR=`"$3rdPartyForwardPath/libiconv/include`" -DLIBICONV_LIBRARY=`"$3rdPartyForwardPath/libiconv/$CMakeLibInstall`" " -Wait