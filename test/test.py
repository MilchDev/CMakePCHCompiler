import subprocess
import unittest
import platform
import shutil
import os
import time

bHasCMake = shutil.which("cmake") != None
bTestMSVC = platform.system() == 'Windows'and shutil.which("cl") != None
bTestGCC = shutil.which("g++") != None
bHasNinja = shutil.which("ninja") != None

def cleanTempDir():
  sTempDir = getTempDir()
  if os.path.isdir(sTempDir): shutil.rmtree(sTempDir)
  os.makedirs(sTempDir)
  return sTempDir

def getTempDir():
  return os.path.join(os.getcwd(),"tmp")

#Setups the project with the specified generator & flags in an temp directory
def setupCMake(sProject,sGenerator,sFlags):
  sCMakeDir = os.path.join(getTempDir(),"cmake")

  sProjectDir = os.path.join(getTempDir(),"project")
  shutil.copytree(sProject,sProjectDir,copy_function=shutil.copy)

  os.makedirs(sCMakeDir,exist_ok=True)
  os.makedirs(sProjectDir,exist_ok=True)
  
  sOriginalProjectAbs = os.path.abspath(sProject).replace(os.sep, '/')
  os.chdir(sCMakeDir)
  sCommand = "cmake -G \"%s\" %s -DORIGINAL_SOURCE_DIR=\"%s\" \"%s\"" % (sGenerator,sFlags,sOriginalProjectAbs,sProjectDir)
  print("setupCMake command: %s" % sCommand)
  aCompleteProcess = subprocess.run(sCommand,check=True)
  return (sCMakeDir,sProjectDir)

def buildCMake(sCMakeDir):
  sCommand = "cmake --build \"%s\"" % (sCMakeDir)
  print("buildCMake command: %s" % sCommand)
  aCompleteProcess = subprocess.run(sCommand)
  #print(aCompleteProcess.stdout)
  return aCompleteProcess.returncode

#Preserves the initial directory between tests
class BaseTest(unittest.TestCase):
  _sOriginalDir = ""

  def setUp(self):
    cleanTempDir()
    self._sOriginalDir = os.getcwd()

  def tearDown(self):
    os.chdir(self._sOriginalDir)

  def project1(self,bUsePCH,sGenerator):
    if bUsePCH:
      sFlags = "-DUSE_PRECOMPILED=1"
    else:
      sFlags = ""

    (sCMakeDir,sProjectDir) = setupCMake("testproject1",sGenerator,sFlags)
    self.assertEqual(buildCMake(sCMakeDir),0)

    #Clear the file
    time.sleep(1) #It seems like ninja is taking into account the file timestamp, dont be too fast!
    sHeader2 = os.path.join(sProjectDir,"header2.h")
    print("Cleaning file %s " % sHeader2)
    aFile = open(sHeader2,"w")
    aFile.write('\n')
    aFile.close()

    #Try to build (expect failure)
    print("Building again %s " % sCMakeDir)
    self.assertTrue(buildCMake(sCMakeDir) != 0)

    #Add to file again
    with open(sHeader2, 'w') as aFile:
      aFile.write('#define RET_VALUE 1\n')

    #Build again
    print("Building again %s " % sCMakeDir)
    self.assertTrue(buildCMake(sCMakeDir) == 0)

@unittest.skipIf(bTestMSVC == False,"Platform not windows or cl not present in path")
class TestMSVC(BaseTest):

  @unittest.skipIf(bHasNinja == False,"Ninja not in present in path")
  def test_ninja_pch(self):
     super().project1(True,"Ninja")

  @unittest.skipIf(bHasNinja == False,"Ninja not in present in path")
  def test_ninja(self):
      super().project1(False,"Ninja")

  def test_sln(self):
      super().project1(False,"Visual Studio 15 2017")

  def test_sln_pch(self):
      super().project1(True,"Visual Studio 15 2017")

@unittest.skipIf(bTestGCC == False,"g++ not present in path")
class TestGCC(BaseTest):

  @unittest.skipIf(bHasNinja == False,"Ninja not in present in path")
  def test_ninja_pch(self):
     super().project1(True,"Ninja")

  @unittest.skipIf(bHasNinja == False,"Ninja not in present in path")
  def test_ninja(self):
      super().project1(False,"Ninja")

if __name__ == '__main__':
    print("Env:")
    print("- bHasCMake: %s" % bHasCMake)
    print("- bTestMSVC: %s" % bTestMSVC)
    print("- bTestGCC: %s" % bTestGCC)
    print("- bHasNinja: %s" % bHasNinja)
    print("Running the tests in %s" % os.getcwd())

    if bTestGCC and bTestMSVC:
      print("MSVC and GCC in path, not allowed! (CMake strongly prefers MSVC)")
      exit(-1)

    print("----------------------------------------------------------------------")

    if not bHasCMake: 
      print("CMake needs to be in path to run any tests!")
      exit(1)
    if not bTestMSVC: 
      print("Skipping MSVC tests - either platform not windows or cl not in PATH!")
    try:
      unittest.main()
    except:
      print("Exception")