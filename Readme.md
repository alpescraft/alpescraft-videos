# Automated video editing for meetup and conference videos
Handle post-production in an automated fashion. Joining video track, slides track and sound track(s) 
is done by using file dates in order to sync the various sources.

All you need to do is to specify the start and end time of the main video. Given that you all recording
devices are time-synced, for instance by connecting them to the same wifi.

# Rationale
Post productions allows for a lot more error recovery in case something went wrong.
The drawback is that is is labor intensive. Hence automating that part brings the best 
of both worlds.

# Install
    pip3 install poetry
    poetry install

# Usage 
    python3 src/produce_video_v2.py [conference_theme] session-config.yaml [max time seconds] <--no-intro>


conference_theme is either `ht` or `alpescraft`. It guides the background and the intro

max_time_seconds is used when you want to generate a preview, and avoid to much processing time

The timing is never completely right, to calibrate, the current best solution is to launch 
the generation of a 7s long video, and check the result, then adapt the extra_offset to the sound file. eg

    python3 src/produce_video_v2.py ht session-config.yaml 7 --no-intro


config.yaml is a file of the form (in it's simples form)

```yaml
title: "awesome session"
speaker_name: "John Doe"

speaker:
  parts:
    # This means that the video will start at 1 minute and 8 seconds from the start of the speaker video. 
    # Sound and slides will be synced accordingly. 
    - start: "1:08"
      stop: "55:15"

sound:

slides:
```

necessary directory layout: 
```
.
├── intro.mp4       
├── logo.png
└── whatever-session-name
    ├── config.yml
    ├── sound.mp3
    ├── slides.mp4
    └── video.mp4
```


If the intro has to be dynamically generated, replace the intro file with 
```
├── jingle.mp3       
├── background.jpg  
└── whatever-session-name
    ├── speaker.jpg     # 400x400
```



A more complete example can be found in the `examples` folder, for instance [example-conf.yml](examples/example-conf.yml).

## Features
* transition-fade between intro and main video
* when capturing you can start any time, all you have to provide is the start time of one video
* automatic adjustment of tracks based on media date metadata
* extra_offset can be used to compensate for bad dates

## Intro
Either provide a ready made intro file, or
Generate one automatically 

* Presentation title
* Speaker name
* Background
* Logo
* jingle


