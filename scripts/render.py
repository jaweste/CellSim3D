import bpy
import csv
import sys
import os
import argparse
import numpy as np

sys.path.append("/home/pranav/dev/celldiv/scripts")
import celldiv


argv = sys.argv

if "--" not in argv:
    print("ERROR: No arguments provided to script")
    sys.exit(80)
else:
    a = argv.index("--")
    argv = argv[a + 1:]

helpString = """
Run as:
blender --background --python %s --
[options]
""" % __file__

parser = argparse.ArgumentParser(description=helpString)

parser.add_argument("trajPath", type=str,
                    help="Trajectory path. Absolute or relative.")

parser.add_argument("-s", "--smooth", type=bool, required=False,
                    help="Do smoothing (really expensive and doesn't look as good)",
                    default=False)

parser.add_argument("-k", "--skip", type=int, required=False,
                    help="Trajectory frame skip rate. E.g. SKIP=10 will only \
                    render every 10th frame.",
                    default=1)

parser.add_argument("-nc", "--noclear", type=bool, required=False,
                    help="specifying this will not clear the destination directory\
                    and restart rendering.",
                    default=False)

parser.add_argument("--min-cells", type=int, required=False,
                    help='Start rendering when system has at least this many cells',
                    default=1)

parser.add_argument("--inds", type=int, required=False, nargs='+',
                    help="Only render cells with these indices",
                    default=[])

parser.add_argument("-nf", "--num-frames", type=int, required=False,
                    help="Only render these many frames.",
                    default=sys.maxsize)

args = parser.parse_args(argv)

imageindex = 0
firstfaces = []
bpy.data.worlds["World"].horizon_color=[0.051, 0.051, 0.051]
bpy.data.scenes["Scene"].render.alpha_mode='SKY'

doSmooth = args.smooth
if doSmooth:
    print("Doing smoothing. Consider avoiding this feature...")

with open('C180_pentahexa.csv', newline='') as g:
    readerfaces = csv.reader(g, delimiter=',')
    for row in readerfaces:
        firstfaces.append([int(v) for v in row])


filename = os.path.realpath(args.trajPath)
basename = os.path.splitext(filename)[0] + "/images/CellDiv_"

nSkip = args.skip

if nSkip > 1:
    print("Skipping over every %dth" % nSkip, "frame...")


noClear = args.noclear

sPath = os.path.splitext(filename)[0] + "/images/"

if not noClear and os.path.exists(sPath):
    for f in os.listdir(sPath):
        os.remove(sPath+f)

cellInds = []
minInd = args.min_cells - 1
if len(args.inds) > 0:
    minInd = max(minInd, min(args.inds))

stopAt = args.num_frames

with celldiv.TrajHandle(filename) as th:
    frameCount = 1
    try:
        for i in range(int(th.maxFrames/nSkip)):

            f = th.ReadFrame(inc=nSkip)

            if len(f) < minInd+1:
                print("Only ", len(f), "cells in frame ", th.currFrameNum,
                      " skipping...")
                continue

            if len(args.inds) > 0:
                f = [f[a] for a in args.inds]

            f = np.vstack(f)
            faces = []
            for mi in range(int(len(f)/192)):
                for row in firstfaces:
                    faces.append([(v+mi*192) for v in row])


            mesh = bpy.data.meshes.new('cellMesh')
            ob = bpy.data.objects.new('cellObject', mesh)

            bpy.context.scene.objects.link(ob)
            mesh.from_pydata(f, [], faces)
            mesh.update()

            if doSmooth:
                bpy.ops.object.select_by_type(type='MESH')
                bpy.context.scene.objects.active = bpy.data.objects['cellObject']
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.normals_make_consistent(inside=False)
                bpy.ops.object.editmode_toggle()
                bpy.ops.object.shade_smooth()
                bpy.context.scene.objects.active = bpy.data.objects['Cube']
                bpy.ops.object.make_links_data(type='MATERIAL')             # copy material from Cube
                bpy.context.scene.objects.active = bpy.data.objects['cellObject']
                bpy.ops.object.select_all(action='TOGGLE')
                bpy.ops.object.modifier_add(type='SUBSURF')

            imagename = basename + "%d.png" % frameCount
            frameCount += 1
            bpy.context.scene.render.filepath = imagename

            bpy.ops.render.render(write_still=True)  # render to file

            bpy.ops.object.select_pattern(pattern='cellObject')
            bpy.ops.object.delete()                                     # delete mesh...
            if frameCount > stopAt:
                break

    except celldiv.IncompleteTrajectoryError:
        print ("Stopping...")
