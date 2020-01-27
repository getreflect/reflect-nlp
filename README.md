# reflect-nlp

[![CircleCI](https://circleci.com/gh/jackyzha0/reflect-nlp.svg?style=svg)](https://circleci.com/gh/jackyzha0/reflect-nlp)

the backend to determine intent validity and stats aggregation. <br>

[the main repo.](https://github.com/jackyzha0/reflect-chrome)

<br><br>

### Docker build instructions
1. Build latest docker image: `docker build -t jzhao2k19/reflect-nlp:latest .`
2. Run the image on port 8081: `docker run -p 8081:8081 jzhao2k19/reflect-nlp:latest`

### Running the NLP Model
This project depends on a bunch of Python libraries. Install them by doing `pip install sklearn keras pandas numpy matplotlib`