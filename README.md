# ressspi_offline

#Moved from bitbucket private repository to github (Eurosun 2018)
#Resuming commits and contributions begining October 2018

#Improvements from 2019
-Juan Antonio Aramburo Pasapera (CIMAV) Changed demand creator funtion to improve the accuracy of the results
-Juan Antonio Aramburo Pasapera (CIMAV) Changed fixed raw water temperature function. Now it depends on the TMY
- Miguel Frasquet Herraiz (SOLATOM) Added new reg to allow external front-ends call ressspi (see an example of frontend at https://github.com/mfrasquet/frontendRessspi

#Bug fixing from 2019
-See slack channel for more information

#All prev. contributors (from bitbucket) will received an email with instructions

Installation instructions
From anaconda (on windows):
create a new environment and install the following libraries:
django, numpy, scipy, pandas, pillow and matplotlib.
it is also necessary the iapws. Since it is not included in anaconda, install manually:
pip install iapws
Now create and navegate to a folder for your project, ej:
cd prueba
copy the cloned folder frontendRessspi.
From prueba folder, type:
django-admin startproject frontendRessspi
now get into the folder frontendRessspi and type:
python manage.py runserver 0.0.0.0:8000
if an error appears is because still is not copied the offline project. So, clone a copy in "prueba" ressspi_offline.
dentro de la carpeta
it is no necessary to type python manage.py startapp FE1. Instead, copy the original content of the cloned folder FE1 and overwrite that in "prueba".
Now type again:
python manage.py runserver 0.0.0.0:8000
and that's it!
Finaly, open a browser and go to http://localhost:8000/
