import tensorflow as tf
import numpy as np
import csv
import os
from active_contours_fast import draw_poly,derivatives_poly,draw_poly_fill, active_contour_step
from snake_utils import imrotate, plot_snakes, CNN_B, snake_graph
from scipy import interpolate
from skimage.filters import gaussian
import time
import matplotlib.pyplot as plt
import Active_contour
import imageio

model_path = 'models2/'
do_train = False
L = 30

#Load data

if do_train:
    num_ims = 100
    push=0+1
else:
    num_ims = 68
    push = 100+1
numfilt = [32,64,128,128,256,256]
batch_size = 1
im_size = 512
out_size = 256 #output size of the CNN result.

data_path = os.getcwd() + '\\buildings\\'

images = np.zeros([im_size,im_size,3,num_ims])
ground_thruths = np.zeros([L,2,num_ims])

#csv reader to read the ground truths.
csvfile=open(data_path+'polygons.csv', newline='')
reader = csv.reader(csvfile)


for i in range(num_ims):
    # interpolation to increase the number of vertices of ground truths to L
    corners = reader.__next__()
    number_of_edges = int(corners[0])
    poly = np.zeros([number_of_edges+1, 2])
    for c in range(number_of_edges):
        poly[c, 0] = np.float(corners[1+2*c])*out_size/im_size
        poly[c, 1] = np.float(corners[2+2*c])*out_size/im_size
    poly[number_of_edges,:] = poly[0,:]
    curve = []
    for c in range(number_of_edges):
        number_of_vertices = L//number_of_edges + min(1,max(L%number_of_edges - c,0))
        for j in range(number_of_vertices):
            curve.append(poly[c,:] + (j/number_of_vertices)*(poly[c+1,:]-poly[c,:]))
    ground_thruths[:,:,i] = np.array(curve)
    #loading images
    images[:,:,:,i] = np.float32(imageio.imread(data_path+'building_'+str(push+i).zfill(3)+'.tif'))/255

#adjusting for images boundaries
ground_thruths = np.minimum(ground_thruths, im_size-1)
ground_thruths = np.maximum(ground_thruths, 0)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~DEFINE CNN ARCHITECTURE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print('Creating CNN...',flush=True)
with tf.device('/gpu:0'):
    tvars, grads, predE, predA, predB, predK, l2loss, grad_predE, \
    grad_predA, grad_predB, grad_predK, grad_l2loss, x, y_ = CNN_B(im_size, out_size, L,
    batch_size=1,wd=0.01,layers=len(numfilt),numfilt=numfilt,E_blur=2,stack_from=0)

optimizer = tf.train.AdamOptimizer(1e-4, epsilon=1e-7)
apply_gradients = optimizer.apply_gradients(zip(grads, tvars))


#Prepare folder to save network
start_epoch = 0
if not os.path.isdir(model_path):
    os.makedirs(model_path)

if not do_train and not os.path.isdir(model_path+'results'):
    os.makedirs(model_path+'results')
elif os.path.isdir(model_path+'results/polygons.csv'):
    os.remove(model_path+'results/polygons.csv')

# Add ops to save and restore all the variables.
saver = tf.train.Saver()



#~~~~~~DEFINE EPOCH~~~~~~
def epoch(n,i,mode):
    # mode (str): train or test
    batch_ind = np.arange(i,i+batch_size)
    batch = np.float32(np.copy(images[:, :, :, batch_ind]))
    thisGT = np.copy(ground_thruths[:, :, batch_ind[0]])
    if mode is 'train':
        ang = np.random.rand() * 360
        for j in range(len(batch_ind)):
            for b in range(batch.shape[2]):
                batch[:, :, b, j] = imrotate(batch[:, :, b, j], ang)
        R = [[np.cos(ang * np.pi / 180), np.sin(ang * np.pi / 180)],
             [-np.sin(ang * np.pi / 180), np.cos(ang * np.pi / 180)]]
        thisGT -= out_size / 2
        thisGT = np.matmul(thisGT, R)
        thisGT += out_size / 2
        thisGT = np.minimum(thisGT, out_size - 1)
        thisGT = np.maximum(thisGT, 0)
    [mapE, mapA, mapB, mapK, l2] = sess.run([predE, predA, predB, predK, l2loss], feed_dict={x: batch})

    mapA = np.maximum(mapA, 0)
    mapB = np.maximum(mapB, 0)
    mapK = np.maximum(mapK, 0)

    s = np.linspace(0, 2 * np.pi, L)
    init_u = out_size / 2 + 20 * np.cos(s)
    init_v = out_size / 2 + 20 * np.sin(s)
    init_snake = np.array([init_u, init_v]).T
    for j in range(batch_size):
        snake = Active_contour.active_contour(mapE[:,:,0,j], mapA[:,:,0,j], mapB[:,:,0,j], -mapK[:,:,0,j], 1, \
                  init_snake, 100, Force_coefficient = 1, Balloon_coefficient = -1, h_= (3*out_size / L)**2, px=1, d0=0.0, d1=0.0)        

        M = mapE.shape[0]
        N = mapE.shape[1]
        print(M, " ",N)
        der1, der2 = derivatives_poly(snake)

        der1_GT, der2_GT = derivatives_poly(thisGT)
        grads_arrayE = mapE*0.0 # A tensor of the same dimensions filled with zeros.
        grads_arrayA = mapA*0.0
        grads_arrayB = mapB*0.0
        grads_arrayK = mapK*0.0
        grads_arrayE[:, :, 0, j] = -(draw_poly(snake, 1, [M, N],4) - draw_poly(thisGT, 1, [M, N],4))
        grads_arrayA[:, :, 0, j] = -(np.mean(der1) - np.mean(der1_GT))
        grads_arrayB[:, :, 0, j] = -(draw_poly(snake, der2, [M, N],4) - draw_poly(thisGT, der2_GT, [M, N],4))
        mask_gt = draw_poly_fill(thisGT, [M, N])
        mask_snake = draw_poly_fill(snake, [M, N])
        grads_arrayK[:, :, 0, j] = -(mask_gt - mask_snake)

        #plt.subplot(121)
        #plt.imshow(batch[:,:,:,j])
        #plt.show()
        #plt.imshow(draw_poly(thisGT, 1, [M, N],4))
        #plt.show()
        #plt.imshow(draw_poly_fill(thisGT, [M, N]))
        #plt.show()
        #plt.subplot(122)
        #plt.imshow(mapE[:,:,0,0])
        #plt.colorbar()
        #plt.show()

        intersection = (mask_gt+mask_snake) == 2
        union = (mask_gt + mask_snake) >= 1
        iou = np.sum(intersection) / np.sum(union)
        area_gt = np.sum(mask_gt>0)
        area_snake = np.sum(mask_snake > 0)
        print('Area ratio: ', area_snake/area_gt)

    if mode is 'train':
        tic = time.time()
        apply_gradients.run(
            feed_dict={x: batch, grad_predE: grads_arrayE, grad_predA: grads_arrayA, grad_predB: grads_arrayB,
                       grad_predK: grads_arrayK, grad_l2loss: 1})
    return iou,area_gt,area_snake,snake


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~RUN THE TRAINING~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
with tf.Session(config=tf.ConfigProto(allow_soft_placement=True,log_device_placement=True)) as sess:

    save_path = tf.train.latest_checkpoint(model_path)
    init = tf.global_variables_initializer()
    sess.run(init)
    if save_path is not None:
        saver.restore(sess,save_path)
        start_epoch = int(save_path.split('-')[-1].split('.')[0])+1

    if do_train:
        end_epoch = 20
    else:
        end_epoch = start_epoch + 1
        polygons_csvfile = open(model_path + 'results/' 'polygons.csv', 'a', newline='')
        polygons_writer = csv.writer(polygons_csvfile)

    for n in range(start_epoch,end_epoch):
        iou_test = 0
        iou_train = 0
        iter_count = 0
        if do_train:
            for i in range(0,num_ims,batch_size):
                #print(i)
                #Do CNN inference
                new_iou, new_area_gt, new_area_snake, snake = epoch(n,i,'train')
                iou_train += new_iou
                iter_count += 1
                print('*********************************************')
                print('Train. Epoch ' + str(n) + '. Iter ' + str(iter_count) + '/' + str(num_ims) + ', IoU = %.2f' % (
                iou_train / iter_count))
                print('*********************************************')
            iou_train /= num_ims

            saver.save(sess,model_path+'model', global_step=n)
        iter_count = 0
        areas_gt = []
        areas_snake = []
        for i in range(num_ims):
            new_iou, new_area_gt, new_area_snake, snake = epoch(n,i, 'test')
            if not do_train:
                list_to_write = [len(snake)]
                snake = np.reshape(snake, 2 * len(snake)).tolist()
                for el in snake:
                    list_to_write.append(el)
                polygons_writer.writerow(list_to_write)
            areas_gt.append(new_area_gt)
            areas_snake.append(new_area_snake)
            iou_test += new_iou
            iter_count += 1
            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            print('Test. Epoch ' + str(n) + '. Iter ' + str(iter_count) + '/' + str(num_ims) + ', IoU = %.2f' % (
            iou_test / iter_count))
            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        areas_gt = np.stack(areas_gt)
        areas_snake = np.stack(areas_snake)
        diff = areas_gt - areas_snake
        rmse = np.sqrt(np.sum(diff ** 2) / len(diff))
        print(rmse)
        iou_test /= num_ims
        if not do_train:
            iou_csvfile = open(model_path + 'iuo_train_test.csv', 'a', newline='')
            iou_writer = csv.writer(iou_csvfile)
            iou_writer.writerow([n,iou_train,iou_test])
            iou_csvfile.close()
            polygons_csvfile.close()




