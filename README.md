# SHIPcal

SHIPcal is an open-source code to simulate solar heat applications for industrial process heat. SHIPcal is written in Python 3 and can be run from terminal or from a web based front-end. There are several propetary front-ends that call SHIPcal. As for example:
- STEORcal (Developed by Miguel Frasquet)
- ReSSSPI (Developed by SOLATOM)
- CIMAV (Developed by CIMAV)

#Technical comments

#Moved from bitbucket private repository to github (Eurosun 2018)
#Resuming commits and contributions begining October 2018

#Improvements from 2019
-Juan Antonio Aramburo Pasapera (CIMAV) Changed demand creator function to improve the accuracy of the results
-Juan Antonio Aramburo Pasapera (CIMAV) Changed fixed raw water temperature function. Now it depends on the TMY
- Miguel Frasquet Herraiz (SOLATOM) Added new reg to allow external front-ends call ressspi (see an example of frontend at https://github.com/mfrasquet/frontendRessspi

#Bug fixing from 2019
-See slack channel for more information https://shipcal.slack.com. If you want to contribute send an email to mfrasquetherraiz@gmail.com

#All prev. contributors (from bitbucket) will received an email with instructions

Installation instructions (Please check the pdf "SHIPcal Installation Manual" for further information)

#From anaconda (on windows):
- create a new environment and install the following libraries:
  - django, numpy, scipy, pandas, pillow and matplotlib.
- it is also necessary the iapws. Since it is not included in anaconda, install manually in the terminal:
  - pip install iapws
- Now create and navigate to the folder of your project, example /Desktop/SHIPcal:
- clone this repository in the folder: git clone https://github.com/mfrasquet/SHIPcal.git
- clone the frontend repository in the same folder: git clone https://github.com/mfrasquet/SHIPcal_frontend.git
- Access the SHIPcal_frontend folder created after the clonning process (cd SHIPcal)

Now type again:
- python manage.py runserver 0.0.0.0:8000

and that's it!
- Finaly, open a browser and go to http://localhost:8000/

# Developers
- Miguel Frasquet Herraiz
- Juan Antonio Aramburo Pasapera
- Carlos Santiago Rocha Leyva