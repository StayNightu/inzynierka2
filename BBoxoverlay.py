import cv2
import csv
from PIL import Image, ImageTk
class BBoxOverlay:
    def __init__(self, video_path, csv_path, main):
        self.video_path = video_path
        self.csv_path = csv_path
        self.bbox_data = self.load_bbox_data()
        self.cap = cv2.VideoCapture(video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.selected_bbox = None
        self.dragging = False
        self.paused = True
        self.current_frame_number = 0
        self.last_frame = None
        self.resizing_bbox = None
        self.original_bbox = None
        self.start_resize_point = None
        self.main = main

    def is_point_inside_bbox(self, x, y, bbox):
        x1, y1 = bbox['x1'], bbox['y1']
        x2, y2 = x1 + bbox['width'], y1 + bbox['height']
        return x1 <= x <= x2 and y1 <= y <= y2

    def load_bbox_data(self):
        bbox_data = {}
        with open(self.csv_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                frame_number = int(row[1])
                bbox_id = int(row[6].split(':')[1])
                detection_id = int(row[0])
                bbox_info = {
                    'x1': int(row[2]),
                    'y1': int(row[3]),
                    'width': int(row[4]),
                    'height': int(row[5]),
                    'id': bbox_id,
                    'detection_id': detection_id
                }
                if frame_number not in bbox_data:
                    bbox_data[frame_number] = []
                bbox_data[frame_number].append(bbox_info)
        return bbox_data

    def read_next_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.resize(frame, (1280, 720))
            self.last_frame = frame
            self.current_frame_number = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        return ret

    def get_frame(self):
        if self.last_frame is None:
            self.read_next_frame()
        frame = self.last_frame.copy()

        if self.current_frame_number in self.bbox_data:
            for bbox in self.bbox_data[self.current_frame_number]:
                self.draw_bbox(frame, bbox)
        return frame

    def select_bbox(self, x, y):
        for bbox in self.bbox_data.get(self.current_frame_number, []):
            if self.is_point_inside_bbox(x, y, bbox):
                self.selected_bbox = bbox
                return True
        return False

    def draw_bbox(self, frame, bbox):
        x1, y1 = bbox['x1'], bbox['y1']
        x2, y2 = x1 + bbox['width'], y1 + bbox['height']
        color = (0, 255, 0)
        if bbox == self.resizing_bbox:
            color = (0, 0, 255)
        elif bbox == self.selected_bbox:
            color = (255, 0, 0)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        bbox_id = bbox['id']
        text = f"ID: {bbox_id}"
        cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    def delete_selected_bbox(self):
        if self.selected_bbox:
            self.bbox_data[self.current_frame_number] = [bbox for bbox in self.bbox_data[self.current_frame_number] if
                                                         bbox != self.selected_bbox]
            self.selected_bbox = None
            self.save_bbox_data()

    def save_bbox_data(self):
        with open(self.csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['detection_id', 'frame_number', 'x_top_left', 'y_top_left', 'width', 'height', 'bb_id'])
            for frame_number, bboxes in self.bbox_data.items():
                for bbox in bboxes:
                    writer.writerow([
                        bbox['detection_id'], frame_number, bbox['x1'], bbox['y1'],
                        bbox['width'], bbox['height'], f"id:{bbox['id']}"
                    ])
    def save_new_bbox(self, new_bbox):
        if self.current_frame_number not in self.bbox_data:
            self.bbox_data[self.current_frame_number] = []
        self.bbox_data[self.current_frame_number].append(new_bbox)
        self.save_bbox_data()

    def start_resizing_bbox(self, x, y):
        for bbox in self.bbox_data.get(self.current_frame_number, []):
            if self.is_point_inside_bbox(x, y, bbox):
                self.resizing_bbox = bbox
                self.original_bbox = bbox.copy()
                self.start_resize_point = (x, y)
                self.resizing_edge = self.detect_resizing_edge(x, y, self.resizing_bbox)
                break
            frame = self.get_frame()
            self.main.update_canvas(frame)

    def detect_resizing_edge(self, x, y, bbox):
        edge_threshold = 10
        x1, y1, x2, y2 = bbox['x1'], bbox['y1'], bbox['x1'] + bbox['width'], bbox['y1'] + bbox['height']

        if abs(y - y1) < edge_threshold:
            if abs(x - x1) < edge_threshold:
                return "top-left"
            elif abs(x - x2) < edge_threshold:
                return "top-right"
            return "top"
        elif abs(y - y2) < edge_threshold:
            if abs(x - x1) < edge_threshold:
                return "bottom-left"
            elif abs(x - x2) < edge_threshold:
                return "bottom-right"
            return "bottom"
        elif abs(x - x1) < edge_threshold:
            return "left"
        elif abs(x - x2) < edge_threshold:
            return "right"

    def resize_bbox(self, x, y):
        if not self.resizing_bbox or not self.resizing_edge:
            return

        dx, dy = x - self.start_resize_point[0], y - self.start_resize_point[1]

        # Zaktualizuj bbox w zależności od przeciąganej krawędzi
        if self.resizing_edge == "top-left":
            self.resizing_bbox['x1'] = self.original_bbox['x1'] + dx
            self.resizing_bbox['y1'] = self.original_bbox['y1'] + dy
            self.resizing_bbox['width'] = self.original_bbox['width'] - dx
            self.resizing_bbox['height'] = self.original_bbox['height'] - dy
        elif self.resizing_edge == "top-right":
            self.resizing_bbox['y1'] = self.original_bbox['y1'] + dy
            self.resizing_bbox['width'] = self.original_bbox['width'] + dx
            self.resizing_bbox['height'] = self.original_bbox['height'] - dy
        elif self.resizing_edge == "bottom-left":
            self.resizing_bbox['x1'] = self.original_bbox['x1'] + dx
            self.resizing_bbox['width'] = self.original_bbox['width'] - dx
            self.resizing_bbox['height'] = self.original_bbox['height'] + dy
        elif self.resizing_edge == "bottom-right":
            self.resizing_bbox['width'] = self.original_bbox['width'] + dx
            self.resizing_bbox['height'] = self.original_bbox['height'] + dy
        elif self.resizing_edge == "left":
            self.resizing_bbox['x1'] = self.original_bbox['x1'] + dx
            self.resizing_bbox['width'] = self.original_bbox['width'] - dx
        elif self.resizing_edge == "right":
            self.resizing_bbox['width'] = self.original_bbox['width'] + dx
        elif self.resizing_edge == "top":
            self.resizing_bbox['y1'] = self.original_bbox['y1'] + dy
            self.resizing_bbox['height'] = self.original_bbox['height'] - dy
        elif self.resizing_edge == "bottom":
            self.resizing_bbox['height'] = self.original_bbox['height'] + dy
        self.resizing_bbox['width'] = max(self.resizing_bbox['width'], 1)
        self.resizing_bbox['height'] = max(self.resizing_bbox['height'], 1)

    def finish_resizing_bbox(self):
        self.resizing_bbox = None
        self.original_bbox = None
        self.start_resize_point = None
        frame = self.get_frame()
        self.main.update_canvas(frame)

    def convert_frame_to_tkinter_format(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(frame)
        return ImageTk.PhotoImage(image=im)

    def prev_frame(self):
        if self.cap.isOpened():
            current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            if current_frame > 1:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame - 2)
                self.read_next_frame()
                return self.get_frame()

    def next_frame(self):
        if self.cap.isOpened():
            self.read_next_frame()
            return self.get_frame()

    def update_bbox_data(self):
        self.bbox_data = self.load_bbox_data()

    def save_video_with_bbox(self, output_path):
        if not self.cap.isOpened():
            print("Nie można otworzyć pliku wideo")
            return

        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = self.cap.get(cv2.CAP_PROP_FPS)  # Pobierz FPS z oryginalnego wideo

        # Utwórz obiekt VideoWriter do zapisu wideo
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Zresetuj wideo do początkowej klatki
        self.current_frame_number = 0

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            if self.current_frame_number in self.bbox_data:
                for bbox in self.bbox_data[self.current_frame_number]:
                    self.draw_bbox(frame, bbox)

            out.write(frame)
            self.current_frame_number += 1

        self.cap.release()
        out.release()
        print("Wideo zostało zapisane.")