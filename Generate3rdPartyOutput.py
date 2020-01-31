#!/usr/bin/env python

import subprocess
from zipfile import ZipFile
import sys
import os
import json
import requests
import glob
from awsauth import S3Auth

from winreg import *

def get_VS_installs():
	VSInstalls = dict()

	k1 = OpenKey(HKEY_LOCAL_MACHINE, r'SOFTWARE\Wow6432Node\Microsoft\VisualStudio\SxS\VS7')

	i = 0
	while 1:
		try:
			vname, value, vtype =  EnumValue(k1, i)
			
			print(vname)
			VSInstalls[vname] = value
	
			i += 1
		except WindowsError:
			break

	CloseKey(k1)

	return VSInstalls 
	
def get_script_path():
    return os.path.dirname(os.path.realpath(__file__))
	
def which(program):

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None
	
def RunAndWait(ProgramLaunch):
	print("Running {}...".format(ProgramLaunch))
	process = subprocess.Popen(ProgramLaunch, bufsize=2048, shell=True, stdout=subprocess.PIPE, encoding='utf8', close_fds=True)
	while True:
		output = process.stdout.readline()
		if output == '' and process.poll() is not None:
			break
		if output:
			print(output, end = '')
	rc = process.poll()
	return "DONE"	

def DownloadFromS3(URL, file_name):

	ACCESS_KEY = 'AKIAQPDYDEOB3AUKT3OO'
	SECRET_KEY = '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' 

	with open(file_name, "wb") as f:
		print("Downloading %s" %(URL))
		response = requests.get(URL, auth=S3Auth(ACCESS_KEY, SECRET_KEY), stream=True)
		total_length = response.headers.get('content-length')

		if total_length is None: # no content length header
			f.write(response.content)
		else:
			dl = 0
			total_length = int(total_length)
			for data in response.iter_content(chunk_size=(1 * 1024 * 1024)):
				dl += len(data)
				f.write(data)
				done = int(50 * dl / total_length)
				sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )    
				sys.stdout.flush()
				
def DownloadAndInstall(URL, file_name):

	with open(file_name, "wb") as f:
		print("Downloading %s" %(URL))
		response = requests.get(URL, stream=True)
		total_length = response.headers.get('content-length')

		if total_length is None: # no content length header
			f.write(response.content)
		else:
			dl = 0
			total_length = int(total_length)
			for data in response.iter_content(chunk_size=(1 * 1024 * 1024)):
				dl += len(data)
				f.write(data)
				done = int(50 * dl / total_length)
				sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )    
				sys.stdout.flush()
				
	RunAndWait(file_name);
	
print("Looking for git.exe.....")	
print(which("git.exe"))
print("Looking for svn.exe.....")
print(which("svn.exe"))
print("Looking for node.exe.....")
print(which("node.exe"))
print("Looking for NASM.exe.....")
print(which("NASM.exe"))

if which("NASM.exe") == None:
	DownloadAndInstall("https://www.nasm.us/pub/nasm/releasebuilds/2.14.02/win64/nasm-2.14.02-installer-x64.exe", "nasm-2.14.02-installer-x64.exe")	
if which("git.exe") == None:
	DownloadAndInstall("https://github.com/git-for-windows/git/releases/download/v2.25.0.windows.1/Git-2.25.0-64-bit.exe", "Git-2.25.0-64-bit.exe")
if which("svn.exe") == None:
	DownloadAndInstall("https://osdn.net/frs/redir.php?m=plug&f=%2Fstorage%2Fg%2Ft%2Fto%2Ftortoisesvn%2F1.13.1%2FApplication%2FTortoiseSVN-1.13.1.28686-x64-svn-1.13.0.msi", "TortoiseSVN-1.13.1.28686-x64-svn-1.13.0.msi")	
if which("node.exe") == None:
	DownloadAndInstall("https://nodejs.org/dist/v12.14.1/node-v12.14.1-x64.msi", "node-v12.14.1-x64.msi")

VSVersions = [ "15.0", "16.0" ]
VSBuildS = [ "-G \"Visual Studio 15 2017 Win64\"", "-G \"Visual Studio 16 2019\" -A x64" ]


VSInstallMap = get_VS_installs()

		
print("Which Visual Studio?");
print("[1] 2017");
print("[2] 2019");
VSVersion = int(input('[1-2]?'))
ActiveZip = None
DeleteExisting = False

#kinda ugly using that readable string as the cmake vs arguemnt
# $VSBinPath = $FoundVS[$SelectionIndex] + "Common7\IDE\devenv.com"

CMakeVSString = None
CMakeLibInstall = None
VSMakeBuildFolder = None
VSBinPath = None

		
if VSVersion == 1:	
	CMakeVSString = "Visual Studio 15 2017 Win64"
	CMakeLibInstall = "lib/win64/vc15"
	VSMakeBuildFolder = "buildVS2017"
if VSVersion == 2:
	CMakeVSString = "Visual Studio 16 2019\" -A \"x64"
	CMakeLibInstall = "lib/win64/vc16"
	VSMakeBuildFolder = "buildVS2019"

VSBinPath = "\"" + VSInstallMap[ VSVersions[VSVersion - 1 ] ] + "Common7\IDE\devenv.com" + "\""
CMakePath = "\"C:\\Program Files\\CMake\\bin\\cmake.exe\""
ThirdPartyPath = os.path.abspath( "..\\3rdParty")
ThirdPartyForwardPath = ThirdPartyPath.replace( "\\", "/" )

print("CMakePath: " + CMakePath)
print("ThirdPartyPath: " + ThirdPartyPath)
print("VSBinPath: " + VSBinPath)

with open('ModulesToBuild.json') as json_file:
	data = json.load(json_file)
	for p in data['modules']:
		print('ModuleName: ' + p['ModuleName'])
		#print('LocalPath: ' + p['LocalPath'])
		#print('CMakeArgs: ' + p['CMakeArgs'])
		print('')
		
		print(os.getcwd())
		os.chdir(p['LocalPath'])
		print(os.getcwd())
		
		OutputPath = ThirdPartyPath + "/" + p['LocalPath']
		CMakeLocalLibInstall = OutputPath + "\\" + CMakeLibInstall
		
		LocalCMakeArgs = p['CMakeArgs']
		LocalCMakeArgs = LocalCMakeArgs.replace( "$CMakeVSString", CMakeVSString )
		LocalCMakeArgs = LocalCMakeArgs.replace( "$VSMakeBuildFolder", VSMakeBuildFolder )
		LocalCMakeArgs = LocalCMakeArgs.replace( "$OutputPath", OutputPath )
		LocalCMakeArgs = LocalCMakeArgs.replace( "$CMakeLibInstall", CMakeLibInstall )
		LocalCMakeArgs = LocalCMakeArgs.replace( "\\", "/" )
		LocalCMakeArgs = LocalCMakeArgs.replace( "$3rdPartyForwardPath", ThirdPartyForwardPath )
		LocalCMakeArgs = LocalCMakeArgs.replace( "$CMakeLocalLibInstall", CMakeLocalLibInstall )
	
		ExecutionString = CMakePath + " " + LocalCMakeArgs
		print("CMAKE CALL: " + ExecutionString)
		RunAndWait(ExecutionString)
		
		SolutionName = None
		SolutionName = glob.glob("./" + VSMakeBuildFolder + "/*.sln")[0]
		
		VSExecutionString = VSBinPath + " " + SolutionName + " /build Release /project INSTALL"
		print("VS CALL: " + VSExecutionString) 
		RunAndWait(VSExecutionString)
		
		os.chdir("../")
		print('')

print("Checking 3rd Party Directory...")

# if os.path.exists("../3rdParty"):
	# print("3rd Party Exists")
	# YesNo = input('Delete exisitng (y/n)?')
	# if YesNo == 'y' or YesNo == 'Y':
		# DeleteExisting = True
# else:
	# DeleteExisting = True

# if DeleteExisting:
	# print("Preparing 3rd Party")
	
	# # Downloading a file
	# if VSVersion == 1:
		# DownloadFromS3("https://sleepingrobot-storage.s3.amazonaws.com/3rdParty_VS2017.zip", "3rdParty_VS2017.zip")
		# ActiveZip = "3rdParty_VS2017.zip"
	# if VSVersion == 2:
		# DownloadFromS3("https://sleepingrobot-storage.s3.amazonaws.com/3rdParty_VS2019.zip", "3rdParty_VS2019.zip")
		# ActiveZip = "3rdParty_VS2019.zip"
	
	# # Create a ZipFile Object and load sample.zip in it
	# if ActiveZip != None:
		# with ZipFile(ActiveZip, 'r') as zipObj:
			# zipObj.extractall('.')	 	

# not needed
# print(RunAndWait("git.exe clone https://github.com/dsleep/3rdPartyMath_Win.git --recursive"))
#print(RunAndWait("svn.exe checkout https://216.31.112.136/svn/RedRiverDrone/trunk RedRiverDrone/src"))


# Start-Process $CMakePath -ArgumentList "-G `"$CMakeVSString`" -B$VSMakeBuildFolder -Hsource -DCMAKE_INSTALL_PREFIX=`"$OutputPath`" -DCMAKE_INSTALL_LIBDIR=`"$CMakeLibInstall`" -DBUILD_METIS=false" -Wait

#Write-Host "SOLUTION NAME: $VSMakeBuildFolder\$SolutionName" 
#		Start-Process $VSBinPath -ArgumentList "$VSMakeBuildFolder\$SolutionName /build Release /project INSTALL" -Wait

# print(RunAndWait("svn.exe checkout https://216.31.112.136/svn/QExperiments/trunk/Intelliflow_CesiumJS/trunk Intelliflow_CesiumJS"))
# print(RunAndWait("svn.exe checkout https://216.31.112.136/svn/IntelliFlow/trunk IntelliFlow/src"))print(RunAndWait("svn.exe checkout https://216.31.112.136/svn/IntelliFlow/trunk IntelliFlow/src"))

#need to find this path...

#RunAndWait("\"{}\" {} -BSuiteBuild".format(CMakePath, VSBuildS[VSVersion-1] ))
