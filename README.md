# INSTALLING THE DEPENDENCIES

if you use poetry

```
poetry shell
poetry install --no-dev
```

if you use pip

```
pip install -r requirements.txt
```

## DEPENDENCIES OF DEVELOPMENT

if you use poetry

```
poetry shell
poetry install
```

if you use pip

```
pip install -r dev-requirements.txt
```

# RUN

```
cd sgv
python main.py
```
## CREDENTIALS

**Name** = *Admin*\
**Pass Word** = *0000*

## CONNECTION

If you want use other database, you can press `Ctrl+l` to alter the configuration of database.

The file mysql.sql contain the struct that database must have.

# RUN tests

```
cd tests
python main.py
```

# BUILD project

```
cd scripts
python build.py
```

# ENCRYPT AND DECRYPT

```
cd scripts
python cript.py e 'word to encrypt'
python cript.py d 'word to decrypt'
```
