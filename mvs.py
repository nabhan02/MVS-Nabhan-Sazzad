#Author: Nabhan Sazzad
#Copyright 2021, Nabhan Sazzad, All Rights Reserved
# -*- coding: utf-8 -*-


# Install packages that we will use in the project
!pip install opencv-contrib-python==4.5.4.60
!pip install pypotree
!pip install open3D

# Import packages
import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv
import pypotree
import open3d as o3d

# Helper functions
def to_homog(points):
    """
    Function: convert points from Euclidean coordinates to homogeneous coordinates
    points: 3xn numpy array containing Euclidean coordinates
    Return: 4xn numpy array containing homogeneous coordinates
    """
    m, n = points.shape
    points_homog = np.concatenate([points, np.ones([1, n])], axis=0)
    return points_homog

def from_homog(points_homog):
    """
    Function: convert points from homogeneous coordinates to Eulidean coordinates
    points_homog: 4xn numpy array containing homogeneous coordinates
    Return: 3xn numpy array containing Euclidean coordinates
    """
    m, n = points_homog.shape
    points = points_homog[:m-1] / points_homog[m-1]
    return points

def hstack_images(img1, img2):
    """
    Function: stacks 2 images side-by-side
    img1, img2: two input images
    Return: stacked image
    """
    H = max(img1.shape[0], img2.shape[0])
    W = img1.shape[1] + img2.shape[1]
    img = np.zeros((H, W, 3), dtype=img1.dtype)
    img[:img1.shape[0], :img1.shape[1], :] = img1
    img[:img2.shape[0], img1.shape[1]:, :] = img2
    return img

def vis_correspondence(img1, img2, S1, S2):
    """
    Function: visualizes corresponding points between two images
    img1, img2: two input images
    S1: 2xn numpy array containing points in image 1
    S2: 2xn numpy array containing points in image 2 that corresponds to points in image 1
    """
    img = hstack_images(img1, img2)
    x_shift = img1.shape[1]
    S1 = S1.astype(np.int)  # Shape: [2, n].
    S2 = S2.astype(np.int)  # Shape: [2, n].
    np.random.seed(0)
    colors = np.random.rand(S1.shape[1], 3)
    if img.dtype == np.uint8:
      colors *= 255

    # Draw figure. 
    for p1, p2, color in zip(S1.T, S2.T, colors):
      x1, y1 = p1
      x2, y2 = p2
      img = cv.circle(img, (x1, y1), 5, color, -1)
      img = cv.circle(img, (x2 + x_shift, y2), 5, color, -1)
      img = cv.line(img, (x1, y1), (x2 + x_shift, y2), color, 2, cv.LINE_AA)
    plt.figure(figsize=(16, 12))
    plt.title('Visualize correspondences')
    plt.imshow(img)
    plt.show()

from google.colab import drive
drive.mount('/content/drive')

# Copy data set folder into working directory
!cp -r '/content/drive/MyDrive/Colab Notebooks/final_project_data' .

# Load images into a list
images = []
for i in range(49):
    image = cv.imread(f'./final_project_data/images/{i}.jpg') # Use cv.imread instead of plt.imread so that we can directly use cv functions afterwards
    image = cv.cvtColor(image, cv.COLOR_BGR2RGB) # cv.imread save data in BGR order by default, change it into RGB
    images.append(image)

# Preview of images
fig = plt.figure(figsize=(25, 25))
row = 7
col = 7
for i in range(row * col):
    ax = fig.add_subplot(row, col, i+1)
    ax.title.set_text(f'Image {i}')
    plt.imshow(images[i])
plt.show()

# Load intrinsic and extrinsic matrices
intrinsics = np.load('./final_project_data/intrinsics.npy')
extrinsics = np.load('./final_project_data/extrinsics.npy')

"""## 2 Identify Points of Interests

"""

# Use SIFT to detect key points in images and compute descriptors for those key points
# You may need the help of cv.SIFT_create(), detectAndCompute(), and cv.drawKeypoints()

keypoints = []
descriptors = []
outputs = []    

for i, image in enumerate(images):
    gray_image = cv.cvtColor(image,cv.COLOR_RGB2GRAY) # Convert image to grayscale
    # Fill in codes to detect corners
    sift = cv.SIFT_create()# Fill in codes to detect corners
    kp, des = sift.detectAndCompute(gray_image, None)
    keypoints.append(kp)
    descriptors.append(des)
    outputs.append(cv.drawKeypoints(gray_image, keypoints[i], descriptors[i]))
    
# Preview of images. You can use cv.drawKeypoints to generate the images with corners and visualize by plt.imshow()
fig = plt.figure(figsize=(25, 25))
row = 7
col = 7
for i in range(row * col):
    ax = fig.add_subplot(row, col, i+1)
    ax.title.set_text(f'Image {i}')
    plt.imshow(outputs[i])
plt.show()

"""## 3 3D Reconstruction with Two Cameras

### 3.1 Search for Corresponding Points across two images

My strategy for producing the method below heavily relied on this openCV dcumentation https://docs.opencv.org/3.4/da/de9/tutorial_py_epipolar_geometry.html.
"""

# you may need functions cv.BFMatcher and knnMatch to compare against features. 
# You may need to understand the output data structure of detectAndCompute() function
# for the SIFT feature extractor. If you are able to understand the description, 
# you should be able to know what kp1, kp2, des1, des2 should be.
def get_corresondence(img1, img2, kp1, kp2, des1, des2):
    """
    Function: get correspondence across two images
    img1, img2: two input images
    kp1, kp2: keypoints of img1 and img2
    des1, des2: descriptors of img1 and img2
    Return: two 2xn numpy array that contains corresponding points after validation
    """
    # Fill in the code here
    bf = cv.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)
    
    good = []

    for m,n in matches:
      if m.distance < 0.55*n.distance:
        good.append([m])
    
    pts1 = np.zeros((2,len(good)))
    pts2 = np.zeros((2,len(good)))

    for i,g in enumerate(good):
      pts1[:,i] = kp1[g[0].queryIdx].pt
      pts2[:,i] = kp2[g[0].trainIdx].pt

    return pts1, pts2

# Get corresondence of image 0 and image 1
pts1, pts2 = get_corresondence(images[0], images[1], keypoints[0], keypoints[1], descriptors[0], descriptors[1])

# Visualize correspondence
vis_correspondence(images[0], images[1], pts1, pts2)
print("Number of correspondences derived: %d" % (len(pts1[0])))

"""### 3.2 Triangulation"""

def reconstruct(pts1, pts2, int1, int2, ext1, ext2):
    """
    Function: reconstruct 3D points with given correspondence
    int1, int2: intrinsic matrices of camera 1 and camera 2
    ext1, ext2: extrinsic matrices of camera 1 and camera 2
    Return: 3xn numpy arrays containing the Euclidean coordinates of reconstructed 3D points
    """
    # Fill in the code here
    i = np.array([[1,0,0,0],
                  [0,1,0,0],
                  [0,0,1,0]])
    tri = cv.triangulatePoints(int1@i@ext1, int2@i@ext2, pts1, pts2)

    recon = from_homog(tri)

    return recon

# Reconstruct 3D points
recon = reconstruct(pts1, pts2, intrinsics[0], intrinsics[1], extrinsics[0], extrinsics[1])

"""Let's see the visualization of our results using pypotree:"""

# Visualizing reconstruction results
cloudpath = pypotree.generate_cloud_for_display(-recon.T) # pypotree takes in nx3 numpy array, add negative to reverse axis
pypotree.display_cloud_colab(cloudpath)

"""## 4 3D Reconstruction with Multiple Cameras

### 4.1 Validate Correspondence
"""

def validate_correspondence(pts1, pts2, int1, int2, ext1, ext2, imgS):
    """
    Function: validate corespondence via fundamental matrix
    pts1, pts2: two 2xn numpy arrays containing the original correspondence
    int1, int2: intrinsic matrices of camera 1 and camera 2
    ext1, ext2: extrinsic matrices of camera 1 and camera 2
    Return: two 2xn numpy array that contains corresponding points after validation
    """
    
    return pts1, pts2

# Validate correspondence via camera matrices
pts1_inliers, pts2_inliers = validate_correspondence(pts1, pts2, intrinsics[0], intrinsics[1], extrinsics[0], extrinsics[1], 0)

# Visualize correspondence after validation
print("Correspondence after validation:")
vis_correspondence(images[0], images[1], pts1_inliers, pts2_inliers)
print("Number of correspondences after validation: %d" % (len(pts1_inliers[0])))

# Reconstruct 3D points with cleaner visualization
recon = reconstruct(pts1_inliers, pts2_inliers, intrinsics[0], intrinsics[1], extrinsics[0], extrinsics[1])

# Visualizing reconstruction results
cloudpath2 = pypotree.generate_cloud_for_display(-recon.T)
pypotree.display_cloud_colab(cloudpath2)

"""### 4.2 Adding More Cameras"""

# Include the whole data set
for i in range (1, 48):
    print("Resconstructing from image %d and %d..." % (i, i+1))
    pts1, pts2 = get_corresondence(images[i], images[i+1], keypoints[i], keypoints[i+1], descriptors[i], descriptors[i+1])
    pts1_inliers, pts2_inliers = validate_correspondence(pts1, pts2, intrinsics[i], intrinsics[i+1], extrinsics[i], extrinsics[i+1], i)
    recon_next = reconstruct(pts1_inliers, pts2_inliers, intrinsics[i], intrinsics[i+1], extrinsics[i], extrinsics[i+1])
    recon = np.hstack([recon, recon_next])

# Visualizing reconstruction results
cloudpath3 = pypotree.generate_cloud_for_display(-recon.T)
pypotree.display_cloud_colab(cloudpath3)

"""## 5 Further Opimization"""

pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(-recon.T)
voxel_down_pcd = pcd.voxel_down_sample(voxel_size=0.01)
inlier_cloud = voxel_down_pcd.remove_statistical_outlier(10, 1.5)

pts = np.asarray(inlier_cloud[0].points)
inlier_cloud = pypotree.generate_cloud_for_display(pts)
pypotree.display_cloud_colab(inlier_cloud)
