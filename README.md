# Automated Video Editing for Meetup and Conference Videos

Handle post-production in an automated fashion. Joining video track, slides track, and sound track(s) is done by using file dates to sync the various sources. All you need to do is specify the start and end time of the main video. Ensure all recording devices are time-synced, for instance, by connecting them to the same Wi-Fi network.

## Key Commands

```sh
poetry run python src/produce_video_v2.py ht template/ht/talk1/config.yml 7 --no-intro
poetry run python src/produce_video_v2.py ht template/ht/talk1/config.yml
poetry run python src/fetch_talk_info.py https://humantalks.com/cities/grenoble/events/609
poetry run python src/make_thumbnail.py ht template/ht/talk1/config.yml
```

## Features

- Transition-fade between intro and main video
- When capturing, you can start any time; all you have to provide is the start time of one video
- Automatic adjustment of tracks based on media date metadata
- `extra_offset` can be used to compensate for bad dates

### Intro

Either provide a ready-made intro file or generate one automatically with:
- Presentation title
- Speaker name
- Background
- Logo
- Jingle

## Usage

```sh
python3 src/produce_video_v2.py [conference_theme] session-config.yaml [max time seconds] <--no-intro>
```

- `conference_theme` is either `ht` or `alpescraft`. It guides the background and the intro.
- `max_time_seconds` is used when you want to generate a preview and avoid too much processing time.

The timing is never completely right. To calibrate, the current best solution is to generate a 7-second long video, check the result, and then adapt the `extra_offset` to the sound file. For example:

```sh
python3 src/produce_video_v2.py ht session-config.yaml 7 --no-intro
```

`config.yml` is a file of the form (in its simplest form):

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

It uses conventions for the file names and locations. Necessary directory layout:

```
.
└── to-process
    ├── jingle.mp4               # Jingle video file for the intro (if dynamically generated)
    ├── logo.webp                # Logo image for the conference theme
    ├── talk1                    # Directory for the first talk/session
    │   ├── config.yml           # Configuration file for the video processing
    │   ├── slides.mkv           # Video file of the slides for this talk
    │   ├── sound.mp3            # Audio file of the talk's sound
    │   ├── speaker.mp4          # Video file of the speaker for this talk
    ├── talk2                    # Directory for the second talk/session
    │   ├── config.yml           # Configuration file for the video processing
    │   ├── slides.mkv           # Video file of the slides for this talk
    │   ├── sound.mp3            # Audio file of the talk's sound
    │   ├── speaker.mp4          # Video file of the speaker for this talk
    ├── talk3                    # Directory for the third talk/session
    │   ├── config.yml           # Configuration file for the video processing
    │   ├── slides.mkv           # Video file of the slides for this talk
    │   ├── sound.mp3            # Audio file of the talk's sound
    │   ├── speaker.mp4          # Video file of the speaker for this talk
    └── talk4                    # Directory for the fourth talk/session
        ├── config.yml           # Configuration file for the video processing
        ├── slides.mkv           # Video file of the slides for this talk
        ├── sound.mp3            # Audio file of the talk's sound
        ├── speaker.mp4          # Video file of the speaker for this talk
```

### Files and Directories Explained

- **`logo.webp`**: The logo image used for the conference theme.
- **`jingle.mp4`**: A jingle video file used for the intro if the intro is dynamically generated.
- **`talk1`, `talk2`, `talk3`, `talk4`**: Directories for each individual talk/session. Each directory should contain:
  - **`config.yml`**: Configuration file with the session details and synchronization settings.
  - **`slides.mkv`**: Video file of the slides for the talk.
  - **`sound.mp3`**: Audio file of the talk's sound.
  - **`speaker.mp4`**: Video file of the speaker's presentation.

---

## Install

```sh
pip3 install poetry
poetry install
```

---

## Fetch Talk Info

This script allows you to retrieve information from a HumanTalks event and generate YAML configuration files for each talk, as well as download the speakers' images.

```bash
poetry run python src/fetch_talk_info.py https://humantalks.com/cities/grenoble/events/609
```

### Directory Structure After Running the Script

The `to-proceed` directory will have the following structure:

```
to-proceed/
├── talk1/
│   ├── speaker.webp      # Speaker's image
│   └── config.yml        # YAML configuration file with talk information
├── talk2/
│   ├── speaker.webp      # Speaker's image
│   └── config.yml        # YAML configuration file with talk information
├── talk3/
│   ├── speaker.webp      # Speaker's image
│   └── config.yml        # YAML configuration file with talk information
└── ...
```

---

## Generate thumbnail

This script allows you to retrieve information from a HumanTalks event and generate YAML configuration files for each talk, as well as download the speakers' images.

```bash
poetry run python src/make_thumbnail.py ht template/ht/talk1/config.yml
```

---

## Docker and Docker Compose (Volume Access)

To set up your environment using Docker Compose, follow these steps:

### Prerequisites

Make sure you have **Docker** and **Docker Compose** installed on your machine. You can download and install them from [Docker](https://www.docker.com/get-started).

### Setting Up Your Environment

```sh
docker-compose build
docker-compose up -d
docker-compose exec alpescraft-videos /bin/bash
```

### Generate a Test Video

Once inside the container, you can generate a test video by running:

```sh
poetry run python src/produce_video_v2.py ht template/ht/talk1/config.yml 7 --no-intro
```

### Generate the Full Video

To generate the full video, run:

```sh
poetry run python src/produce_video_v2.py ht template/ht/talk1/config.yml
```

### Docker Compose Cheat Sheet

| Command                             | Description                                        |
|-------------------------------------|----------------------------------------------------|
| `docker-compose up`                 | Start the services defined in `docker-compose.yml` |
| `docker-compose up -d`              | Start the services in detached mode                |
| `docker-compose down`               | Stop the services and clean up                     |
| `docker-compose logs`               | Show logs from the services                        |
| `docker-compose exec app /bin/bash` | Access the `app` container in interactive mode     |
| `docker-compose exec web /bin/bash` | Access the `web` container in interactive mode     |
| `docker-compose build`              | Build or rebuild the images                        |
| `docker-compose stop`               | Stop the services without removing the containers  |

---

### Additional Tips

- I used DaVinci Resolve to crop the video and flip it because the slides are on the right, and people tend to look on the left.
- Ensure all file paths and configurations are correct for successful video generation.

### References

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Dockerfile Reference](https://docs.docker.com/engine/reference/builder/)
- [Docker Compose CLI Reference](https://docs.docker.com/compose/cli-command/)
- [Python HTTP Server Documentation](https://docs.python.org/3/library/http.server.html)

---
