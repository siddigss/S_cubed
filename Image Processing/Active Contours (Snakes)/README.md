# Active Contours.

Let's consider following image.<br>

<p align="center">
<img src= https://i.imgur.com/NprbwMm.png><br>
</p>

There are three colored shapes. Our first goal is draw the boundary of only one of the shapes which we are going to do using the **Active Contours Method**. The method is visualized below by starting from a small polygon inside the chosen shape and *evolving* it.<br>

<p align="center">
<img src= "https://media.giphy.com/media/htQzYHvO9UdMgLmkMF/giphy.gif"  width="250">
<img src= "https://media.giphy.com/media/hWp6k4Lw18YQvMBt9n/giphy.gif" width="250">
<img src= "https://media.giphy.com/media/W0c6dU1TD6XQcA5Dtz/giphy.gif" width="250">
</p>

In other words we want to draw a curve as close as possible to the [edges](https://en.wikipedia.org/wiki/Edge_detection) (The places where the change of the image colors is high as in the image below) of the chosen shape the image. <br>

<p align="center">
<img src= https://i.imgur.com/t5FGmJ1.png><br>
Image Edges (E)
</p>

We can look for a curve ![](https://latex.codecogs.com/svg.latex?u%3D%5C%7B%28x_1%2Cy_1%29%2C%28x_2%2Cy_2%29%2C...%2C%28x_n%2Cy_n%29%5C%7D) that *locally maximizes* (because we only want the boundary of our shape even if it not the absolute maximum)<br>

<p align="center">
<img src= https://latex.codecogs.com/svg.latex?L%3D%5Csum_%7Bi%3D1%7D%5En%5Ctextup%7BE%7D%28x_i%2Cy_i%29><br>
</p>

where ![](https://latex.codecogs.com/svg.latex?%5Ctextup%7BE%7D) is the edge map as in the image above.  To approximate this desired curve, we will use the simple and well-known [gradient descent](https://en.wikipedia.org/wiki/Gradient_descent) with the function ![](https://latex.codecogs.com/svg.latex?-L). That is we consider a sequence of curves ![](https://latex.codecogs.com/svg.latex?%28u_k%29_%7Bk%5Cin%5Cmathbb%7BN%7D%5Ccup%5C%7B0%5C%7D%7D)  with some initial curve ![](https://latex.codecogs.com/svg.latex?u_0) (this is the small polygon in our implementation) following the recursion<br>

<p align="center">
<img src= https://latex.codecogs.com/svg.latex?u_%7Bk&plus;1%7D%5E%7B%28i%29%7D%3Du_k%5E%7B%28i%29%7D&plus;%5Calpha%5Cnabla%20L%28u_k%5E%7B%28i%29%7D%29><br>
</p>

for every vertix ![](https://latex.codecogs.com/svg.latex?u%5E%7B%28i%29%7D). For simplicity of notations we will write this equation as

<p align="center">
<img src= https://latex.codecogs.com/svg.latex?u_%7Bk&plus;1%7D%3Du_k&plus;%5Calpha%5Cnabla%20L><br>
</p>

However we quickly see that this will not work properly as in the middle of the shapes there is no change in color at all and hence our small initial polygon will not evolve at all using the gradient descent. To fix this we add a term that gives a push into the normal direction of the curve (*Balloon Force*). To this end we define at each vertix of the curve ![](https://latex.codecogs.com/svg.latex?u%3D%5C%7B%28x_1%2Cy_1%29%2C%28x_2%2Cy_2%29%2C...%2C%28x_n%2Cy_n%29%5C%7D) the *normal vector*
<p align="center">
<img src= https://latex.codecogs.com/svg.latex?N_i%20%3D%20%5Cpm%5Cfrac%7B1%7D%7B%7C%7C%28y_%7Bi-1%7D-y_%7Bi&plus;1%7D%2Cx_%7Bi&plus;1%7D-x_%7Bi-1%7D%29%7C%7C%7D%28y_%7Bi-1%7D-y_%7Bi&plus;1%7D%2Cx_%7Bi&plus;1%7D-x_%7Bi-1%7D%29><br>
</p>

the sign depends on orientation (clockwise or anti-clockwise) and indices are taken modulo n.<br>
We now *evolve* our initial curve according to the following recursion<br>
<p align="center">
<img src= https://latex.codecogs.com/svg.latex?%5Clarge%20u_%7Bk&plus;1%7D%20%3D%20u_k%20&plus;%20%5Calpha%5Cnabla%20L%20&plus;%20%5Cunderbrace%7B%5Cbeta%20N%7D_%7B%5Ctextup%7BBalloon%7D%7D><br>
</p>

for appropriate choice of constants ![](https://latex.codecogs.com/svg.latex?%5Calpha%2C%20%5Cbeta).<br>

After implementing with different ![](https://latex.codecogs.com/svg.latex?%5Calpha%2C%5Cbeta), we notice two bad scenarios. We may overshoot the edges if the ballon force was very stronger or the *force* at the edges induced from ![](https://latex.codecogs.com/svg.latex?%5Ctextup%7BE%7D) pushes back the curve and messes it. To remedey this we will *delocalize* ![](https://latex.codecogs.com/svg.latex?%5Ctextup%7BE%7D) by bluring it with a Gaussian. This will increase the effective range of ![](https://latex.codecogs.com/svg.latex?%5Ctextup%7BE%7D) and smoothen its force.

<p align="center">
<img src= https://imgur.com/GR8vn46.png><br>
<sub>Implemention with <img src= "https://latex.codecogs.com/svg.latex?%5Calpha%3D%5Cbeta%3D1" width="60"></sub>
</p>

From this image we see that the curve is not *smooth* enough. As we can see in the picture some edges are longer than others. Indeed the mean edge length in our curve is `7.77` while the standard devaition is `14`. This indicates that some vertices are getting closer and some are getting further. A quick fix for this is check our curve after every few gradient descent iterations to delete the short edges and add additional vertices in the middle of the long edges. Indeed implementing this idea reduced the standard variation to `1.18` with mean `5.16` and the number of vertices increased to `179` as opposed to the fixed number of edges we started with `100`.

<p align="center">
<img src= "https://imgur.com/6Ai9XjC.png" width="300"> <img src= "https://imgur.com/R6VlCDx.png" width="300"><br>
<sub>In this implementation short and long edges are defined to be those the are shorter than half the mean length and those that are longer than one half the mean length respectively.</sub>
</p>

This looks much better! If we now look at the boundary of the blue shape above, we see that there is an unnecessary part we would like to get rid of. decreasing the number of vertices we start with improves the results.

<p align="center">
<img src= "https://media.giphy.com/media/htQzYHvO9UdMgLmkMF/giphy.gif"  width="250">
<img src= "https://media.giphy.com/media/hWp6k4Lw18YQvMBt9n/giphy.gif" width="250">
<img src= "https://media.giphy.com/media/W0c6dU1TD6XQcA5Dtz/giphy.gif" width="250"><br>
<sub>Number of vertices of the the initial polygon = `30` and <img src= "https://latex.codecogs.com/svg.latex?%5Calpha%3D%5Cbeta%3D1" width="60"></sub>
</p>

Let's try it with some other shapes

<p align="center">
<img src= "https://media.giphy.com/media/J4h9bxfsBjoEFnWo39/giphy.gif" width="250"><br>
<sub>Same parameters as in the previous three images</sub>
</p>

We see that our method works nicely in these simple settings.

To be continued ... つづく ...
