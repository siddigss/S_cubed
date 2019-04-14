import numpy as np
import matplotlib.pyplot as plt
import imageio
from PIL import Image, ImageDraw
import csv
from snake_utils import CNN_B
import tensorflow as tf

L=20
im_size = 64
out_size = 64
numfilt = [32,64,128,128]
data_path = os.getcwd() + '\\single_buildings\\'
model_path = os.getcwd() + '\\models\\'
csvfile_pred = open(model_path+'results\\polygons.csv', newline='')
csvfile_truth = open(data_path+'building_coords.csv', newline='')

reader_pred = csv.reader(csvfile_pred)
reader_truth = csv.reader(csvfile_truth)

img_number = 436
img_size = 64

for _ in range(img_number - 335):
    reader_pred.__next__()

for _ in range(img_number):
    reader_truth.__next__()

true_curve = reader_truth.__next__()
pred_curve = reader_pred.__next__()

true_tuples= []
for i in range(4):
    true_tuples.append((int(float(true_curve[1+2*i])), int(float(true_curve[2+2*i]))))
true_tuples.append(true_tuples[0])

pred_tuples = []
for i in range(L):
    pred_tuples.append((int(float(pred_curve[1+2*i])), int(float(pred_curve[2+2*i]))))
pred_tuples.append(pred_tuples[0])

image = Image.open(data_path + 'building_'+str(img_number)+'.png')

draw = ImageDraw.Draw(image)

draw.line(true_tuples, fill = (0,0,255), width = 1)
draw.line(pred_tuples, fill = (0,255,0), width = 1)

del draw

#Show Energy
#CNN structure
tvars, grads, predE, predA, predB, predK, l2loss, grad_predE, \
    grad_predA, grad_predB, grad_predK, grad_l2loss, x, y_ = CNN_B(im_size, out_size, L,
    batch_size=1,wd=0.01,layers=len(numfilt),numfilt=numfilt,E_blur=2,stack_from=0)


#Initialize the CNN and its variables.

with tf.Session(config=tf.ConfigProto(allow_soft_placement=True,log_device_placement=True)) as sess:
    saver = tf.train.Saver()
    save_path = tf.train.latest_checkpoint(model_path)
    init = tf.global_variables_initializer()
    sess.run(init)
    if save_path is not None:
        saver.restore(sess,save_path)

    #plot the image.
    plt.subplot(121)
    plt.imshow(image)
    #plot the Energy.
    batch = np.zeros((im_size,im_size,3,1))
    batch[:,:,:,0] = image
    [Energy] = sess.run([predE], feed_dict = {x: batch})
    plt.subplot(122)
    plt.imshow(Energy[:,:,0,0])
    plt.colorbar()
    plt.show()










