# Automated video editing for meetup and conference videos
Handle post-production in an automated fashion. Joining video track, slides track and sound track(s) 
is done by using file dates in order to sync the various sources.

All you need to do is to specify the start and end time of the main video

# Rationale
Post productions allows for a lot more error recovery in case something went wrong.
The drawback is that is is labor intensive. Hence automating that part brings the best 
of both worlds.

# Usage

    python3 make_video.py session-config.yaml

Where session-config.yaml is a file of the form

```yaml
intro:
  title: "awesome session"
  speaker_name: "John Doe"
  logo: "logo.png"

speaker:
  file_name: "awesome-session.mkv"
  parts:
    - start: "1:08"
      stop: "55:15"

sound:
  file_name: "sound.wav"

slides:
  file_name: "slides.mp4"
```



## Intro
The intro can be dynamically created including:

* Presentation title
* Speaker name
* Background
* Logo
* Music


It does a transition fade with the main video 

# Sound
The soundtrack can be separate (and even several sound-tracks) or originate from the main video.
It is included with a fade-out effect

# Slides
Slides can be a separate video source
