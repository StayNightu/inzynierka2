from tkinter import filedialog
import cv2
import torch
import numpy as np
import math
from super_gradients.training import models
from deep_sort_pytorch.utils.draw import palette
from deep_sort_pytorch.utils.parser import get_config
from deep_sort_pytorch.deep_sort import DeepSort

MODEL_NAME = 'yolo_nas_s'

class Sledzenie:
    def __init__(self):
        self.video_path = None
        self.cap, self.frame_width, self.frame_height = None, None, None
        self.model = self.load_model(MODEL_NAME)
        self.deepsort = self.initialize_deepsort()

    def load_video(self):
        self.video_source = filedialog.askopenfilename(filetypes=[("Pliki MP4", "*.mp4"), ("Pliki AVI", "*.avi")])
        if not self.video_source:
            raise ValueError("Nie wybrano pliku.")
        return self.video_source

    def set_video(self, video_path):
        if not video_path:
            raise ValueError("Niepoprawne wideo.")
        self.video_path = video_path
        self.cap, self.frame_width, self.frame_height = self.get_video_info(self.video_path)

    def get_video_info(self, video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Error: Could not open the video file.")
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return cap, frame_width, frame_height

    def load_model(self, model_name):
        device = torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
        model = models.get(model_name, pretrained_weights="coco").to(device)
        return model

    def initialize_deepsort(self):
        cfg_deep = get_config()
        cfg_deep.merge_from_file("./deep_sort_pytorch/configs/deep_sort.yaml")

        return DeepSort(cfg_deep.DEEPSORT.REID_CKPT,
                        max_dist=cfg_deep.DEEPSORT.MAX_DIST,
                        min_confidence=cfg_deep.DEEPSORT.MIN_CONFIDENCE,
                        nms_max_overlap=cfg_deep.DEEPSORT.NMS_MAX_OVERLAP,
                        max_iou_distance=cfg_deep.DEEPSORT.MAX_IOU_DISTANCE,
                        max_age=cfg_deep.DEEPSORT.MAX_AGE,
                        n_init=cfg_deep.DEEPSORT.N_INIT,
                        nn_budget=cfg_deep.DEEPSORT.NN_BUDGET,
                        use_cuda=True
                        )
    def compute_color_for_labels(self, label):
        color = [int((p * (label ** 2 - label + 1)) % 255) for p in palette]
        return color

    def draw_boxes(self, img, bbox, identities=None, offset=(0, 0)):
        for i, box in enumerate(bbox):
            x1, y1, x2, y2 = [int(i) for i in box]
            x1 += offset[0]
            x2 += offset[0]
            y1 += offset[0]
            y2 += offset[0]
            id = int(identities[i]) if identities is not None else 0
            cv2.rectangle(img, (x1, y1), (x2, y2), color=self.compute_color_for_labels(id), thickness=2, lineType=cv2.LINE_AA)
            label = str(id)
            t_size = cv2.getTextSize(str(label), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1 / 2, thickness=1)[0]
            c2 = x1 + t_size[0], y1 - t_size[1] - 3
            cv2.rectangle(img, (x1, y1), c2, color=self.compute_color_for_labels(id), thickness=-1, lineType=cv2.LINE_AA)
            cv2.putText(img, str(label), (x1, y1 - 2), 0, 1 / 2, [255, 255, 255], thickness=1, lineType=cv2.LINE_AA)
        return img

    def process_video(self):
        self.out = cv2.VideoWriter('Output.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10,
                                   (self.frame_width, self.frame_height))

        prev_frame = None
        while True:
            xywh_bboxs = []
            confs = []
            oids = []
            ret, frame = self.cap.read()

            if ret:
                if prev_frame is not None:
                    fg_mask = cv2.absdiff(prev_frame, frame)
                    fg_mask = cv2.cvtColor(fg_mask, cv2.COLOR_BGR2GRAY)
                    _, fg_mask = cv2.threshold(fg_mask, 5, 300, cv2.THRESH_BINARY)
                    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    if len(contours) > 0:
                        result = list(self.model.predict(frame, conf=0.6))[0]
                        bbox_xyxys = result.prediction.bboxes_xyxy.tolist()
                        confidences = result.prediction.confidence
                        labels = result.prediction.labels.tolist()
                        for (bbox_xyxy, confidence, cls) in zip(bbox_xyxys, confidences, labels):
                            bbox = np.array(bbox_xyxy)
                            x1, y1, x2, y2 = bbox[0], bbox[1], bbox[2], bbox[3]
                            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                            conf = math.ceil((confidence * 100)) / 100
                            cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
                            bbox_width = abs(x1 - x2)
                            bbox_height = abs(y1 - y2)
                            xcycwh = [cx, cy, bbox_width, bbox_height]
                            if fg_mask[cy, cx] == 255:
                                xywh_bboxs.append(xcycwh)
                                confs.append(conf)
                                oids.append(int(cls))
                        xywhs = torch.tensor(xywh_bboxs)
                        confss = torch.tensor(confs)
                        outputs = self.deepsort.update(xywhs, confss, oids, frame)
                        if len(outputs) > 0:
                            bbox_xyxy = outputs[:, :4]
                            identities = outputs[:, -2]
                            object_id = outputs[:, -1]
                            self.draw_boxes(frame, bbox_xyxy, identities, object_id)
                prev_frame = frame.copy()
                self.out.write(frame)
            else:
                break
        self.out.release()
        self.cap.release()
    def run(self):
        self.set_video(self.video_source)
        self.process_video()