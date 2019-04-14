import numpy as np
import scipy
import scipy.linalg
from PIL import Image, ImageDraw, ImageFilter
import matplotlib.pyplot as plt
import time
import PIL.ImageOps
from Active_contour import active_contour

def active_contour_original(Energy_ext, Method_of_solving, A, Time_step, Initial_snake, Number_of_iterations, Balloon_coefficient, Force_coefficient):
    if Method_of_solving == 'finite differences':
        N=Initial_snake.shape[0]
        snake = np.zeros((N,2), dtype=np.int)
        snake2 = Initial_snake
        snake2=np.around(snake2)
        for i in range(N):
            snake[i,0] = 0 if 0 > int(snake2[i,0]) else (Energy_ext.shape[0]-1 if int(snake2[i,0]) >= Energy_ext.shape[0] else int(snake2[i,0]))
            snake[i,1] = 0 if 0 > int(snake2[i,1]) else (Energy_ext.shape[1]-1 if int(snake2[i,1]) >= Energy_ext.shape[1] else int(snake2[i,1]))


        Force = -np.array([np.gradient(Energy_ext, axis=0),np.gradient(Energy_ext, axis=1)])
        print(np.max(Force))
        snake_ = np.zeros((N,2))
        for _ in range(Number_of_iterations):
            
            Balloon_force = np.zeros((N,2))
            for i in range (N):
                if  not (snake [(i-1)%N,0] == snake[(i+1)%N,0] and snake [(i+1)%N,1]==snake[(i-1)%N,1]):
                    Balloon_force[i,0] = (snake [(i+1)%N,1]-snake[(i-1)%N,1]) / np.linalg.norm([snake [(i-1)%N,0]-snake[(i+1)%N,0],snake [(i+1)%N,1]-snake[(i-1)%N,1] ])
                    Balloon_force[i,1] = (snake [(i-1)%N,0]-snake[(i+1)%N,0]) / np.linalg.norm([snake [(i-1)%N,0]-snake[(i+1)%N,0],snake [(i+1)%N,1]-snake[(i-1)%N,1] ])
                else:
                    Balloon_force[i,0] = 0
                    Balloon_force[i,1] = 0
            Balloon_force = - Balloon_force

            snake_[:,0] = np.linalg.solve(np.identity(N) + Time_step*A,\
                                          snake[:,0] + Time_step*
                              (Force_coefficient*Force[0,snake[:,0], snake[:,1]] + Balloon_coefficient*Balloon_force[:,0]))

            snake_[:,1] = np.linalg.solve(np.identity(N) + Time_step*A,\
                                          snake[:,1] + Time_step*
                              (Force_coefficient*Force[1,snake[:,0], snake[:,1]] + Balloon_coefficient*Balloon_force[:,1]))

            snake_ = np.around(snake_)
            for i in range(N):
                snake[i,0] = 0 if 0 > int(snake_[i,0]) else (Energy_ext.shape[0]-1 if int(snake_[i,0]) >= Energy_ext.shape[0] else int(snake_[i,0]))
                snake[i,1] = 0 if 0 > int(snake_[i,1]) else (Energy_ext.shape[1]-1 if int(snake_[i,1]) >= Energy_ext.shape[1] else int(snake_[i,1]))
        return snake
    return None

def onclick(event):
    global ix, iy
    ix, iy = event.xdata, event.ydata
    print(ix,iy)

    global coords
    coords.append([int(iy), int(ix)])

    if len(coords) == Number_of_edges:
        fig.canvas.mpl_disconnect(cid)

    return coords

Image_name='lips.png'
Energy_ext_img = Image.open(Image_name)
Energy_ext_img_bw = Energy_ext_img.convert(mode='L')
Energy_ext_img_bw = Energy_ext_img_bw.filter(ImageFilter.FIND_EDGES)
Energy_ext_img_bw = PIL.ImageOps.invert(Energy_ext_img_bw)
Energy_ext_img_bw = Energy_ext_img_bw.filter(ImageFilter.GaussianBlur(5))
Energy_ext_img_bw.load()
Energy_ext = np.asarray(Energy_ext_img_bw, dtype='int32')
#Energy_ext[Energy_ext>200]=255
#for i in range(10):
#    Energy_ext[i,:]=255
#    Energy_ext[Energy_ext.shape[0]-1-i,:]=255
#    Energy_ext[:,i]=255
#    Energy_ext[:,Energy_ext.shape[1]-i-1]=255
#Image.fromarray(np.asarray(Energy_ext, dtype='uint8'), mode='L').show()
#plt.imshow(Energy_ext)
#plt.colorbar()
#plt.show()

Number_of_edges = 20
Time_step = 1 #0.01
pixel_factor = 1

coords=[]
fig = plt.figure()
plt.imshow(Energy_ext_img)
fig.show()
cid = fig.canvas.mpl_connect('button_press_event', onclick)
boolean = False
while True:
   if plt.waitforbuttonpress():
       break

h=  (2*max(Energy_ext.shape[0],Energy_ext.shape[1])/Number_of_edges)**2
a=0.1
b=0.1

A=np.zeros((Number_of_edges,Number_of_edges))
for i in range(Number_of_edges):
    A[i,i]=2*a/(h*h) + 6*b/(h*h*h)
for i in range(Number_of_edges-1):
    A[i,i+1]=-a/(h*h) -4*b/(h*h*h*h)
    A[i+1,i]=-a/(h*h) -4*b/(h*h*h*h)
for i in range(Number_of_edges-2):
    A[i,i+2]=b/(h*h*h*h)
    A[i+2,i]=b/(h*h*h*h)


snake = np.array(coords)
while True:
    if plt.waitforbuttonpress():
        Energy_ext_img2 = Image.open(Image_name)
        Energy_ext_img2.load()
        draw = ImageDraw.Draw(Energy_ext_img2)
        snake_tuples = []
        for i in range(Number_of_edges):
            snake_tuples.append((snake[i,1], snake[i,0]))
        snake_tuples.append((snake[0,1], snake[0,0]))
        draw.line(snake_tuples,  fill=(0,255,0), width=1)
        plt.imshow(Energy_ext_img2)
        fig.show()
        del draw

        #To apply the local version of Ballon Force (This commented function), the curve is oriented counter-clockwise.
        #snake = active_contour(Energy_ext, a*np.ones((Energy_ext.shape[0], Energy_ext.shape[1])),\
               #                     b*np.ones((Energy_ext.shape[0], Energy_ext.shape[1])), np.ones((Energy_ext.shape[0], Energy_ext.shape[1])),\
              #                       Time_step, snake, 1, 5*pixel_factor*1/Time_step, \
                #               Balloon_coefficient =0.1*pixel_factor*1/Time_step, \
                 #              h_ = (2*max(Energy_ext.shape[0],Energy_ext.shape[1])/Number_of_edges)**2, px=2)

        #For the global version the curve is oriented clockwise.
        snake = active_contour_original(Energy_ext, 'finite differences', A,\
                                    Time_step, snake, 1, 1*pixel_factor*1/Time_step, 1*pixel_factor*1/Time_step)
