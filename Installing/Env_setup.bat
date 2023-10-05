@echo off
echo Upgrading pip and installing virtualenv package
pause
py -m pip install --upgrade pip
py -m pip install virtualenv

echo:
echo Crating virtualenv
pause
py -m venv JSUS_env
cd JSUS_env
cd Scripts

call .\activate
cd ..

echo:
echo Clone git repository
pause
git clone https://github.com/JakovStanislav/JSUS
cd JSUS

echo:
where python

echo:
echo Installing packages from requirements.txt
pause
python.exe -m pip install --upgrade pip
pip install -r requirements.txt

echo:
echo Running setup.py file
pause
python setup.py install

echo:
echo Finished installing
pause


