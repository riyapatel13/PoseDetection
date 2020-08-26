# Pose Detection

This repo contains code to perform pose detection on video clips. This was created as part of an ongoing research project at Carnegie Mellon Human-Computer Interaction Institute under Dr. Nik Martelaro. The project is aimed at assisting user researchers in analyzing large amounts of qualitative data that humans are typically tasked with. Specifically, my role was concerned with developing and using off-the-shelf machine learning tools to perform computational analysis on data such as human speech and movements. 

## Files Included 
* data  
  * videos
    * 2020-03-03_IKEA-DRIVE_CLIP.mp4 - video of 1 driver and 2 passengers from 4 different camera views
    * output.mp4 - same video of 1 driver and 2 passengers with only 1 camera view and frame numbers on the bottom left
    * skeleton.mp4 - output.mp4 with skeleton detection from running through OpenPose
  * driving_frames
    * Folder containing photos of first 1000 individual skeleton frame from skeleton.mp4 (mostly used for debugging purposes)
  * driving_jsons
    * Folder containing JSON files with pose data of first 1000 skeleton frames from skeleton.mp4
  * annotated_driving.xml
    * XML file containing information on bounding rectangles used for analysis
  * left_wrist.csv
    * CSV file containing location of driver's left wrist in first 1000 frames (mostly used for viewing purposes)
  * right_wrist.csv
    * CSV file containing location of driver's right wrist in first 1000 frames (mostly used for viewing purposes)
* images
  * Images used in README
* hand_detect.py
  * File containg code for determining when the driver's hand is off the wheel using output.mp4 (in data) as reference.
* hand_detect_res.txt
  * Results of hand_detect.py on output.mp4
  * Contains JSON objects of times when hand was off the wheel in the following format: ```{"event": "left/right hand off wheel", "start": <start time>, "end": <end time>}```


## Process
The overall goal is to be able to identify poses that are deemed "interesting" by the user researcher. In the context of driving, this includes when a driver's hands are off the wheel, when they adjust their mirrors, etc. I focused on identifying when the driver is not placing their hands on the wheel. First, I started with a video clip of 4 different camera views of the driver (2020-03-03_IKEA-DRIVE_CLIP.mp4). I cropped it to one view and added frame numbers using [FFmpeg](https://ffmpeg.org/) (output.mp4). Then, I ran this new video through [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose) and saved the video with the skeleton (skeleton.mp4), along with pictures of each frame with the skeletons (driving_frames) and JSON files containing data of each frame with the skeleton (driving_jsons).

![](images/orig.gif) ![](images/output.gif) ![](images/skeleton.gif)

## Running Code
Need to create a requirements.txt 

To run the hand detection code to determine whether the driver's hand is off the wheel, run
```bash
python3 hand_detect.py <input_folder> <output_file>
```
* <input_folder> is the folder containing JSON objects of frames
* <output_file> file containing JSON objects of results (when driver's hands were off the wheel)
