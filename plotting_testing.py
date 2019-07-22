import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from convolution_matching import FindMaterial

#cd '/Users/user/Documents/raman_analysis'

test_png = "../../raman_analysis/uploads/L_M1_Rescan_Area.bmp"
test_spectra = "uploads/test_spectra.csv"

fm = FindMaterial(test_spectra, 'graphene_oxide', subtract_baseline=False)
fm.find_matches()

# to plot match positions, it's not enough to just get the position, 
#just make bitmap as we're going, actually grayscale to reflect confidence score

# need to get dimensions- its not necessaritly square

first_x = fm.data.loc[fm.data["x"] == fm.data.x[0]]

#import imageio
#import visvis as vv

image = mpimg.imread(test_png)

im = Image.open(test_png)
#m.show()

np_im = np.array(im)

im_back_again = Image.fromarray(np_im)
# need to work out what x and y correspond to, x is outer, y is inner
# say x length is 20, y length is 10, dimensions of 

len_x = 20
len_y = 10

i = 13

def make_match_image_background(df):
    # get dimensions:
    len_x = len(df.loc[df.data["x"] == df.data.x[0]])
    len_y = len(df.data)/float(x)
    image = np.zeros(len_x, len_y)
    x = int(i)/int(len_y)
    y = i%(x*len_y)


# want to show where matches are in numpy array,
# use alpha (transparency) to indicate confidence
# so not confident is completely transparent, 100% confident is completely opaque
# so want binary, but not black and white, with adjustable alpha
class MatchImage(object):
    def __init__(self, df):
        self.len_x = len(df.loc[df.data["x"] == df.data.x[0]])
        self.len_y = len(df.data)/float(x)
        self.match_image = np.zeros(len_x, len_y, dtype = np.uint8)

    def add_value_to_image(self, i, con):
        x = int(i)/int(self.len_y)
        y = i%(x*self.len_y)
        self.match_image[x, y] = [0, 0, 255, np.uint8(con*0.01*255)]

    def add_image(self, image_filename, testing = True):
        im = Image.open(image_filename)
        np_im = np.array(im)
        im_shape = np_im.shape
        im_x = im_shape[0]
        im_y = im_shape[1]
        if not testing:
            if im_x != self.len_x:
                raise ValueError("image x dimension, %d, does not match data x dimension, %d" % (im_x, self.len_x))
            if im_y != self.len_y:
                raise ValueError("image y dimension, %d, does not match data y dimension, %d" % (im_y, self.len_y))



random_array = np.array([[[0,0, 255, np.random.randint(255)] for i in range(100)] for j in range(100)],np.uint8)
random_image = Image.fromarray(random_array)

# blue at 100% opaque is [0, 0, 255, 255], blue at 100% transparency is [0, 0, 255, 0]

# test on 
filename = "D_M1_Spleen_Slide3_2019_02_11_14_43_47.txt"
image_filename = "D_M1_Spleen_Slide3_Area_2.bmp"

fm = FindMaterial(filename, 'graphene_oxide', subtract_baseline=False)
fm.overlay_match_positions(image_filename, "test.bmp", confidence="all")

mi = MatchImage(fm.x, fm.y)
mi.add_image(image_filename)
matches = fm.matches.matches
for match, con in matches:
    mi.add_value_to_image(match, con)

mi.save_image("test.png")


# now need to make it selectable.... matlab has built in function, imfreehand
# python offers: https://stackoverflow.com/questions/15058621/python-interactive-selection-tools-like-in-matlab

# in send_packet_command get error 41 while writing to socket. protocol wrong type for socket

from convolution_matching import FindMaterial
test_png = "../../raman_analysis/uploads/L_M1_Rescan_Area.bmp"
test_spectra = "../../raman_analysis/uploads/test_spectra.csv"
fm = FindMaterial(test_spectra, 'graphene_oxide', subtract_baseline=False)

fm.overlay_match_positions( "D_M1_Spleen_Slide3_Area_2.bmp", "test2.png")
#(u'uploads/D_M1_Spleen_Slide3_2019_02_11_14_43_47.txt', u'graphene_oxide', u'False')
#(u'uploads/D_M1_Spleen_Slide3_2019_02_11_14_43_47.txt', u'graphene_oxide', u'False')

matches = fm.matches
len_x = fm.len_x
len_y = fm.len_y

matches_med = fm.get_condifence_matches()
from match_support_classes import MatchImage


mi = MatchImage(len_x, len_y)
mi.add_image("D_M1_Spleen_Slide3_Area_2.bmp")
for match, confidence, _ in matches_med:
    mi.add_value_to_image(match, confidence)

mi.save_image("test_green_manual_contrast.png")

# tested: yellow [255, 255, 0, np.uint8(con*0.01*255)] - not enough contrast between high and low confidence- even with manually adjusted transparency, not great
# orange: [255, 128, 0, np.uint8(con*0.01*255)]- better, both bright and contrast slightly visible, not very visible when using medium filter, better with manual contrast
# pink: [255, 0, 127, np.uint8(con*0.01*255)]- visible but contrast not so good, contrast still low
# green [0, 204, 102, np.uint8(con*0.01*255)] - visible but low contrast, same even for manual contrast

# all have same problem of low contrast if they stand out. try pure r/g
# red: [255, 0, 0, np.uint8(con*0.01*255)]
# pure green: [ 0, 255, 0, np.uint8(con*0.01*255)] - same issue as yellow

# use orange!!
confidence = 'medium'
matches = fm.get_condifence_matches(confidence)
number_matches = len(matches)
index_to_plot_1 = np.random.randint(0, number_matches)
index_to_plot_2 = np.random.randint(0, number_matches)
m1 = fm.matches.matches[index_to_plot_1][2]
m2 = fm.matches.matches[index_to_plot_2][2]
ymax = np.max([np.max(m1.values), np.max(m2.values)]) + 50
#string = '%d matches found' % number_matches
fig, (ax1, ax2) = plt.subplots(1,2, sharex=True,figsize=(13, 5))
plt.ylim(ymin=-200, ymax=ymax)
ax1.set(xlabel = 'Shift (cm$^-1$)')
ax1.set(ylabel='Intensity')
ax2.set(xlabel = 'Shift (cm$^-1$)')
ax2.set(ylabel='Intensity')
m1.plot(ax=ax1)
m2.plot(ax=ax2)