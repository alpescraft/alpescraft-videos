# Summary of steps

## Setting Up Your Environment

```sh
docker-compose build
```

T'as vu mes slides ? Je les fais en typst ! Virginie Pageaud - 873 vues
UV, la révolution pour Python Par Lenormand Julien 784 vues
Découverte des serveurs MCP : discuter avec ses outils pour Matias Vara - 678 vues


```sh
docker-compose up -d
docker-compose exec alpescraft-videos /bin/bash
```

## Fetch Talk Info
This will create a to-proceed folder with avatar and config.yml
```sh
poetry run python src/fetch_talk_info.py https://humantalks.com/cities/grenoble/events/1123
```
Not needed anymore: Remove date in config.yml after the name

## Prepare files
Copy the video slides and speaker camera inside to-proceed/talk{1-4}
Check the avatar of the speaker in case they used a different one than Gravatar


## Generate thumbnail
```
poetry run python src/make_thumbnail.py ht to-proceed/talk1/config.yml
poetry run python src/make_thumbnail.py ht to-proceed/talk2/config.yml
poetry run python src/make_thumbnail.py ht to-proceed/talk3/config.yml
poetry run python src/make_thumbnail.py ht to-proceed/talk4/config.yml

```
## Test generation
poetry run python src/produce_video_v2.py ht template/ht/talk1/config.yml 7 --no-intro
poetry run python src/produce_video_v2.py ht template/ht/talk2/config.yml 7 --no-intro


```
.
└── ht
    ├── talk1                    # Directory for the first talk/session
    │   ├── config.yml           # Configuration file for the video processing
    │   ├── slides.mkv           # Video file of the slides for this talk
    │   ├── sound.mp3            # Audio file of the talk's sound
    │   ├── speaker.mp4  
```


Dupliquer timeline
Ajouter Screencast et Speaker
Delink media, remove sound screencast
Relink
CTRL + C sur clip, Option + V sur nouveau clip pour coller attributs
Changer nom
Couper début et fin
Etre sur que ecran titre et logo vont jusqu'a la fin de la video
