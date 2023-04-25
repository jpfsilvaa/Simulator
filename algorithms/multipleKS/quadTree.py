from geopy import distance

class Point:
    def __init__(self, x, y, entity):
        latNorm = 90
        longNorm = 180
        self.x = (x + latNorm)
        self.y = (y + longNorm)
        self.entity = entity

class QuadNode:
    def __init__(self, x, y, width, height, depth=0, capacity=4):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.depth = depth
        self.capacity = capacity
        self.points = []
        self.children = []

    def insert(self, point):
        if not self._contains_point(point):
            return False
        
        if len(self.points) < self.capacity:
            self.points.append(point)
            return True
        
        if not self.children:
            self._split()
            
        for child in self.children:
            if child.insert(point):
                return True
        
        return False

    def query(self, x, y, radius):
        result = []
        if self._intersects_circle(x, y, radius):
            for point in self.points:
                if self._distance(x, y, point.x, point.y) <= radius:
                    result.append(point)
            for child in self.children:
                result.extend(child.query(x, y, radius))
        return result

    def _contains_point(self, point):
        return self.x <= point.x < self.x + self.width and self.y <= point.y < self.y + self.height

    def _intersects_circle(self, x, y, radius):
        dx = abs(x - (self.x + self.width / 2))
        dy = abs(y - (self.y + self.height / 2))

        if dx > (self.width / 2 + radius):
            return False
        if dy > (self.height / 2 + radius):
            return False

        if dx <= (self.width / 2):
            return True
        if dy <= (self.height / 2):
            return True

        corner_distance_sq = (dx - self.width / 2) ** 2 + (dy - self.height / 2) ** 2

        return corner_distance_sq <= (radius ** 2)

    def _distance(self, x1, y1, x2, y2):
        distanceRes = distance.distance((x1, y1), (x2-90, y2-180)).meters
        return distanceRes
    
    def _split(self):
        half_width = self.width / 2
        half_height = self.height / 2
        depth = self.depth + 1
        self.children = [
            QuadNode(self.x, self.y, half_width, half_height, depth, self.capacity),
            QuadNode(self.x + half_width, self.y, half_width, half_height, depth, self.capacity),
            QuadNode(self.x, self.y + half_height, half_width, half_height, depth, self.capacity),
            QuadNode(self.x + half_width, self.y + half_height, half_width, half_height, depth, self.capacity)
        ]
        for point in self.points:
            for child in self.children:
                if child.insert(point):
                    break
        self.points = []



""" if __name__ == '__main__':
    import random
    import time
    import matplotlib.pyplot as plt

    random.seed(11)

    def generate_points(n):
        points = []
        for i in range(n):
            x = random.uniform(-24, -23)
            y = random.uniform(-47, -46)
            print(x, y)
            points.append(Point(x, y))
        return points

    def plot_points(points, x, y, radius):
        plt.figure(figsize=(10, 10))
        plt.xlim(0, 112000)
        plt.ylim(0, 112000)
        plt.scatter([point.x for point in points], [point.y for point in points], s=1)
        circle = plt.Circle((x, y), radius, color='r', fill=False)
        plt.gca().add_patch(circle)
        plt.show()

    points = generate_points(1000)
    x = random.uniform(0, 111000)
    y = random.uniform(0, 111000)
    radius = 10000

    # start = time.time()
    # result = []
    # for point in points:
    #     if ((point.x - x) ** 2 + (point.y - y) ** 2) ** 0.5 <= radius:
    #         result.append(point)
    # end = time.time()
    # print('Naive method: {} points found in {} seconds'.format(len(result), end - start))

    start = time.time()
    quad_tree = QuadNode(112000/2, 112000/2, 112000, 112000, capacity=4)
    for point in points:
        quad_tree.insert(point)
    result = quad_tree.query(x, y, radius)
    end = time.time()
    print('Quad tree method: {} points found in {} seconds'.format(len(result), end - start))

    plot_points(result, x, y, radius) """