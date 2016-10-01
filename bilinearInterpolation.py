import cv2

# Path to an image on my computer. Use your own image / frame.
impath = 'C:\Users\Gus\Pictures\Christmas 2014\Line.jpg'
img = cv2.imread('C:\Users\Gus\Pictures\Christmas 2014\Line.jpg')

# Show the picture until any key is pressed. REMOVE
cv2.imshow("original", img)
cv2.waitKey(0)

# This is the resizing ratio. Increasing length and height by r=2.
r = 4
# The dimensions of the new image.
dim = (int(img.shape[1] * r), int(img.shape[0] * r))
 
# perform the actual resizing of the image using bilinear interpolation
resized = cv2.resize(img, dim, interpolation = cv2.INTER_LINEAR)

# Show that image until a key is pressed. REMOVE
cv2.imshow("resized", resized)
cv2.waitKey(0)

cv2.imwrite('interp.png',resized)