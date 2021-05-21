# import the necessary packages
import cv2, glob, os, argparse, math
from random import randint

# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
refPt = []
cropping = False
class_selected = 0
class_str = ''
dict_classes = dict()
regions = list()
file_pos = 0
NUM_IMGS = 0
MAX_WIDTH = 1280
MAX_HEIGHT = 800
class_colours = list()

# def draw_info(image):
    # font = cv2.FONT_HERSHEY_SIMPLEX
    # cv2.rectangle(image, (0,0), (110,15), (138, 136, 142), cv2.FILLED)
    # cv2.putText(image,'Selected: {}'.format(class_str),(3,13), font, 0.1, class_colours[class_selected],1, cv2.LINE_AA)

    # pos_y = 15

    # cv2.rectangle(image, (0,pos_y), (85,pos_y+15), (138, 136, 142), cv2.FILLED)
    # cv2.putText(image,'{} of {}'.format(file_pos+1, NUM_IMGS),(3,pos_y+13), font, 0.1, (255, 255, 255), 1, cv2.LINE_8)


def save_regions(image_path, regions, dimensions):
    # Replace jpg path to read txt file

    filename, file_extension = os.path.splitext(image_path)

    file_path = image_path.replace(file_extension, ".txt")

    weight_img = dimensions[1]
    height_img = dimensions[0]

    if regions:
        print('\nSaving ... {}'.format(regions))
        file = open(file_path, 'w')
        for region in regions:

            weight = region['region'][1][0] - region['region'][0][0]
            height = region['region'][1][1] - region['region'][0][1]
            Yolo_x = (region['region'][0][0] + (weight/2)) / weight_img
            Yolo_y = (region['region'][0][1] + (height/2)) / height_img
            Yolo_weight = abs(weight / weight_img)
            Yolo_height = abs(height / height_img)

            print('{} {:6f} {:6f} {:6f} {:6f}'.format(region['class'], Yolo_x, Yolo_y, Yolo_weight, Yolo_height))
            # print('<{} {} {} {} {}>'.format(region['class'], (region['region'][0][0] + (weight/2)), (region['region'][0][1] + (height/2)), weight, height))

            file.write('{} {:6f} {:6f} {:6f} {:6f}\n'.format(region['class'], Yolo_x, Yolo_y, Yolo_weight, Yolo_height))

        file.close()


def read_markers(image_path, dimensions):
    global regions

    filename, file_extension = os.path.splitext(image_path)

    # Replace jpg path to read txt file
    file_path = image_path.replace(file_extension, ".txt")

    if os.path.isfile(file_path):
        regions = list()

        weight_img = dimensions[1]
        height_img = dimensions[0]

        file = open(file_path, "r")
        lines = file.readlines()
        for line in lines:
            line = line.replace("\n", "")
            line = line.split(' ')
            # print(line)

            x = round(float(line[1]) * weight_img) # centroid
            y = round(float(line[2]) * height_img) # centroid
            weight = round(float(line[3]) * weight_img)
            height = round(float(line[4]) * height_img)
            Yolo_class = int(line[0])

            element = dict()
            element['region'] = [(round(x-(weight/2)), round(y-(height/2))), (round(x + (weight/2)), round(y + (height/2)))]
            element['class'] = Yolo_class
            regions.append(element)

        file.close()

        print_regions()


def read_img(file_path):
    global MAX_WIDTH, MAX_HEIGHT
    image = cv2.imread(file_path)
    dimensions = image.shape
    print('{} {}'.format(file_path, dimensions))

    if dimensions[1] > MAX_WIDTH or dimensions[0] > MAX_HEIGHT:
        if math.ceil(dimensions[1] / MAX_WIDTH) > math.ceil(dimensions[0] / MAX_HEIGHT):
            denominator = math.ceil(dimensions[1] / MAX_WIDTH)
        else:
            denominator = math.ceil(dimensions[0] / MAX_HEIGHT)

        image = cv2.resize(image, None, fx=1 / denominator, fy=1 / denominator, interpolation=cv2.INTER_CUBIC)
        print("New dimension {}".format(image.shape))


    cv2.namedWindow("image")
    cv2.setMouseCallback("image", click_and_crop)

    #read_markers(file_path)
    return image


def click_and_crop(event, x, y, flags, param):
    # grab references to the global variables
    global refPt, cropping

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being
    # performed
    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x, y)]
        cropping = True

    # check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
        # record the ending (x, y) coordinates and indicate that
        # the cropping operation is finished
        refPt.append((x, y))
        cropping = False

        element = dict()
        element['region'] = [refPt[0], refPt[1]]
        element['class'] = class_selected
        regions.append(element)

        print_regions()



def print_regions():
    cv2.imshow("image", image)

    for region in regions:
        class_type = region['class']
        region = region['region']

        # draw a rectangle around the region of interest
        cv2.rectangle(image, region[0], region[1], class_colours[class_type], 1)
        cv2.imshow("image", image)



if __name__ == '__main__':

    for m, i in enumerate(range(48, 58)):
        dict_classes[chr(i)] = m

    for n, j in enumerate(range(97, 123)):
        dict_classes[chr(j)] = n+10

    class_colours = [(randint(0, 255),randint(0, 255),randint(0, 255)) for _ in range(len(dict_classes))]

    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--path", required=True, help="Path to the image", type=str)
    ap.add_argument('-d', '--dimension', nargs=2, help='Max width and height to show the image', required=True, type=int)
    args = vars(ap.parse_args())

    MAX_WIDTH = args['dimension'][0]
    MAX_HEIGHT = args['dimension'][1]

    # Image path list
    files = glob.glob(args['path'])
    NUM_IMGS = len(files)

    if not NUM_IMGS:
        print('No image!')
        exit(0)

    # Read the first image and its markers
    image = read_img(files[file_pos])
    read_markers(files[file_pos], image.shape)

    # keep looping until the 'q' key is pressed
    while True:

        # display the image and wait for a keypress
        # image = read_img(files[file_pos])
        read_markers(files[file_pos], image.shape)
        # draw_info(image)

        cv2.imshow("image", image)
        key = cv2.waitKey(-1)

        # if the '0-9' key is pressed, class is setted
        if key >= 48 and key <= 57:
            class_selected = dict_classes[chr(key)]
            class_str = chr(key)
            print(class_str)

        # if the 'A-Z' key is pressed, class is setted
        if key >= 97 and key <= 123:
            class_selected = dict_classes[chr(key)]
            class_str = chr(key-32)
            print(class_str)

        # if the '+' key is pressed, next image is setted
        if key == ord("+"):
            save_regions(files[file_pos], regions, image.shape)
            regions = list()

            if file_pos + 1 < NUM_IMGS:
                file_pos = file_pos + 1

                image = read_img(files[file_pos])
                read_markers(files[file_pos], image.shape)

        # if the '-' key is pressed, previous image is setted
        if key == ord("-"):
            if file_pos > 0:
                file_pos = file_pos - 1

                image = read_img(files[file_pos])
                read_markers(files[file_pos], image.shape)

        # if the '/' key is pressed, reset the cropping region
        if key == ord("/"):
            image = read_img(files[file_pos])
            print('Cleaning regions')
            regions = list()

            filename, file_extension = os.path.splitext(files[file_pos])
            file_path = files[file_pos].replace(file_extension, ".txt")
            # file_path = files[file_pos].replace("jpg", "txt")

            if os.path.isfile(file_path):
                os.remove(file_path)

            print_regions()

        # if the '*' key is pressed, break from the loop
        elif key == ord("*"):
            break

    # close all open windows
    cv2.destroyAllWindows()
