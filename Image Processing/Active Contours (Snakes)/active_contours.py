import numpy as np

def active_contours(Energy, Initial_snake, Number_of_iterations, Balloon_coefficient, Force_coefficient):
    N=Initial_snake.shape[0]
    snake = np.zeros((N,2), dtype=np.int)
    for i in range(N):
        snake[i,0] = 0 if 0 > int(Initial_snake[i,0]) else (Energy.shape[0]-1 if int(Initial_snake[i,0]) >= Energy.shape[0] else int(Initial_snake[i,0]))
        snake[i,1] = 0 if 0 > int(Initial_snake[i,1]) else (Energy.shape[1]-1 if int(Initial_snake[i,1]) >= Energy.shape[1] else int(Initial_snake[i,1]))

    snake_ = np.copy(Initial_snake)
    Force = -np.array([np.gradient(Energy, axis=0),np.gradient(Energy, axis=1)])
    for _ in range(Number_of_iterations):
            
        normal = np.zeros((N,2))
        for i in range (N):
            if  not (snake [(i-1)%N,0] == snake[(i+1)%N,0] and snake [(i+1)%N,1]==snake[(i-1)%N,1]):
                normal[i,0] = (snake [(i+1)%N,1]-snake[(i-1)%N,1]) / np.linalg.norm([snake [(i-1)%N,0]-snake[(i+1)%N,0],snake [(i+1)%N,1]-snake[(i-1)%N,1] ])
                normal[i,1] = (snake [(i-1)%N,0]-snake[(i+1)%N,0]) / np.linalg.norm([snake [(i-1)%N,0]-snake[(i+1)%N,0],snake [(i+1)%N,1]-snake[(i-1)%N,1] ])
            else:
                normal[i,0] = 0
                normal[i,1] = 0
        normal = - normal

        snake_ = snake_ + Force_coefficient*Force[:,snake[:,0], snake[:,1]].T + Balloon_coefficient*normal

        snake_ = np.around(snake_)
        for i in range(N):
            snake[i,0] = 0 if 0 > int(snake_[i,0]) else (Energy.shape[0]-1 if int(snake_[i,0]) >= Energy.shape[0] else int(snake_[i,0]))
            snake[i,1] = 0 if 0 > int(snake_[i,1]) else (Energy.shape[1]-1 if int(snake_[i,1]) >= Energy.shape[1] else int(snake_[i,1]))
    return snake

def add_vertices_to_curve(curve, length1, length2):
    N = curve.shape[0]
    new_curve = np.array([curve[0,:]])
    for i in range(N):
        if (np.sqrt((curve[i,0]-curve[(i+1)%N, 0])**2 + (curve[i,1]-curve[(i+1)%N, 1])**2 ) > length1):
            new_curve = np.append(new_curve, (curve[i,:] + curve[(i+1)%N, :])/ 2)
        if ((not (i==N-1)) and (np.sqrt((curve[i,0]-curve[(i+1)%N, 0])**2 + (curve[i,1]-curve[(i+1)%N, 1])**2 ) > length2)):
             new_curve = np.append(new_curve, curve[(i+1)%N,:])
             
    new_curve2 = np.zeros((new_curve.shape[0]//2, 2))
    
    for i in range(new_curve.shape[0]):
        if(i%2==0):
            new_curve2[i//2,0] = new_curve[i]
        else:
            new_curve2[i//2,1] = new_curve[i]
    
    return new_curve2


