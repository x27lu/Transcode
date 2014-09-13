import argparse
import os
import re
import subprocess

def ParseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', required=True)
    parser.add_argument('--level', required=True)
    parser.add_argument('--resolution', required=True)
    parser.add_argument('--threads', type=int)
    parser.add_argument('--output-folder', required=True)
    parser.add_argument('inputfile', metavar='INPUT FILE', nargs=1)

    args = parser.parse_args()
    return args
    
    
def GetPrettyName(filename):
    filename = re.sub('\([0-9]{3,4}x[0-9]{3,4}[^)]+\)', '', filename)
    filename = re.sub('\([0-9]{3,4}p\)', '', filename)
    filename = re.sub('_', ' ', filename)
    filename = re.sub('[ ]*\[[^[]*\][ ]*', '', filename)
    
    return filename
    
    
def GetAudioTrackIDs(filename):
    output = subprocess.check_output(["mkvmerge", "--identify", filename]).decode("utf-8")
    
    ids = []
    for line in output.splitlines():
        if re.match('Track ID [0-9]{1,2}: audio.*', line):
            ids.append(re.sub('Track ID ', '', re.sub(':.*', '', line)))
    
    return ids
    

def GetVideoTrackIDs(filename):
    output = subprocess.check_output(["mkvmerge", "--identify", filename]).decode("utf-8")
    
    ids = []
    
    for line in output.splitlines():
        if re.match('Track ID [0-9]{1,2}: video.*', line):
            ids.append(re.sub('Track ID ', '', re.sub(':.*', '', line)))
    
    return ids
    
    
def TranscodeFile(args):
    tempOutputVideoFile = "{0}{1}{2}.transcode.avi".format(args.output_folder, os.sep, os.path.basename(args.inputfile[0]))
    
    arguments = ["mencoder", args.inputfile[0], "-nosound", "-ass", "-ovc", "x264", "-x264encopts", "preset=slower:profile={0}:level={1}:threads={2}:ref=3".format(args.profile, args.level, args.threads if args.threads is not None else "auto"), "-vf", "scale={0}".format(args.resolution), "-o", tempOutputVideoFile]
    
    subprocess.call(arguments)
    
    prettyFileName = GetPrettyName(os.path.basename(args.inputfile[0]))
    
    audioTrackIDs = GetAudioTrackIDs(args.inputfile[0])
    if not audioTrackIDs:
        print("Error - cannot find any audio tracks, exitting...")
        exit(1)
    
    videoTrackIDs = GetVideoTrackIDs(tempOutputVideoFile)
    if not videoTrackIDs:
        print("Error - cannot find any video tracks, exitting...")
        exit(1)
    
    audioTrackID = audioTrackIDs[0]
    videoTrackID = videoTrackIDs[0]
    
    arguments = ["mkvmerge", "-o", "{0}{1}{2}".format(args.output_folder, os.sep, prettyFileName), "--compression", "{0}:none".format(videoTrackID), "-d", videoTrackID, "-A", "-S", "-T", "--no-global-tags", "--no-chapters", "(", tempOutputVideoFile, ")", "--compression", "{0}:none".format(audioTrackID), "-a", audioTrackID, "--no-attachments", "-D", "-S", "-T", "--no-global-tags", "(", args.inputfile[0], ")", "--track-order", "0:{0},1:{1}".format(videoTrackID, audioTrackID), "--title", re.sub('.mkv$', '', prettyFileName)]
    
    subprocess.call(arguments)
    
    
def main():
    args = ParseArguments()
    
    if not os.path.isdir(args.output_folder):
        print("Error - output directory '{0}' does not exist, exitting...".format(args.output_folder))
        exit(1)
        
    if not os.path.isfile(args.inputfile[0]):
        print("Error - input file '{0}' does not exist, exitting...".format(inputFile))
        exit(1)
    
    TranscodeFile(args)
    

if __name__ == "__main__" : main()