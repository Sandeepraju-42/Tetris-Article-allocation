Python 3D bin packing “Tetris” algorithm

The py3dbp package (https://github.com/enzoruiz/3dbinpacking) optimally packs cuboid items into a 3D rectangular box solving an ‘NP-Hard’ problem using computer solvers, which otherwise is practically impossible. 
The basic premise of the algorithm is as follows:
For a finite set of items i, with three dimensions wi, di, and hi corresponding to item width, depth, and height 
Items can rotate orthogonally, meaning swapping the sides with Width (wi), Depth (di), and Height (hi) in specific manners as provided below

![image](https://github.com/user-attachments/assets/81288b0a-3df4-4881-bc66-6c02511024b1)
![image](https://github.com/user-attachments/assets/f85e058e-ca78-4187-9a33-08025ddd293a)



Concept Problem formula
- Problem statement: All items must fit into bins 
- Below are the solver constraints: The total summation volumes of all items must be less than or equal to the bin volume
-       ∑(𝑤𝑖 ∗ℎ𝑖 ∗𝑑𝑖) ≤ 𝑊 ∗𝐷 ∗𝐻
- The bin volume and the total volume difference should be minimized
-       (𝑾∗𝑯∗𝑫) = ∑(𝑤𝑖 ∗ℎ𝑖 ∗𝑑𝑖〗)

Data creation and Assumptions
- 100 customers with a random number of order items are created
- The items have random dimension ranging between 10cm to 50cm in Width (wi), Depth (di), and Height (hi). 
- The bins allocated going to be the biggest bin that would fit all items, with the highest fill rate
-       Fill rate = ∑(𝑤𝑖 ∗ℎ𝑖 ∗𝑑𝑖)/(𝑊 ∗𝐷 ∗𝐻)
-   A buffer of 1-2% is added to all items for free movement while fitting into the bins

Flowchart
![image](https://github.com/user-attachments/assets/130b6167-ff5e-4957-9063-bae4c6a58076)









