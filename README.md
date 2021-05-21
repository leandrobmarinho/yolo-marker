## Yolo marker

![screenshot](https://user-images.githubusercontent.com/19287934/67440616-3e601e00-f5d0-11e9-9804-7780635fbd51.png)

### Install virtualenv via pip:

pip install virtualenv

### Test your installation

virtualenv --version

### Create the virtualenv for the project

cd yolo-marker\
virtualenv .env -p python3 --no-site-packages

### To begin using the virtual environment, it needs to be activated:

. .env/bin/activate

### Intall the packages

pip install -r requirements.txt

### Run the application

python3 marker.py -p \"PATH_WITH_IMGS/\*EXTENSION\" -d WIDTH HEIGHT\
Eg.: python3 marker.py -p \"/Users/leandrobmarinho/img/\*.png\" -d 1920 1080

#### If you are done working in the virtual environment for the moment, you can deactivate it:

deactivate

## .txt files for Yolo train

### Run the script to generate the txt files

#### write_img_names - the images' path will be data/img

python write_img_names.py -p \"PATH_WITH_IMGS/\*EXTENSION\" -ptrain [0..1] [-v]\
Eg1.: python write_img_names.py -p \"/Users/leandrobmarinho/img/\*.png\" -ptrain .95 -v\
Eg2.: python write_img_names.py -p \"/Users/leandrobmarinho/img/\*.png\" -ptrain .95

#### write_img_names_2 - the images' path will be the absolute path, and if there is not marked images, they will not be counted to the train and test files

python write_img_names_2.py -p \"PATH_WITH_IMGS/\*EXTENSION\" -ptrain [0..1] [-v]\
Eg1.: python write_img_names_2.py -p \"/Users/leandrobmarinho/img/\*.png\" -ptrain .95 -v\

## marker_change_class.py

This file is different from the markey.py file. The difference consists on the permission of changing a class after marking the bounding box. To change the class, you should place the mouse cursor inside the bounding box, then press the number representing the class. However, if you are marking the images, you should be attentive to change the class outside the of the existing bounding boxes. The marker_change_class.py file is useful, mainly, on the reviewing process.

## marker_characters.py

All characters can be chosen as object classes, in addition to numbers. Image manipulations are now:

**\+** &#8594; next image

**\-** &#8594; previous image

**\/** &#8594; reset the cropping region

**\*** &#8594; exit
