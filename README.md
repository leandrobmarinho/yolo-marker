## Yolo marker

![](screen.png?raw=true)

### Install virtualenv via pip:
pip install virtualenv

### Test your installation
virtualenv --version



### Create the virtualenv for the project
virtualenv yolo-marker -p python3 --no-site-packages\
cd yolo-marker

### To begin using the virtual environment, it needs to be activated:
source bin/activate

### Intall the packages
pip install -r requirements.txt

### Run the application
python3 marker.py -p <PATH_WITH_IMGS_IN_JPG> -d <WIDTH> <HEIGHT>

#### If you are done working in the virtual environment for the moment, you can deactivate it:
deactivate

