# Deep Structured Active Contours
## Active Contours.
Let's consider following image.<br>
![Imgur](https://i.imgur.com/NprbwMm.png)<br>

There are three colored shapes. We want to draw the boundary of only one of them. We are going to solve this problem using the <i>Active Contoues Method<i/> which is visualized below by drawing a small polygon inside the chosen shape and <i>evolving<i/> it.<br>
![Imgur](https://i.imgur.com/3o2u3mG.gif)
![Imgur](https://i.imgur.com/ZEE3uon.gif)
![Imgur](https://i.imgur.com/CyrZhW1.gif)<br>

We want our curve to be at the <i>edges<i/>(The places where the change of the image colors is high as in the image below) of the image.<br>
![Edges of the image](https://i.imgur.com/t5FGmJ1.png)<br>
In other words we look for a curve ![](https://latex.codecogs.com/svg.latex?u%3D%5C%7B%28x_1%2Cy_1%29%2C%28x_2%2Cy_2%29%2C...%2C%28x_n%2Cy_n%29%5C%7D) that <i>locally<i/> (because we only want the boundary of our shape even if it not the absolute maximum) maximizes<br>
<p align="center">
![aaa](https://latex.codecogs.com/svg.latex?L%3D%5Csum_%7Bi%3D1%7D%5En%5Ctextup%7BE%7D%28x_i%2Cy_i%29)
</p>
where ![](https://latex.codecogs.com/svg.latex?%5Ctextup%7BE%7D) is the edge map (the image above). To approximate this desired curve, we could use the simple and well-known <i>gradient descent<i/> with the function ![](https://latex.codecogs.com/svg.latex?-L)<br>
![](https://latex.codecogs.com/svg.latex?u_%7Bn&plus;1%7D%3Du_n&plus;%5Calpha%5Cnabla%20L)
However we quickly see that this will not work properly as in the middle of the shapes there is no change in color at all and so our small initial polygon will not evolve at all using the gradient descent. To fix this we define the <i>Balloon Force<i/>.<br>
  
At each vertics of the curve ![](https://latex.codecogs.com/svg.latex?u%3D%5C%7B%28x_1%2Cy_1%29%2C%28x_2%2Cy_2%29%2C...%2C%28x_n%2Cy_n%29%5C%7D) we define the normal vector![](https://latex.codecogs.com/svg.latex?n_i%3D%28y_%7Bi-1%7D-y_%7Bi&plus;1%7D%2Cx_%7Bi&plus;1%7D-x_%7Bi-1%7D%29) (or negative this vector depending on orientation). We then solve the following equation
![](https://latex.codecogs.com/svg.latex?u_%7Bn&plus;1%7D%3Du_n&plus;%5Calpha%5Cnabla%20L%20&plus;%5Cbeta%20n).
for appropriate constants ![](https://latex.codecogs.com/svg.latex?%5Calpha%2C%20%5Cbeta)
