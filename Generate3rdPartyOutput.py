#!/usr/bin/env python

import subprocess
from zipfile import ZipFile
import sys
import os
import json
import requests
import glob
from awsauth import S3Auth

import argparse

from winreg import *

def str2bool(v):
	if isinstance(v, bool):
		return v
	if v.lower() in ('yes', 'true', 't', 'y', '1'):
		return True
	elif v.lower() in ('no', 'false', 'f', 'n', '0'):
		return False
	else:
		raise argparse.ArgumentTypeError('Boolean value expected.')
		
parser = argparse.ArgumentParser(description='Generate 3rd Party!')
parser.add_argument("--dev", type=str2bool, nargs='?', const=True, default=False, help="Use Dev")
args = parser.parse_args()

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
	
def RunAndWait(ProgramLaunch, LogName=''):
	print("Running {}...".format(ProgramLaunch))
	
	LogFile = None
	
	if LogName != '':
		LogFile = open(LogName + ".log.txt","w")
	
	process = subprocess.Popen(ProgramLaunch, bufsize=2048, shell=True, stdout=subprocess.PIPE, encoding='utf8', close_fds=True)
	while True:
		output = process.stdout.readline()
		if output == '' and process.poll() is not None:
			break
		if output:
			print(output, end = '')
			if LogFile:
				LogFile.write(output)
	rc = process.poll()
	
	if LogFile:
		LogFile.close()
		
	#print("ERROR CODE" + process.returncode) //// hmmm
	
	return "DONE"	

def DownloadFromS3(URL, file_name):

	ACCESS_KEY = 'ACCESS_KEY'
	SECRET_KEY = 'SECRET_KEY'

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
ScriptPath = get_script_path()

print("CMakePath: " + CMakePath)
print("ThirdPartyPath: " + ThirdPartyPath)
print("VSBinPath: " + VSBinPath)

with open('ModulesToBuild.json') as json_file:
	data = json.load(json_file)
	
	if(args.dev):
		data['modules'] = data['modules'] + data['devmodules'] 
	
	for p in data['modules']:
		print('ModuleName: ' + p['ModuleName'])
		print('LocalPath: ' + p['LocalPath'])
		print('CMakeArgs: ' + p['CMakeArgs'])
		print('')
		
		print(os.getcwd())
		os.chdir(p['LocalPath'])
		print(os.getcwd())
		
		OutputPath = ThirdPartyPath + "/" + p['LocalPath']
		CMakeLocalLibInstall = OutputPath + "\\" + CMakeLibInstall
		
		LocalCMakeArgs = p['CMakeArgs'] + " -DThirdPartyPath:PATH=\"" + ThirdPartyPath + "\" -C \"" + ScriptPath + "/CMakeCachePreload.cmake \""
		LocalCMakeArgs = LocalCMakeArgs.replace( "$CMakeVSString", CMakeVSString )
		LocalCMakeArgs = LocalCMakeArgs.replace( "$VSMakeBuildFolder", VSMakeBuildFolder )
		LocalCMakeArgs = LocalCMakeArgs.replace( "$OutputPath", OutputPath )
		LocalCMakeArgs = LocalCMakeArgs.replace( "$CMakeLibInstall", CMakeLibInstall )
		LocalCMakeArgs = LocalCMakeArgs.replace( "\\", "/" )
		LocalCMakeArgs = LocalCMakeArgs.replace( "$3rdPartyForwardPath", ThirdPartyForwardPath )
		LocalCMakeArgs = LocalCMakeArgs.replace( "$CMakeLocalLibInstall", CMakeLocalLibInstall )
		
	
		ExecutionString = CMakePath + " " + LocalCMakeArgs
		print("CMAKE CALL: " + ExecutionString)
		RunAndWait(ExecutionString, "../" + p['ModuleName'] + "_CMAKE" )
		
		SolutionName = None
		SolutionName = glob.glob("./" + VSMakeBuildFolder + "/*.sln")[0]
		
		VSExecutionString = VSBinPath + " " + SolutionName + " /build Release /project INSTALL"
		print("VS CALL: " + VSExecutionString) 
		RunAndWait(VSExecutionString, "../" + p['ModuleName'] + "_BUILD" )
		
		os.chdir("../")
		print('')


