import cv2
import numpy as np

NO_COLOR = -1
NOT_MARKED = -1
BACKGROUND_MARK = -2
MINIMUM_BORDER_WIDTH_RATIO = 0.15
IMPORTANT_COLOR_HIGH_THRESHOLD = 256 - 35
IMPORTANT_COLOR_LOW_THRESHOLD = 35
MINIMUM_REGION_AREA_RATIO = 0.0005
MAXIMUM_NEIGHBOR_PIXEL_COLOR_DIFFERENCE = 50
INF = 10 ** 30
MAXIMUM_NUMBER_OF_REGIONS = 1000
DX = [-1, +1, 0, 0]
DY = [0, 0, -1, +1]
SHARPEN_KERNEL = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
MAXIMUM_IMAGE_WIDTH = 1000
MAXIMUM_IMAGE_HEIGHT = 1000

class Node:
    def __init__(self, node_id, node_x, node_y):
        self.id = node_id
        self.x = node_x
        self.y = node_y
        self.adj = []
        self.color = -1

    def add_edge(self, node):
        self.adj.append(node.id)

    def set_color(self, cl):
        self.color = cl

class Map:
    def __init__(self, image):
        self.image = image
        self.height = len(image)
        self.width = len(image[0])
        if self.width > MAXIMUM_IMAGE_WIDTH or self.height > MAXIMUM_IMAGE_HEIGHT:
            print("Error: please specify an image with smaller dimensions.")
            exit(0)
        self.total_area = self.width * self.height
        self.mark = [[NOT_MARKED for i in range(self.width)] for j in range(self.height)]
        self.nodes = []
        self.regions = [[] for i in range(MAXIMUM_NUMBER_OF_REGIONS)]
        self.regions_border = [[] for i in range(MAXIMUM_NUMBER_OF_REGIONS)]
        self.nodes_color = [NO_COLOR for i in range(MAXIMUM_NUMBER_OF_REGIONS)]
    
    def is_inside(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return True

    def is_on_border(self, x, y):
        if self.mark[y][x] == BACKGROUND_MARK:
            return False
        for k in range(4):
            x2 = x + DX[k]
            y2 = y + DY[k]
            if self.is_inside(x2, y2) and self.mark[y2][x2] == BACKGROUND_MARK:
                return True
        return False
    
    def same_pixel_colors(image_object, x1, y1, x2, y2):
        if not image_object.is_inside(x1, y1) or not image_object.is_inside(x2, y2):
            return False
        b1, g1, r1 = image_object.image[y1][x1]
        b2, g2, r2 = image_object.image[y2][x2]
        r1, g1, b1 = int(r1), int(g1), int(b1)
        r2, g2, b2 = int(r2), int(g2), int(b2)
        diff = abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2)
        return diff <= 3 * MAXIMUM_NEIGHBOR_PIXEL_COLOR_DIFFERENCE
    
    def get_region_area(self, start_x, start_y, src_mark, dst_mark):
        if not self.is_inside(start_x, start_y) or self.mark[start_y][start_x] != src_mark:
            return 0
        color_area = 0
        queue = [(start_x, start_y)]
        self.mark[start_y][start_x] = dst_mark
        while queue:
            x, y = queue.pop(0)
            self.mark[y][x] = dst_mark
            color_area += 1
            for k in range(4):
                x2 = x + DX[k]
                y2 = y + DY[k]
                if self.is_inside(x2, y2) and self.mark[y2][x2] == src_mark and self.same_pixel_colors(x, y, x2, y2):
                    self.mark[y2][x2] = dst_mark
                    queue.append((x2, y2))
        return color_area
    
    def apply_threshold(self):
        for y in range(self.height):
            for x in range(self.width):
                b, g, r = self.image[y][x]
                r, g, b = int(r), int(g), int(b)
                if r + g + b < IMPORTANT_COLOR_LOW_THRESHOLD * 3:
                    self.image[y][x] = (255, 255, 255)
                    self.mark[y][x] = BACKGROUND_MARK
                if r + g + b > IMPORTANT_COLOR_HIGH_THRESHOLD * 3:
                    self.image[y][x] = (255, 255, 255)
                    self.mark[y][x] = BACKGROUND_MARK
                    
    def whiten_background(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.mark[y][x] == NOT_MARKED or self.mark[y][x] == BACKGROUND_MARK:
                    self.image[y][x] = (255, 255, 255)
    
    def are_adjacent(self, node1: Node, node2: Node):
        start_x, start_y = node1.x, node1.y
        end_x, end_y = node2.x, node2.y
        min_distance_sqr = INF
        for u in self.regions_border[self.mark[start_y][start_x]]:
            for v in self.regions_border[self.mark[end_y][end_x]]:
                tmp_distance_sqr = (u[0] - v[0]) * (u[0] - v[0]) + (u[1] - v[1]) * (u[1] - v[1])
                if tmp_distance_sqr < min_distance_sqr:
                    min_distance_sqr = tmp_distance_sqr
                    start_x, start_y = u[0], u[1]
                    end_x, end_y = v[0], v[1]
        dx, dy = end_x - start_x, end_y - start_y
        if abs(dx) + abs(dy) <= 1:
            return True
        dx, dy = float(dx), float(dy)
        border_width_threshold = MINIMUM_BORDER_WIDTH_RATIO * (self.width * self.width + self.height * self.height)
        if min_distance_sqr >= border_width_threshold:
            return False
        total_steps = int(2 * ((self.width * self.width + self.height * self.height) ** 0.5))
        for i in range(total_steps):
            x = int(start_x + i * dx / total_steps + 0.5)
            y = int(start_y + i * dy / total_steps + 0.5)
            if self.mark[y][x] >= 0 and (x != start_x or y != start_y) and (x != end_x or y != end_y):
                return False
        return True
    
    def change_region_color(self, node: Node, pixel_color):
        region_idx = self.mark[node.y][node.x]
        for i in range(len(self.regions[region_idx])):
            x = self.regions[region_idx][i][0]
            y = self.regions[region_idx][i][1]
            self.image[y][x] = pixel_color
            
    def get_all_regions_pixels(self):
        for y in range(self.height):
            for x in range(self.width):
                region_mark = self.mark[y][x]
                self.regions[region_mark].append((x, y))
                if self.is_on_border(x, y):
                    self.regions_border[region_mark].append((x, y))

    def find_graph_nodes(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.mark[y][x] == NOT_MARKED:
                    color_area = self.get_region_area(x, y, NOT_MARKED, len(self.nodes))
                    if color_area > MINIMUM_REGION_AREA_RATIO * self.total_area:
                        self.nodes.append(Node(len(self.nodes), x, y))
                    else:
                        self.get_region_area(x, y, len(self.nodes), NOT_MARKED)
        self.get_all_regions_pixels()

    def add_graph_edges(self):
        for i in range(len(self.nodes)):
            for j in range(len(self.nodes)):
                if j > i and self.are_adjacent(self.nodes[i], self.nodes[j]):
                    self.nodes[i].add_edge(self.nodes[j])
                    self.nodes[j].add_edge(self.nodes[i])

    def initial_preprocessing(self):
        print('Please wait for preprocessing...')

        self.apply_threshold()
        self.image = cv2.medianBlur(self.image, 3)
        self.apply_threshold()
        self.image = cv2.filter2D(self.image, -1, SHARPEN_KERNEL)
        self.apply_threshold()

        self.find_graph_nodes()
        self.add_graph_edges()

        self.whiten_background()

        print('Preprocessing finished.')
    