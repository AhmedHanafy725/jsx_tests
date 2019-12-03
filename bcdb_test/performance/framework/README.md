### Before running tests
1- Don't use core redis as it has limitation on the maximum size of memory.
2- Edit redis's config file by adding memory's maximum size of 3 gb
3- Start redis on port `6379`
4- Install mongodb `apt-get install -y mongodb`
5- Install python packages `pip3 install -r requirements.txt`

### How to run

```bash
nosetests-3.4 -v --nologcapture testcases.py
```
