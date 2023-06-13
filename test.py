import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Circle

def uiGen(points, minX, minY, maxX, maxY, radius):
    fig, ax = plt.subplots()
    img_path = 'antena.jpg'
    for x, y in points:
        img = mpimg.imread(img_path)
        img_size = radius/3
        ax.imshow(img, extent=(x - img_size, x + img_size, y - img_size, y + img_size))
        circle = Circle((x, y), radius, edgecolor='b', facecolor='none')
        ax.add_patch(circle)

    plt.xlim(minX, maxX)
    plt.ylim(minY, maxY)
    plt.gca().axes.get_yaxis().set_visible(False)
    plt.gca().axes.get_xaxis().set_visible(False)
    plt.show()

def pointsGen(minX, minY, maxX, maxY, radius):
    points = []
    nextPointX = minX
    nextPointY = minY
    advance = True
    step = 2*radius - 0.6*radius # intersection of 300m for radius of 500m
    while nextPointY < maxY:
        while nextPointX < maxX:
            points.append((nextPointX, nextPointY))
            nextPointX += step
        nextPointY += step
        if advance:
            nextPointX = step/2
            advance = False
        else:
            nextPointX = minX
            advance = True
    return points

from geopy import distance

def add_meters_to_latitude(latitude, longitude, distance_meters):
    original_point = (latitude, longitude)
    meters_per_deg_lat = distance.distance(original_point, (latitude + 1, longitude)).meters

    new_latitude = latitude + (distance_meters / meters_per_deg_lat)

    return new_latitude

points = pointsGen(0, 0, 5000, 5000, 500)
print(points)
uiGen(points, 0, 0, 5000, 5000, 500)