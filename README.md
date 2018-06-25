## Yolo marker

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
python3 marker.py -p 'path/with/imgs_in_jpg'

#### If you are done working in the virtual environment for the moment, you can deactivate it:
deactivate