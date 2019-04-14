import numpy as np
import scipy
import scipy.linalg
from PIL import Image, ImageDraw, ImageFilter, ImageMath
import matplotlib.pyplot as plt
import time
import PIL.ImageOps
import math

def active_contour(Energy_ext, alpha, beta, kappa, Time_step, \
                   Initial_snake, Number_of_iterations, Force_coefficient, Balloon_coefficient, h_=1, px=2, d0=0.0, d1=0.0, Method_of_solving = 'finite differences'):
    if Method_of_solving == 'finite differences':
        
        N=Initial_snake.shape[0]
        A=np.zeros((N,N))
        alpha = alpha[0,0] #alpha is tensor whose components all have the same value (just for similicty of the code)
        #
        for i in range(N):
            A[i,i]=2*alpha/h_
        for i in range(N): 
            A[i,(i+1)%N]= -alpha/h_
            A[(i+1)%N,i]= -alpha/h_

        #Gradient of the Image Energy
        Force = -np.array([np.gradient(Energy_ext, axis=0),np.gradient(Energy_ext, axis=1)])
        snake_r = Initial_snake

        for _ in range(Number_of_iterations):            
            snake = np.int32(snake_r)
            E_k_grad= np.zeros((N,2))

            #Gradient of E_k (local balloon force) calculations. The coming four loops (and if's) are to calcuate the intergals (over the triangles) in the paper.
            #Notice this Balloon Force expands the curve given it is oriented counter-clockwise. Otherwise the effect will be the opposite.
            for i in range(N):
                if not (snake[(i-1)%N, 1] == snake[i, 1]):
                    integtal_limit = abs(snake[(i-1)%N, 1]-snake[i, 1])
                    integtal_limit = int(integtal_limit)
                    for h in range(integtal_limit):
                        k = h / abs(snake[(i-1)%N, 1]-snake[i, 1])
                        E_k_grad[i,0] -=  (0.5 + h / (snake[(i-1)%N, 1]-snake[i, 1]))*kappa[int((1-k)*snake[(i-1)%N, 0]+k*snake[i,0]), int((1-k)*snake[(i-1)%N, 1]+k*snake[i,1])]

                if not (snake[(i+1)%N, 1] == snake[i, 1]):
                    integtal_limit = abs(snake[(i+1)%N, 1]-snake[i, 1])
                    integtal_limit = int(integtal_limit)
                    for h in range(integtal_limit):
                        k = h / abs(snake[(i+1)%N, 1]-snake[i, 1])
                        E_k_grad[i,0] +=  (0.5 + h / (snake[(i+1)%N, 1]-snake[i, 1]))*kappa[int((1-k)*snake[(i+1)%N, 0]+k*snake[i,0]), int((1-k)*snake[(i+1)%N, 1]+k*snake[i,1])]


            for i in range(N):
                if not snake[(i-1)%N, 0] == snake[i, 0]:
                    integtal_limit = abs(snake[(i-1)%N, 0]-snake[i, 0])
                    integtal_limit = int(integtal_limit)
                    for h in range(integtal_limit):
                        k = h / abs(snake[(i-1)%N, 0]-snake[i, 0])
                        E_k_grad[i,1] +=  (0.5 + h / (snake[(i-1)%N, 0]-snake[i, 0]))*kappa[int((1-k)*snake[(i-1)%N, 0]+k*snake[i,0]), int((1-k)*snake[(i-1)%N, 1]+k*snake[i,1])]

                if not (snake[(i+1)%N, 0] == snake[i, 0]):
                    integtal_limit = abs(snake[(i+1)%N, 0]-snake[i, 0])
                    integtal_limit = int(integtal_limit)
                    for h in range(integtal_limit):
                        k = h / abs(snake[(i+1)%N, 0]-snake[i, 0])
                        E_k_grad[i,1] -= (0.5 + h / (snake[(i+1)%N, 0]-snake[i, 0]))*kappa[int((1-k)*snake[(i+1)%N, 0]+k*snake[i,0]), int((1-k)*snake[(i+1)%N, 1]+k*snake[i,1])]

            #The gradient just calculated depends on the length of the edges. This loop is to normalize this factor.
            for i in range(N):
                if not ( np.linalg.norm(snake[(i-1)%N,:] - snake[(i+1)%N,:]) == 0 ):
                    E_k_grad[i,:] = E_k_grad[i,:] / np.linalg.norm(snake[(i-1)%N,:] - snake[(i+1)%N,:])

            #A=A+B as in the paper. However in the paper h_=1.
            for i in range(N):
                A[i,i] = A[i,i] + (beta[snake[(i-1)%N,0],snake[(i-1)%N,1]] + \
                            4*beta[snake[i,0],snake[i,1]] + beta[snake[(i+1)%N,0],snake[(i+1)%N,1]])/(h_*h_)

            for i in range(N): 
                A[i,(i+1)%N] = A[i,(i+1)%N] + (- 2*beta[snake[(i+1)%N,0],snake[(i+1)%N,1]] - \
                            2*beta[snake[i,0],snake[i,1]])/(h_*h_)
                A[(i+1)%N,i] = A[(i+1)%N,i] + (- 2*beta[snake[(i-1)%N,0],snake[(i-1)%N,1]] - \
                            2*beta[snake[i,0],snake[i,1]])/(h_*h_)

            for i in range(N): 
                A[i,(i+2)%N] = A[i,(i+2)%N] + beta[snake[(i+1)%N,0],snake[(i+1)%N,1]]/(h_*h_)
                A[(i+2)%N,i] = A[(i+2)%N,i] + beta[snake[(i-1)%N,0],snake[(i-1)%N,1]]/(h_*h_)

            #Solving a bit modified version (and hopefully more regular) of the discretized Active Contour linear equation.
            d0 = px*np.tanh(Time_step* \
                              (Force_coefficient*Force[0,snake[:,0], snake[:,1]]+ Balloon_coefficient*E_k_grad[:,0]))*0.5 + d0*0.5
            
            snake_0 = np.linalg.solve(np.identity(N) + 2*Time_step*A, snake_r[:,0] + d0)

            d1 = px*np.tanh(Time_step* \
                              (Force_coefficient*Force[1,snake[:,0], snake[:,1]] + Balloon_coefficient*E_k_grad[:,1]))*0.5 + d1*0.5
            snake_1 = np.linalg.solve(np.identity(N) + 2*Time_step*A, snake_r[:,1] + d1)
            #Final result rounded to integers within the image dimensions.
            for i in range(N):
                snake_r[i,0] = snake_0[i]
                snake_r[i,1] = snake_1[i]
                if snake_r[i,0] < 0:
                    snake_r[i,0]=0
                if snake_r[i,0] >= Energy_ext.shape[0]:
                    snake_r[i,0] = Energy_ext.shape[0]-1
                if snake_r[i,1] < 0:
                    snake_r[i,1]=0
                if snake_r[i,1] >= Energy_ext.shape[1]:
                    snake_r[i,1] = Energy_ext.shape[0]-1

        return snake_r
    return None
