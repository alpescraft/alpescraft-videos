FROM python:3.10

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    exiftool \
    && rm -rf /var/lib/apt/lists/*

# Installer Poetry
RUN pip install --upgrade pip && pip install poetry

# Ajouter Poetry au PATH
ENV PATH="/root/.local/bin:$PATH"

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de configuration de Poetry
COPY pyproject.toml poetry.lock ./

# Installer les dépendances du projet
RUN poetry install --no-root

# Copier le reste des fichiers de l'application
COPY . .

# Modifiez le fichier policy.xml pour permettre les opérations nécessaires
RUN sed -i 's/rights="none"/rights="read|write"/g' /etc/ImageMagick-6/policy.xml && \
    sed -i 's/rights="none"/rights="read|write"/g' /etc/ImageMagick-7/policy.xml || true \

# Démarrer une session shell interactive
CMD ["/bin/bash"]
