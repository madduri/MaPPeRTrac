from sys import argv
from os.path import exists,join,split,splitext,abspath
from os import system,mkdir,remove,environ,chmod
import stat
from shutil import *
from glob import glob
from tempfile import *
from utilities import *

if len(argv) < 4:
    print "Usage: %s <source.nii.gz>:<target.nii.gz> <root-dir> <bedpost-dir> <output-dir>"
    exit(0)

seed = argv[1].split(":")[0]
seed_name = splitext(splitext(split(seed)[1])[0])[0]
target = argv[1].split(":")[1]
target_name = splitext(splitext(split(target)[1])[0])[0]

root_dir = argv[2]
bedpost_dir = argv[3]
output_dir = argv[4]

tmp_dir = mkdtemp()

fsl = join(environ['FSLDIR'],"bin")

copy(seed,tmp_dir)
copy(target,tmp_dir)
copy(join(root_dir,"EDI","terminationmask.nii.gz"),tmp_dir)
chmod(join(tmp_dir,"terminationmask.nii.gz"),stat.S_IWUSR | stat.S_IRUSR | stat.S_IXUSR)

copy(join(root_dir,"EDI","allvoxelscortsubcort.nii.gz"),tmp_dir)

copy(join(root_dir,"EDI","bs.nii.gz"),join(tmp_dir,"brainstemplate.nii.gz"))
chmod(join(tmp_dir,"brainstemplate.nii.gz"),stat.S_IWUSR | stat.S_IRUSR | stat.S_IXUSR)

copytree(bedpost_dir,join(tmp_dir,"bedpostx"))



# Creating the masks
run("fslmaths"," %s -sub %s %s" % (join(tmp_dir,"allvoxelscortsubcort.nii.gz"),
                                   join(tmp_dir,split(seed)[1]),
                                   join(tmp_dir,"exclusion.nii.gz")))

run("fslmaths", " %s -sub %s %s" % (join(tmp_dir,"exclusion.nii.gz"),
                                                join(tmp_dir,split(target)[1]),
                                                join(tmp_dir,"exclusion.nii.gz")))

run("fslmaths", " %s -add %s %s" % (join(tmp_dir,"exclusion.nii.gz"),
                                                join(tmp_dir,split(seed)[1]),
                                                join(tmp_dir,"brainstemplate.nii.gz")))

run("fslmaths", " %s -add %s %s" % (join(tmp_dir,"terminationmask.nii.gz"),
                                                join(tmp_dir,split(target)[1]),
                                                join(tmp_dir,"terminationmask.nii.gz")))

waypoint = open(join(tmp_dir,"waypoint.txt"),"w")
waypoint.write(target + "\n")
waypoint.close()


arguments = (" -x %s " % join(tmp_dir,split(seed)[1])
    + " --pd -l -c 0.2 -S 2000 --steplength=0.5 -P 1000"
    + " --waypoints=%s" % join(tmp_dir,"waypoint.txt")
    + " --avoid=%s" % join(tmp_dir,"exclusion.nii.gz")
    + " --stop=%s" % join(tmp_dir,"terminationmask.nii.gz")
    + " --forcedir --opd"
    + " -s %s" % join(tmp_dir,"bedpostx","merged")
    + " -m %s" % join(tmp_dir,"bedpostx","nodif_brain_mask.nii.gz")
    + " --dir=%s" % tmp_dir
    + " --out=%sto%s.nii.gz" % (seed_name,target_name)
    )

run("probtrackx2",arguments)
copy(join(tmp_dir,"%sto%s.nii.gz" % (seed_name,target_name)),output_dir)

rmtree(tmp_dir)


