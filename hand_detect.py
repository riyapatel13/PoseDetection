import numpy as np
import os
import cv2
import pandas as pd
import json
import csv
import argparse

'''
hand_detect.py

This file contains code for detecting points in time when the driver took his hands 
off the wheel. After passing through the video in OpenPose and receiving a folder 
of JSON files, this code reads through each file, determines which person in the 
frame was the driver, and determines whether or not their hands were off the wheel
using bounding boxes. This is the first "brute force" attempt at pose detection.
'''

# file paths
json_folder = 'data/driving_jsons'
vid_path = 'data/videos/output.mp4'
# bounding box of driver (so we don't detect passengers)
subject_rect = [(71,55), (243, 235)]
# Data from finding rectangles using labelImg - saved in annotated_driving.xml 
# 8 rects = 8 lists
# [top left, bottom right] where each pt is (x,y)
wheel_rects_diags = [[(157,153),(165,165)],
            [(160,143),(167,152)],
            [(162,132),(174,142)],
            [(170,124),(183,131)],
            [(169,116),(196,128)],
            [(192,124),(199,140)],
            [(156,120),(173,163)],
            [(157,108),(201,123)]]


# gets width and height of video (for debugging purposes)
def vid_dimensions(vid_path):
    cap = cv2.VideoCapture(vid_path)
    width = int(cap.get(3))
    height = int(cap.get(4))
    cap.release()
    return width, height


# importing the JSON files into a list
def import_jsons(json_folder_path):
    json_files = [json for json in os.listdir(json_folder_path) if json.endswith('.json')]
    return json_files


'''
Given a path to a folder of json files, boolean for whether we are looking at the 
left wrist, and the number of frames to process (< number of files in json folder), 
this function will create a dataframe with a columns as x, y, confidence. This data 
was found by running the video through OpenPose.
'''
def create_dataframe(json_folder, is_left, num_frames):
    json_files = import_jsons(json_folder)
    wrist_df = pd.DataFrame()

    i = 0
    for file in json_files:
        temp_df = json.load(open(json_folder+'/'+file))
        temp = []
        
        num_people_in_frame = len(temp_df['people'])

        # we know the subject's location on screen, so we can make sure to add points in that area to make sure we don't analyze the wrong person
        # [x, y, confidence]
        if is_left:
                for j in range(num_people_in_frame):
                    key_points = temp_df['people'][j]['pose_keypoints_2d']
                    left_point = [key_points[21], key_points[22], key_points[23]]
                    x = left_point[0]
                    y = left_point[1]

                    # within bounds
                    if x >= subject_rect[0][0] and x <= subject_rect[1][0] and y >= subject_rect[0][1] and y <= subject_rect[1][1]:
                        temp.append(left_point)
                        break
        else:
            for j in range(num_people_in_frame):
                key_points = temp_df['people'][j]['pose_keypoints_2d']
                right_point = [key_points[12], key_points[13], key_points[14]]
                x = right_point[0]
                y = right_point[1]

                # within bounds
                if x >= subject_rect[0][0] and x <= subject_rect[1][0] and y >= subject_rect[0][1] and y <= subject_rect[1][1]:
                    temp.append(right_point)
                    break

        # adding to dataframe
        df = pd.DataFrame(temp)
        # fill N/A values with 0
        # data points with confidence values of 0 should be ignored in analysis
        df.fillna(0)

        try:
            wrist_df = wrist_df.append(df)
        except:
            if is_left:
                print('bad left wrist point set at: ', file)
            else:
                print('bad right wrist point set at: ', file)
 
        # cut off at num_frames frames because it takes too long to processes everything
        i+=1
        if i == num_frames:
            break

    # add column headers
    if is_left:
        wrist_df.columns = ['lx', 'ly', 'lconfidence']
    else:
        wrist_df.columns = ['rx', 'ry', 'rconfidence']
    
    wrist_df.reset_index()
    return wrist_df


# Convert dataframe to csv for viewing purposes. Will be saved under csv_name
def df_to_csv(df, csv_name):
    return df.to_csv(csv_name)


# scaling down to vid dimensions in case the image is viewed at a different scale
def scale_coords(coordinates, scale_factor):
    for rect in coordinates:
        for i in range(len(rect)):
            x,y = rect[i]
            new_coord = (x/(scale_factor), y/(scale_factor))
            rect[i] = new_coord


'''
Given the dataframe of the wrist coordinates, a boolean for whether its the left 
or right wrist, the top left and bottom right points of the bounding boxes, and
a buffer (a buffer of 10 is 10 pixels around the bounding box), this function
returns a list of all times the hands were outside of the bounding box
'''
def off_wheel_frames(wrist_df, is_left, rect_diags, buffer):
    hands_off_frames = []
    frame_num = 0
    for row in wrist_df.iterrows():
        # row[0] is the index of the row (always 0 for some reason)
        # row[1] is the information (x, y, confidence)
        if is_left:
            x = row[1]['lx']
            y = row[1]['ly']
        else:
            x = row[1]['rx']
            y = row[1]['ry']
        in_rect = False

        for rect in rect_diags:
            # checking if in any rectangle
            if (x >= rect[0][0]-buffer and x <= rect[1][0]+buffer) and (y >= rect[0][1]-buffer and y <= rect[1][1]+buffer):
                in_rect = True
            else:
                if is_left:
                    if row[1]['lconfidence'] == 0:
                        continue
                else:
                    if row[1]['rconfidence'] == 0:
                        continue

        if not in_rect:
            hands_off_frames.append(frame_num)
        frame_num += 1
    return hands_off_frames

'''
Given the list of frames where the hand is not on the wheel, this function will
only keep the frames where its neighboring frames are within a range of buffer.
i.e.: if buffer is 5 and the frame number is 60, it will keep frame 60 if there 
exists a frame in the range of 55-65. This prevents noisy data from being added.
'''
def debounce_data(frames, buffer):
    filtered_frames = []
    
    for i in range(len(frames)):
        if (i == 0): 
            if (abs(frames[i] - frames[i+1]) <= buffer):
                filtered_frames.append(frames[i])
        elif (i == len(frames)-1): 
            if (abs(frames[i] - frames[i-1]) <= buffer):
                filtered_frames.append(frames[i])
        else: 
            if (abs(frames[i] - frames[i-1]) <= buffer) or (abs(frames[i] - frames[i+1]) <= buffer):
                filtered_frames.append(frames[i])
    return filtered_frames


'''
Given a list of frames and a range, this function will create a list of tuples of 
start to end frames in that range.
ex: create_range([[7, 10, 15, 31, 35, 37, 51, 60, 78], 15)
    --> [(7,15), (31,60), (78,78)]
The difference between the start of one tuple and the end of another is >= range.
'''
def create_ranges(frames, range_len):
    range_list = []
    
    for i in range(len(frames)):
        if i == 0:
            cur_range = frames[i], frames[i]
            continue
        
        if frames[i]-cur_range[1] <= range_len:
            cur_range = cur_range[0], frames[i]
        
        else:
            range_list.append(cur_range)
            cur_range = frames[i], frames[i]

    range_list.append(cur_range)
    return range_list


# converts frame number to time in min:sec.microsecs given frames per sec of vid in string format
def frame_to_time(frame_num, fps):
    total_secs = frame_num/fps
    mins = int(total_secs // 60)
    secs = round(total_secs % 60, 6)

    time = f"{mins}:{secs}"
    return time

# writes text (list) as a list of JSON objects into outfile
def write_file(text, is_left, outfile):
    data = {}
    json_list = []

    for start,end in text:
        if is_left:
            data["event"] = "left hand off wheel"
        else:
            data["event"] = "right hand off wheel"
        
        # change this depending on fps of video
        fps = 15
        data["start"] = frame_to_time(start, fps)
        data["end"] = frame_to_time(end, fps)
        json_dump = json.dumps(data)
        json_list.append(json_dump)

    with open(outfile, 'a') as out:
            out.writelines(["%s\n" % item for item in json_list])
    
    print("Results written to ", outfile)



if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description = "Hand detection - Given a folder of JSON files representing each frame of a video after being run through OpenPose for pose detection, this file will detect every time the driver's hands have left the steering wheel.")
    argparser.add_argument("input_folder",
                        type=str,
                        help="folder containing JSON objects of frames")
    argparser.add_argument("output_file",
                        type=str,
                        help="file containing JSON objects of results (when driver's hands were off the wheel)")

    args = argparser.parse_args()

    # change this if you want to analyze more/fewer frames
    num_frames_to_analyze = 1000
    left_wrist_df = create_dataframe(args.input_folder, True, num_frames_to_analyze)
    right_wrist_df = create_dataframe(args.input_folder, False, num_frames_to_analyze)

    # smaller padding --> tighter rects, larger padding --> bigger rects
    rect_padding = 10
    l_hands_off_frames = off_wheel_frames(left_wrist_df, True, wheel_rects_diags, rect_padding)
    r_hands_off_frames = off_wheel_frames(right_wrist_df, False, wheel_rects_diags, rect_padding)

    # smaller noise_buf --> more noisy data, larger noise_buf --> smoother data
    noise_buf = 5
    l_updated_frames = debounce_data(l_hands_off_frames, noise_buf)
    r_updated_frames = debounce_data(r_hands_off_frames, noise_buf)

    # uncomment to see results
    '''
    print("left wrist")
    print(l_hands_off_frames)
    print("Num frames: ",len(l_hands_off_frames),"\n")
    print("filtered left frames")
    print(l_updated_frames)
    print("Num frames: ",len(l_updated_frames),"\n")
 
    print("right wrist")
    print(r_hands_off_frames)
    print("Num frames: ",len(r_hands_off_frames),"\n")
    print("filtered right frames")
    print(r_updated_frames)
    print("Num frames: ",len(r_updated_frames),"\n")
    '''
    # smaller time_range --> more precise results, larger --> less precise
    # time_range is in frames
    time_range = 25 # 1.67 s
    l_hand_ranges = create_ranges(l_hands_off_frames, time_range)
    r_hand_ranges = create_ranges(r_hands_off_frames, time_range)

    write_file(l_hand_ranges, True, args.output_file)
    write_file(r_hand_ranges, False, args.output_file)