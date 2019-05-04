# Deep Structured Active Contours
## Active Contours.
Let's consider following image.<br>
![Imgur](https://i.imgur.com/NprbwMm.png)<br>

There are three colored shapes. We want to draw the boundary of only one of them. We choose one and ask the computer to draw its boundaty.<br>

We are going to solve this problem using the <i>Active Contoues Method<i/> which is visualized below by drawing a small polygon inside the chosen shape and <i>evolving<i/> it.<br>
![Imgur](https://i.imgur.com/3o2u3mG.gif)
![Imgur](https://i.imgur.com/ZEE3uon.gif)
![Imgur](https://i.imgur.com/CyrZhW1.gif)<br>

By evolution of a curve we mean a sequence of curves ![](https://latex.codecogs.com/svg.latex?u_0%2Cu_1%2Cu_2%2C....)
We want the curve to get closer to the <i>edges<i/>(The places where the gradient of the image is high) of the image. 
