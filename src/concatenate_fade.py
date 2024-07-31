from moviepy.editor import VideoFileClip, concatenate_videoclips

intro = VideoFileClip("intro.mp4")
main_video = VideoFileClip("main_video.mp4")

# Set the duration of the crossfade transition (in seconds)
transition_duration = 2

# Trim the intro and main video to match the transition duration
intro = intro.set_duration(transition_duration)
main_video = main_video.set_duration(transition_duration)

# Apply crossfade transition
video_with_transition = concatenate_videoclips([intro.crossfadeout(transition_duration), main_video.crossfadein(transition_duration)])

# Concatenate the remaining main video
video_with_transition = concatenate_videoclips([video_with_transition, main_video.set_start(transition_duration)])

# Export the final video
video_with_transition.write_videofile("output.mp4")
