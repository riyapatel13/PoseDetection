# Pose Detection

This repo contains code to perform pose detection on video clips. This was created as part of an ongoing research project at Carnegie Mellon Human-Computer Interaction Institute under Dr. Nik Martelaro - for more information about the study, visit <b>link</b>. The project is aimed at assisting user researchers in analyzing large amounts of qualitative data that humans are typically tasked with. Specifically, my role was concerned with developing and using off-the-shelf machine learning tools to perform computational analysis on data such as human speech and movements. 

## Files Included 
* data  
  * videos
    * 2020-03-03_IKEA-DRIVE_CLIP.mp4 - video of 1 driver and 2 passengers from 4 different camera views
    * output.mp4 - same video of 1 driver and 2 passengers with only 1 camera view and frame numbers on the bottom left
    * skeleton.mp4 - output.mp4 with skeleton detection from running through OpenPose
  * driving_frames
    * Folder containing photos of each individual skeleton frame from skeleton.mp4 (mostly used for debugging purposes)
  * driving_jsons
    * Folder containing JSON files with pose data of each skeleton frame from skeleton.mp4

## Process


## Running Code
Need to create a requirements.txt 
