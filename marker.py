# import the necessary packages
import cv2, glob, os, argparse, math
from natsort import natsorted

# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
refPt = []
cropping = False
class_selected = 0
regions = list()
originalImage = None
file_pos = 0
NUM_IMGS = 0
MAX_WIDTH = 1280
MAX_HEIGHT = 800

class_colours = [(58,36,170), (218,135,9), (166,206,227), (31,120,180), (178,223,138), (51,160,44), (251,154,153), (227,26,28), (253,191,111),
                 (255,127,0)]
#, (202,178,214), (106,61,154)

# class_colours = [(141,211,199), (255,255,179), (190,186,218), (251,128,114), (128,177,211), (253,180,98), (179,222,105),
#                  (252,205,229), (217,217,217), (188,128,189)]
# class_colours.reverse() # I prefer that start from end :p

# class_colours = [(58,36,170), (40,65,95), (207,207,234), (183,117,117), (160,219,142), (192,214,228), (255,192,203), (210,221,205),
#                  (255, 253, 199), (218,135,9)]


def draw_info(image):

    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.rectangle(image, (7,5), (103,23), (138, 136, 142), cv2.FILLED)
    cv2.putText(image,'Selected: {}'.format(class_selected),(10,20), font, 0.5, class_colours[class_selected],1, cv2.LINE_AA)

    pos_y = 40
    for i in range(0, len(class_colours)):
        cv2.putText(image, 'Class {}'.format(i), (10, pos_y), font, 0.5, class_colours[i], 1, cv2.LINE_4)
        pos_y = pos_y + 15

    cv2.rectangle(image, (7,pos_y+13), (95,pos_y+30), (138, 136, 142), cv2.FILLED)
    cv2.putText(image,'{} of {}'.format(file_pos+1, NUM_IMGS),(10,pos_y+25), font, 0.5, (255, 255, 255),1, cv2.LINE_8)

    cv2.putText(image,'B (back)',(10, pos_y+40), font, 0.5, (255, 255, 255),1, cv2.LINE_8)
    cv2.putText(image, 'N (next|save)', (10, pos_y + 55), font, 0.5, (255, 255, 255), 1, cv2.LINE_8)
    cv2.putText(image, 'R (reset)', (10, pos_y + 70), font, 0.5, (255, 255, 255), 1, cv2.LINE_8)
    cv2.putText(image, 'Q (quit)', (10, pos_y + 85), font, 0.5, (255, 255, 255), 1, cv2.LINE_8)

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
    global refPt, refPtAux, cropping

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being
    # performed
    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x, y)]
        cropping = True

        element = dict()
        element['region'] = [refPt[0], refPt[0]]
        element['class'] = class_selected
        regions.append(element)

    # check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
        # record the ending (x, y) coordinates and indicate that
        # the cropping operation is finished
        refPt.append((x, y))
        cropping = False

        element = dict()
        element['region'] = [refPt[0], refPt[1]]
        element['class'] = class_selected
        regions[-1] = element

        print_regions()

    # check if the mouse is dragging a region
    elif event == cv2.EVENT_MOUSEMOVE and cropping == True:
        refPtAux = (x, y)

        element = dict()
        element['region'] = [refPt[0], refPtAux]
        element['class'] = class_selected
        regions[-1] = element

        print_regions(drag=True)



def print_regions(drag=False):
    cv2.imshow("image", image)

    for region in regions:
        class_type = region['class']
        region = region['region']

        # draw a rectangle around the region of interest
        if drag==True:
            aux = image.copy()
            cv2.rectangle(aux, region[0], region[1], class_colours[class_type], 2)
            cv2.imshow("image", aux)
        else:
            cv2.rectangle(image, region[0], region[1], class_colours[class_type], 2)
            cv2.imshow("image", image)




if __name__ == '__main__':
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--path", required=True, help="Path to the image.", type=str)
    ap.add_argument('-d', '--dimension', required=True, nargs=2, help='Max width and height to show the image.', type=int)
    ap.add_argument('-n', '--numbers', required=False, default=False, help="Name of images are numbers (True) or not (False). Default is False.", type=bool)
    args = vars(ap.parse_args())

    MAX_WIDTH = args['dimension'][0]
    MAX_HEIGHT = args['dimension'][1]

    # Image path list
    if args['numbers'] is True:
        files = sorted(glob.glob(args['path']), key = lambda x: int(x[args['path'].find('*'):x.find('.')]))
    else:
        files = natsorted(glob.glob(args['path']))

    NUM_IMGS = len(files)

    if not NUM_IMGS:
        print('No image!')
        exit(0)

    # Read the first image and its markers
    image = read_img(files[file_pos])
    read_markers(files[file_pos], image.shape)
    originalImage = image

    # keep looping until the 'q' key is pressed
    while True:

        # display the image and wait for a keypress
        # image = read_img(files[file_pos])
        read_markers(files[file_pos], image.shape)
        draw_info(image)

        cv2.imshow("image", image)
        key = cv2.waitKey(-1)

        # if the '0-9' key is pressed, class is setted
        if key >= 48 and key <= 57:
            class_selected = int(chr(key))

        if key == ord("n"):
            save_regions(files[file_pos], regions, image.shape)
            regions = list()

            if file_pos + 1 < NUM_IMGS:
                file_pos = file_pos + 1

                image = read_img(files[file_pos])
                read_markers(files[file_pos], image.shape)

        if key == ord("b"):
            if file_pos > 0:
                file_pos = file_pos - 1

                image = read_img(files[file_pos])
                read_markers(files[file_pos], image.shape)

        # if the 'r' key is pressed, reset the cropping region
        if key == ord("r"):
            
            image = read_img(files[file_pos])
            print('Cleaning regions')
            regions = list()

            filename, file_extension = os.path.splitext(files[file_pos])
            file_path = files[file_pos].replace(file_extension, ".txt")
            # file_path = files[file_pos].replace("jpg", "txt")

            if os.path.isfile(file_path):
                os.remove(file_path)

            print_regions()

        # if the 'q' key is pressed, break from the loop
        elif key == ord("q"):
            break


    # close all open windows
    cv2.destroyAllWindows()
