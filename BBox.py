class BoundingBox:
    def __init__(self, main_instance, canvas=None):
        self.main = main_instance
        self.canvas = canvas
        self.bounding_boxes = {}
        self.reusable_ids = []
        self.next_box_id = 1
        self.selected_bbox_id = None
        self.current_rect = None

        self.is_drawing = False
        self.is_editing = False
        self.edit_mode = None

        # Event bindings
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)

    # Event Handlers
    def on_mouse_down(self, event):
        if self.is_drawing:
            self.start_drawing(event)
        else:
            self.select_bbox(event)

    def on_mouse_move(self, event):
        if self.is_drawing and self.current_rect:
            self.update_drawing(event)

    def on_mouse_release(self, event):
        if self.is_drawing and self.current_rect:
            self.finalize_drawing(event)

    # Drawing Methods
    def start_drawing(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.current_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', tags="bbox")

    def update_drawing(self, event):
        curX, curY = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.canvas.coords(self.current_rect, self.start_x, self.start_y, curX, curY)

    def finalize_drawing(self, event):
        end_x, end_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        new_id = self.reusable_ids.pop(0) if self.reusable_ids else self.next_box_id
        bbox_label = self.canvas.create_text(
            self.start_x + 5, self.start_y + 5,
            text=str(new_id), fill="yellow", tags=("bbox", "bbox_label_" + str(new_id))
        )
        self.bounding_boxes[new_id] = {
            'coords': (int(self.start_x), int(self.start_y), int(end_x), int(end_y)),
            'rect': self.current_rect,
            'label': bbox_label
        }
        self.current_rect = None
        self.is_drawing = False
        self.main.draw_button.config(text="Rysuj Bounding Box")
        if not self.reusable_ids:
            self.next_box_id += 1

    # BBox Selection and Deletion
    def select_bbox(self, event):
        clicked_id = self.get_bbox_at_position(event.x, event.y)
        if clicked_id:
            self.selected_bbox_id = int(clicked_id.split('_')[-1])

    def delete_selected_bbox(self):
        if self.selected_bbox_id in self.bounding_boxes:
            bbox = self.bounding_boxes[self.selected_bbox_id]
            self.canvas.delete(bbox['rect'])
            self.canvas.delete(bbox['label'])
            del self.bounding_boxes[self.selected_bbox_id]
            self.reusable_ids.append(self.selected_bbox_id)
            self.reusable_ids.sort()
            self.selected_bbox_id = None

    # Helper Methods
    def get_bbox_at_position(self, x, y):
        selected_items = self.canvas.find_overlapping(x, y, x, y)
        for item in selected_items:
            for tag in self.canvas.gettags(item):
                if tag.startswith("bbox_"):
                    return tag
        return None

    def toggle_drawing_mode(self):
        self.is_drawing = not self.is_drawing
        button_text = "Zakończ rysowanie" if self.is_drawing else "Rysuj Bounding Box"
        self.main.draw_button.config(text=button_text)