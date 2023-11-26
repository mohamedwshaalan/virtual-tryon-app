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
> python -m venv .venv 
```
# Local Testing
```
> source .venv/bin/activate
> pip install -r requirements.txt
> flask --app main run
```

# Running Docker
```
docker build --tag flask .
docker run -p 5000:5000 flask
```