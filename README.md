### Author:Maciej Knapik

# Setting up the application

```python
$ git clone https://github.com/JaKnapik/api
$ cd api

$ virtualenv -p `which python3` venv
$ source venv/bin/activate
(venv) $ pip3 install flask
(venv) $ pip3 install requests
(venv) $ pip3 install requestium
(venv) $ pip3 install flask-mysqldb
(venv) $ pip3 install passlib

(venv) $ python setup.py develop
(venv) $ python api/app.py
