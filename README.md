# virtual-tryon-app
Github Repository for Thesis Project

# Requirements
- Python 3.6+
- Flask
- Flutter

# Backend Setup
```
> git clone https://github.com/mohamedwshaalan/virtual-tryon-app.git
> cd virtual-tryon-app
> python -m venv <venv-name> 
```
# Local Testing
```
> source .venv/bin/activate
> pip install -r requirements.
> export FLASK_APP=app.py
> flask run
```

# Building Docker Compose
```
docker-compose up --build
```

# Running Docker Compose 
```
docker-compose pull
docker-compose up -d --no-build
```

# Removing all images and containers
```
docker system prune -a
```