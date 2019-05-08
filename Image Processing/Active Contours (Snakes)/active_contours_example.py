import numpy as np
import scipy
from PIL import Image, ImageDraw, ImageFilter
import matplotlib.pyplot as plt
from matplotlib import cm
from active_contours import active_contours, add_vertices_to_curve

#Loding the image
Image_name='image.png'
Energy_img = Image.open(Image_name)

Energy_img_bw = Energy_img.convert(mode='L')                                         #Convert to Black and White (We don't need other colors for edge detection here)
Energy_img_bw = Energy_img_bw.filter(ImageFilter.FIND_EDGES)          #Edge filter
Energy_img_bw = Energy_img_bw.filter(ImageFilter.GaussianBlur(5))       #Bluring usually helps (the edges map is very localized otherwise).

Energy= np.asarray(Energy_img_bw, dtype='int32')                                     #Image to array
#plt.imshow(Energy_img)
#plt.show()

Number_of_edges = 30                                                                                                 #of the initial polygon

center_x = 500                                                                                                               #Setting the initial curve
center_y = 280
radius = 30
snake = np.array([center_y+radius*np.sin(np.linspace(0, 2*np.pi, Number_of_edges)), \
                  center_x+radius*np.cos(np.linspace(0, 2*np.pi, Number_of_edges))]).T          


pixel_factor = 1
fig = plt.figure()

while True:                                                                                                                      #Keep pressing SPACE BAR to see the evolution
    if plt.waitforbuttonpress():
        Energy_img2 = Image.open(Image_name)                                                         #Open a new image to draw the curve (snake) on it
        draw = ImageDraw.Draw(Energy_img2)
        snake_tuples = []
        for i in range(snake.shape[0]):
            snake_tuples.append((snake[i,1], snake[i,0]))
        snake_tuples.append((snake[0,1], snake[0,0]))
        draw.line(snake_tuples,  fill=(255,255,255), width=5)
        plt.imshow(Energy_img2)
        
        fig.show()
        del draw
        del Energy_img2
        snake_lengths = np.sqrt(np.sum((snake-np.roll(snake,1,axis=0))**2, axis = 1))  #Length of the curve.
        mean = np.mean(snake_lengths)                                                                             #Mean of curve edges length

        #print('std: ', np.std(snake_lengths))
        #print('mean: ', mean)
        snake = add_vertices_to_curve(snake, 1.5*mean, 0.5*mean)                            #Adding and deleteing vertices.
        snake = active_contours(-Energy, snake, 10, 1*pixel_factor, 1*pixel_factor)    #Evolution step


