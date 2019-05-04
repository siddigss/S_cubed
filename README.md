# Deep Structured Active Contours
## Active Contours.
Let's consider following image.<br>
![Imgur](https://i.imgur.com/NprbwMm.png)<br>

There are three colored shapes. We want to draw the boundary of only one of them. We choose one and ask the computer to draw its boundaty.<br>

We are going to solve this problem using the <i>Active Contoues Method<i/> which is visualized below by drawing a small polygon inside the chosen shape and <i>evolving<i/> it.<br>
![Imgur](https://i.imgur.com/3o2u3mG.gif)
![Imgur](https://i.imgur.com/ZEE3uon.gif)
![Imgur](https://i.imgur.com/CyrZhW1.gif)<br>

We want our curve to be a the <i>edges<i/>(The places where the change of the image colors is high as in the image below) of the image.
![Edges of the image](https://i.imgur.com/t5FGmJ1.png)<br>
In other words we look for a curve if our curve ![](https://latex.codecogs.com/svg.latex?%5C%7B%28x_1%2Cy_1%29%2C%28x_2%2Cy_2%29%2C...%2C%28x_n%2Cy_n%29%5C%7D) that <i>locally<i/> (because we only want the boundary of our shape even if it not the absolute maximum) maximizes ![](https://latex.codecogs.com/svg.latex?%5Csum_%7Bi%3D1%7D%5En%5Ctextup%7BE%7D%28x_i%2Cy_i%29) where ![](https://latex.codecogs.com/svg.latex?%5Ctextup%7BE%7D) is the edge map (the image above). To approximate this desired curve, we could use the simple and well-known <i>gradient descent<i/> with the function ![](https://latex.codecogs.com/svg.latex?-%5Ctextup%7BE%7D)
