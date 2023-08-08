starting_time = file_creation_date + seconds_in_video_where_action_starts
starting_second = to_seconds(starting_time - second_file_create_time) 

# get file creation time

import os
import time

file_path = 'path_to_your_file_here'

creation_time = os.path.getctime(file_path)
creation_time_milliseconds = int(creation_time * 1000)

# compose

from moviepy.editor import VideoFileClip, CompositeVideoClip
import os

def create_composite_video(video_path1, video_path2, output_path):
    creation_time1 = os.path.getctime(video_path1)
    creation_time2 = os.path.getctime(video_path2)
    time_offset = creation_time2 - creation_time1

    video_clip1 = VideoFileClip(video_path1)
    video_clip2 = VideoFileClip(video_path2)

    # Adjust the starting time of the second video
    video_clip2 = video_clip2.set_start(max(0, time_offset))

    # Set the duration of both clips to the minimum of their durations
    min_duration = min(video_clip1.duration, video_clip2.duration)
    video_clip1 = video_clip1.set_duration(min_duration)
    video_clip2 = video_clip2.set_duration(min_duration)

    # Create a composite video clip with both videos playing simultaneously
    composite_clip = CompositeVideoClip([video_clip1, video_clip2.set_position(('center', 'center'))])

    # Export the composite video clip
    composite_clip.write_videofile(output_path)

video_file1 = 'path_to_video_file1.mp4'
video_file2 = 'path_to_video_file2.mp4'
output_file = 'output_composite_video.mp4'

create_composite_video(video_file1, video_file2, output_file)
