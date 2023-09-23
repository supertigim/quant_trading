# Introduction  

 Playground for quant trading. 

## Environments
* Python installer: pyenv
* Python virtual environment: poetry
* python: 3.11
* Containerization: Docker
* SCM : github
* Database: sqlite3
* Code editor : VSCode with Github Copilot, Jupyter, Pylance, Python, and SQLite

## How to run jupyter notebook

```bash
$ docker-compose up 

# Go to http://localhost:8888
# Token password is '1'  <- See the jupyter_config/jupyter_notebook_config.json
```

## Jupyter notebooks

* notebooks/data_korea.ipynb : 국내(Kospi) 주식 데이터 수집, DB 생성/저장, etc


 ## Reference

 - [국내 주식 데이터 수집](https://github.com/hyunyulhenry/quant_py/blob/main/data_korea.ipynb)
