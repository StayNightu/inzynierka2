'''
class BBox:
    def __init__(self, canvas):
        self.canvas = canvas
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.selected_corner = None
        self.bindings = []
        self.edit_mode = False

        self.setup_bindings()

    def setup_bindings(self):
        # Bindowanie zdarzeń do odpowiednich metod
        self.bindings.append(self.canvas.bind("<ButtonPress-1>", self.on_press))
        self.bindings.append(self.canvas.bind("<B1-Motion>", self.on_drag))
        self.bindings.append(self.canvas.bind("<ButtonRelease-1>", self.on_release))

    def on_press(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

        # Sprawdź, czy kliknięcie nastąpiło w jednym z narożników bounding boxa
        if self.rect:
            for corner in self.get_corners():
                if self.is_point_near(cur_x, cur_y, corner[1][0], corner[1][1]):
                    self.selected_corner = corner[0]
                    break
            # Jeśli żaden narożnik nie został wybrany, sprawdź, czy kliknięcie nastąpiło wewnątrz bounding boxa
            if not self.selected_corner and self.is_point_inside(cur_x, cur_y):
                self.selected_corner = "center"
        else:
            # Jeśli nie ma bounding boxa, ustaw początkowe współrzędne dla nowego
            self.start_x = cur_x
            self.start_y = cur_y

    def on_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)

        if self.edit_mode and self.rect:
            # Jeśli wybrano narożnik bounding boxa
            if self.selected_corner:
                if self.selected_corner != "center":
                    self.edit_bbox_corner(cur_x, cur_y)
                else:
                    self.move_bbox(cur_x - self.start_x, cur_y - self.start_y)
                    self.start_x, self.start_y = cur_x, cur_y
        elif not self.edit_mode:
            if not self.rect:
                self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, cur_x, cur_y, outline="red")
            else:
                self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_release(self, event):
        # Zresetuj zaznaczenie narożnika
        self.selected_corner = None

    def clear(self):
        # Usuń bounding box
        if self.rect:
            self.canvas.delete(self.rect)
            self.rect = None

    def unbind(self):
        for binding in self.bindings:
            self.canvas.unbind("<ButtonPress-1>", binding)
            self.canvas.unbind("<B1-Motion>", binding)
            self.canvas.unbind("<ButtonRelease-1>", binding)

    def get_corners(self):
        # Zwraca współrzędne narożników bounding boxa
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        return [
            ("top-left", (x1, y1)),
            ("top-right", (x2, y1)),
            ("bottom-left", (x1, y2)),
            ("bottom-right", (x2, y2)),
        ]

    def is_point_near(self, x1, y1, x2, y2, distance=5):
        # Sprawdza, czy dwa punkty są blisko siebie
        return abs(x1 - x2) <= distance and abs(y1 - y2) <= distance

    def is_point_inside(self, x, y):
        # Sprawdza, czy punkt jest wewnątrz bounding boxa
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        return x1 <= x <= x2 and y1 <= y <= y2

    def edit_bbox_corner(self, x, y):
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        if self.selected_corner == "top-left":
            self.canvas.coords(self.rect, x, y, x2, y2)
        elif self.selected_corner == "top-right":
            self.canvas.coords(self.rect, x1, y, x, y2)
        elif self.selected_corner == "bottom-left":
            self.canvas.coords(self.rect, x, y1, x2, y)
        elif self.selected_corner == "bottom-right":
            self.canvas.coords(self.rect, x1, y1, x, y)

    def move_bbox(self, dx, dy):
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        self.canvas.coords(self.rect, x1 + dx, y1 + dy, x2 + dx, y2 + dy)
'''