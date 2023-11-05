import cv2
import torch
from super_gradients.training import models
import numpy as np
import math
import random

from deep_sort_pytorch.utils.draw import draw_boxes, palette
from deep_sort_pytorch.utils.parser import get_config
from deep_sort_pytorch.deep_sort import DeepSort

MODEL_NAME = 'yolo_nas_s'

class sledzenie:
    def __init__(self):
        self.video_path = 'test3.mp4'
        self.cap, self.frame_width, self.frame_height = self.get_video_info(self.video_path)
        self.model = self.load_model(MODEL_NAME)
        self.classNames = self.cococlassNames()
        self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(self.classNames))]
        self.palette = (2 ** 11 - 1, 2 ** 15 - 1, 2 ** 20 - 1)
        self.deepsort = self.initialize_deepsort()
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=20, detectShadows=False)

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
        # Create the Deep SORT configuration object and load settings from the YAML file
        cfg_deep = get_config()
        cfg_deep.merge_from_file("./deep_sort_pytorch/configs/deep_sort.yaml")

        # Initialize the DeepSort tracker
        deepsort = DeepSort(cfg_deep.DEEPSORT.REID_CKPT,
                            max_dist=cfg_deep.DEEPSORT.MAX_DIST,
                            # min_confidence  parameter sets the minimum tracking confidence required for an object detection to be considered in the tracking process
                            min_confidence=cfg_deep.DEEPSORT.MIN_CONFIDENCE,
                            # nms_max_overlap specifies the maximum allowed overlap between bounding boxes during non-maximum suppression (NMS)
                            nms_max_overlap=cfg_deep.DEEPSORT.NMS_MAX_OVERLAP,
                            # max_iou_distance parameter defines the maximum intersection-over-union (IoU) distance between object detections
                            max_iou_distance=cfg_deep.DEEPSORT.MAX_IOU_DISTANCE,
                            # Max_age: If an object's tracking ID is lost (i.e., the object is no longer detected), this parameter determines how many frames the tracker should wait before assigning a new id
                            max_age=cfg_deep.DEEPSORT.MAX_AGE, n_init=cfg_deep.DEEPSORT.N_INIT,
                            # nn_budget: It sets the budget for the nearest-neighbor search.
                            nn_budget=cfg_deep.DEEPSORT.NN_BUDGET,
                            use_cuda=True
                            )

        return deepsort

    def cococlassNames(self):
        class_names = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
                       "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", "dog",
                       "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
                       "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite",
                       "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle",
                       "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
                       "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
                       "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
                       "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
                       "teddy bear", "hair drier", "toothbrush"]
        return class_names

    def compute_color_for_labels(self, label):
        """
        Function that adds fixed color depending on the class
        """
        if label == 0:  # person  #BGR
            color = (85, 45, 255)
        elif label == 2:  # Car
            color = (222, 82, 175)
        elif label == 3:  # Motobike
            color = (0, 204, 255)
        elif label == 5:  # Bus
            color = (0, 149, 255)
        else:
            color = [int((p * (label ** 2 - label + 1)) % 255) for p in palette]
        return tuple(color)

    def draw_boxes(self, img, bbox, identities=None, categories=None, names=None, offset=(0, 0)):
        for i, box in enumerate(bbox):
            x1, y1, x2, y2 = [int(i) for i in box]
            x1 += offset[0]
            x2 += offset[0]
            y1 += offset[0]
            y2 += offset[0]
            cat = int(categories[i]) if categories is not None else 0
            id = int(identities[i]) if identities is not None else 0
            # Create Bounding Boxes around the Detected Objects
            cv2.rectangle(img, (x1, y1), (x2, y2), color=self.compute_color_for_labels(), thickness=2,
                          lineType=cv2.LINE_AA)
            label = str(id) + ":" + self.classNames[cat]
            (w, h), _ = cv2.getTextSize(str(label), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1 / 2, thickness=1)
            # Create a rectangle above the detected object and add label and confidence score
            t_size = cv2.getTextSize(str(label), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1 / 2, thickness=1)[0]
            c2 = x1 + t_size[0], y1 - t_size[1] - 3
            cv2.rectangle(self.frame, (x1, y1), c2, color=self.compute_color_for_labels(), thickness=-1, lineType=cv2.LINE_AA)
            cv2.putText(self.frame, str(label), (x1, y1 - 2), 0, 1 / 2, [255, 255, 255], thickness=1, lineType=cv2.LINE_AA)
        return img

    def process_video(self):
        self.out = cv2.VideoWriter('Output.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10,
                                   (self.frame_width, self.frame_height))

        while True:
            xywh_bboxs = []
            confs = []
            oids = []
            outputs = []
            ret, frame = self.cap.read()
            if ret:
                # Apply background subtraction
                fg_mask = self.background_subtractor.apply(frame)

                # Threshold the foreground mask to get a binary mask
                fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)[1]

                # Find contours in the binary mask
                contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Process only if there are contours (moving objects)
                if len(contours) > 0:
                    result = list(self.model.predict(frame, conf=0.5))[0]
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

                        # Check if the centroid of the bounding box is within a moving object region
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
                        draw_boxes(frame, bbox_xyxy, identities, object_id)
                self.out.write(frame)
            else:
                break

        self.out.release()
        self.cap.release()

    def display_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Error: Could not open the video file.")

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow('Video', frame)
            # Wait for 25ms per frame or until user presses 'q'
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def run(self):
        self.process_video()
        self.display_video('output.avi')

if __name__ == "__main__":
    main = Main()
    main.run()