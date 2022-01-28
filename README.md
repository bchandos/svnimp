# svnimp
Local web app for managing SVN repositories

Test using docker by referring to `docker-test.txt`

```
$ python3 -m venv venv/

$ source venv/bin/activate

$ pip3 install -r requirements.txt

$ python3 svnimp.py
```

## Requirements & Limitations
- You must have password-free access to all `svn` commands
- Almost no error handling currently
- Does not handle merge conflicts
