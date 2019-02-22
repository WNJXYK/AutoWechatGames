import os, time
import cv2, numpy

####### ADB Screencap #######
global screencapLast, screencapNow
screencapLast = 0
screencapNow = 1


def screen():
    # Calc FPS
    global screencapLast, screencapNow
    screencapLast = screencapNow
    screencapNow = time.time()
    # Create & Pull
    screencapName = "screencap.png"
    os.system('adb shell screencap -p /sdcard/{}'.format(screencapName))
    os.system('adb pull /sdcard/{} .'.format(screencapName))
    # Read & Return
    img = cv2.imread(screencapName, -1)
    return img


def screen_fps():
    global screencapLast, screencapNow
    return "FPS: {}".format(1.0/(screencapNow-screencapLast))


####### ABD Click #######
def click(x, y):
    os.system("adb shell input tap %d %d" % (x, y))


def sweep(x0, y0, x1, y1, ctime = 50):
    os.system("adb shell input touchscreen swipe %d %d %d %d %d" % (x0, y0, x1, y1, ctime))


def long_click(x, y, ctime = 1000):
    sweep(x, y, x+5, y+5, ctime)


###### CV ######
def read_img(file, fx):
    # Read
    img = cv2.imread(file, -1)

    # Resize
    a, w, h = img.shape[::-1]
    w = int(w * fx)
    h = int(h * fx)
    img = cv2.resize(img, (w, h))

    return img


def match_img(img, tem, thr):
    # Info
    a, w, h = tem.shape[::-1]
    res = cv2.matchTemplate(img, tem, cv2.TM_CCOEFF_NORMED)


    # Select
    loc = numpy.where(res >= thr)

    # Draw
    for pt in zip(*loc[::-1]):
        cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (255, 255, 255), 2)

    return loc, res


def show_img(img, title = "screen", height = 800):
    # Resize
    size = img.shape
    dsize = (size[1] * height // size[0], height)
    disp = cv2.resize(img, dsize)

    # Show
    cv2.imshow(title, disp)

    # Waitkey
    return cv2.waitKey(1)


###### Main ######

def main():
    while True:
        img = screen()
        cv2.imshow('image', img)
        k = cv2.waitKey(1)
        if k == 27:  # wait for ESC key to exit
            cv2.destroyAllWindows()
        elif k == ord('s'):  # wait for 's' key to save and exit
            cv2.imwrite('messigray.png', img)
            cv2.destroyAllWindows()
    # pass

if __name__ == "__main__": main()

