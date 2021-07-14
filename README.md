# webscp

## how to use

1. Create a virtual environment
```shell
$ python -m venv .venv
```

2. activate environment
- Terminal
```shell
$ source .venv/bin/activate
```
- PowerShell
```shell
$ .\.venv\Scripts\Activate.ps1
```

3. change directory app use package install in requirements.txt
```shell
$ pip install -r requirements.txt
$ cd app
```

4. run
```shell
$ python main.py
```

5. Interactive　shell input eventID or eventURL
```python
Please input eventPageURL or eventID >>
# example
# eventID: 123456
# URL: http://example.com
```

6. csv output
```
output/eventTitle.csv
```
