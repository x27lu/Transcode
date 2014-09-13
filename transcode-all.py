import argparse
import glob
import os
import subprocess

def ParseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--format', type=int, required=True)
    parser.add_argument('--threads', type=int)
    parser.add_argument('--output-folder', required=True)
    parser.add_argument('inputfiles', metavar='INPUT FILES', nargs='+')

    args = parser.parse_args()
    return args
    
def GetFormatDetails(format):
    profileKey = "profile"
    levelKey = "level"
    resolutionKey = "resolution"
    if format == 1:
        return {profileKey: "baseline", levelKey: "3.0", resolutionKey: "800:450"}
    if format == 2:
        return {profileKey: "high", levelKey: "3.1", resolutionKey: "960:540"}
    if format == 3:
        return {profileKey: "high", levelKey: "3.2", resolutionKey: "1280:720"}
    
    return None
    
def ProcessFiles(args, format):
    for inputFilePattern in args.inputfiles:
        inputFilesInPattern = glob.glob(inputFilePattern)
        
        # was not glob expression (glob returns empty list for regular filename)
        if not inputFilesInPattern:
            inputFilesInPattern = [inputFilePattern]
        
        for inputFile in inputFilesInPattern:
            if not os.path.isfile(inputFile):
                print("Error - input file '{0}' does not exist, skipping...".format(inputFile))
                continue
            
            arguments = ["python", "transcode.py", "--profile", format["profile"], "--level", format["level"], "--resolution", format["resolution"], "--output-folder", str(args.output_folder), inputFile]
            if args.threads is not None:
                arguments.extend(["--threads", str(args.threads)])
            
            subprocess.call(arguments)
            
            
def main():
    args = ParseArguments()
    #print(args.format)
    #print(args.threads)
    #print(args.output_folder)
    #print(args.inputfiles)
    
    if not os.path.isdir(args.output_folder):
        print("Error - output directory '{0}' does not exist, exitting...".format(args.output_folder))
        exit(1)
        
    format = GetFormatDetails(args.format)
    if format is None:
        print("Error - specified format type '{0}' does not exist, exitting...".format(args.format))
        exit(1)
    
    ProcessFiles(args, format)
    
if __name__ == "__main__" : main()