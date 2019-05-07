# Active Contours.
Let's consider following image.<br>
<p align="center">
<img src= https://i.imgur.com/NprbwMm.png><br>
</p>

There are three colored shapes. Our first goal is draw the boundary of only one of the shapes which we are going to do using the **Active Contours Method**. The method is visualized below by starting from a small polygon inside the chosen shape and *evolving* it.<br>
<p align="center">
<img src= https://i.imgur.com/3o2u3mG.gif>
<img src= https://i.imgur.com/ZEE3uon.gif>
<img src= https://i.imgur.com/CyrZhW1.gif>
</p>

In other words we want to draw a curve as close as possible to the ![edges](https://en.wikipedia.org/wiki/Edge_detection) (The places where the change of the image colors is high as in the image below) of the chosen shape the image. <br>
<p align="center">
<img src= https://i.imgur.com/t5FGmJ1.png><br>
Image Edges (E)
</p>

We can look for a curve ![](https://latex.codecogs.com/svg.latex?u%3D%5C%7B%28x_1%2Cy_1%29%2C%28x_2%2Cy_2%29%2C...%2C%28x_n%2Cy_n%29%5C%7D) that *locally maximizes* (because we only want the boundary of our shape even if it not the absolute maximum)<br>
<p align="center">
<img src= https://latex.codecogs.com/svg.latex?L%3D%5Csum_%7Bi%3D1%7D%5En%5Ctextup%7BE%7D%28x_i%2Cy_i%29><br>
</p>

where ![](https://latex.codecogs.com/svg.latex?%5Ctextup%7BE%7D) is the edge map (the image above). To approximate this desired curve, we will use the simple and well-known ![gradient descent](https://en.wikipedia.org/wiki/Gradient_descent) with the function ![](https://latex.codecogs.com/svg.latex?-L). That is we consider the following sequence of curves with some initial curve ![](https://latex.codecogs.com/svg.latex?u_0) (this is the small polygon in our implementation)<br>

<p align="center">
<img src= https://latex.codecogs.com/svg.latex?u_%7Bk&plus;1%7D%3Du_k&plus;%5Calpha%5Cnabla%20L><br>
</p>

However we quickly see that this will not work properly as in the middle of the shapes there is no change in color at all and so our small initial polygon will not evolve at all using the gradient descent. To fix this we add a term that gives a push into the normal direction of the curve (<i>Balloon Force<i/>).<br>
  
At each vertix of the curve ![](https://latex.codecogs.com/svg.latex?u%3D%5C%7B%28x_1%2Cy_1%29%2C%28x_2%2Cy_2%29%2C...%2C%28x_n%2Cy_n%29%5C%7D) we define the normal vector![](https://latex.codecogs.com/svg.latex?N_i%20%3D%20%28y_%7Bi-1%7D-y_%7Bi+1%7D%2Cx_%7Bi&plus;1%7D-x_%7Bi-1%7D%29) (or negative this vector depending on orientation, and indices are taken modulo n). We then solve the following equation<br>
![](https://latex.codecogs.com/svg.latex?u_%7Bk&plus;1%7D%3Du_k&plus;%5Calpha%5Cnabla%20L%20&plus;%5Cbeta%20N)<br>
for appropriate choice of constants ![](https://latex.codecogs.com/svg.latex?%5Calpha%2C%20%5Cbeta).
