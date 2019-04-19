$OutputPath = $3rdPartyPath + "\" + $CurrentModule
Write-Host "MODULE CMAKE MODULE: " $ModulePath "OUTPUT TO" $OutputPath

# run the process
Start-Process $CMakePath -ArgumentList "-G `"$CMakeVSString`" -B$VSMakeBuildFolder -Hsource -DCMAKE_INSTALL_PREFIX=`"$OutputPath`" -DCMAKE_INSTALL_LIBDIR=`"$CMakeLibInstall`" -DBUILD_EXAMPLES=false -DBUILD_TESTING=false -DSUITESPARSE=true -DSuiteSparse_DIR=`"$3rdPartyForwardPath/suitesparse`" -DGLOG_INCLUDE_DIR_HINTS=`"$3rdPartyForwardPath/glog/include`" -DGLOG_LIBRARY_DIR_HINTS=`"$3rdPartyForwardPath/glog/$CMakeLibInstall`" -DEigen3_DIR=`"$3rdPartyForwardPath/eigen`" " -Wait