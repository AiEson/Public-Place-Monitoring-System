import clip
import cv2
import matplotlib.pyplot as plt
import numpy as np
import torch
import yaml
from PIL import Image


class Model:
    def __init__(self, settings_path: str = "./settings.yaml"):
        with open(settings_path, "r") as file:
            self.settings = yaml.safe_load(file)

        self.device = self.settings["model-settings"]["device"]
        self.model_name = self.settings["model-settings"]["model-name"]
        self.threshold = self.settings["model-settings"]["prediction-threshold"]
        self.model, self.preprocess = clip.load(self.model_name, device=self.device)
        self.labels = self.settings["label-settings"]["labels"]
        self.labels_ = []
        for label in self.labels:
            text = "a photo of " + label  # will increase model's accuracy
            self.labels_.append(text)

        self.text_features = self.vectorize_text(self.labels_)
        self.default_label = self.settings["label-settings"]["default-label"]

    @torch.no_grad()
    def transform_image(self, image: np.ndarray):
        pil_image = Image.fromarray(image).convert("RGB")
        tf_image = self.preprocess(pil_image).unsqueeze(0).to(self.device)
        return tf_image

    @torch.no_grad()
    def tokenize(self, text: list):
        text = clip.tokenize(text).to(self.device)
        return text

    @torch.no_grad()
    def vectorize_text(self, text: list):
        tokens = self.tokenize(text=text)
        text_features = self.model.encode_text(tokens)
        return text_features

    @torch.no_grad()
    def predict_(self, text_features: torch.Tensor, image_features: torch.Tensor):
        # Pick the top 5 most similar labels for the image
        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)
        similarity = image_features @ text_features.T
        values, indices = similarity[0].topk(1)
        return values, indices

    @torch.no_grad()
    def predict(self, image: np.array) -> dict:
        """
        Does prediction on an input image

        Args:
            image (np.array): numpy image with RGB channel ordering type.
                              Don't forget to convert image to RGB if you
                              read images via opencv, otherwise model's accuracy
                              will decrease.

        Returns:
            (dict): dict that contains predictions:
                    {
                    'label': 'some_label',
                    'confidence': 0.X
                    }
                    confidence is calculated based on cosine similarity,
                    thus you may see low conf. values for right predictions.
        """
        tf_image = self.transform_image(image)
        image_features = self.model.encode_image(tf_image)
        values, indices = self.predict_(
            text_features=self.text_features, image_features=image_features
        )
        label_index = indices[0].cpu().item()
        label_text = self.default_label
        model_confidance = abs(values[0].cpu().item())
        if model_confidance >= self.threshold:
            label_text = self.labels[label_index]

        prediction = {"label": label_text, "confidence": model_confidance}

        return prediction

    @staticmethod
    def plot_image(image: np.array, title_text: str):
        plt.figure(figsize=[13, 13])
        plt.title(title_text)
        plt.axis("off")
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        plt.imshow(image)


from typing import Union

import matplotlib.pyplot as plt
import numpy as np


def plot(
    image: np.array,
    title: str,
    title_size: int = 16,
    figsize: tuple = (13, 7),
    save_path: Union[str, None] = None,
):
    plt.figure(figsize=figsize)
    plt.title(title, size=title_size)
    plt.axis("off")
    plt.imshow(image)
    if save_path:
        plt.savefig(save_path)


def process_video(input_video_path: str, model: Model):
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)
    size = (width, height)
    fps = int(cap.get(cv2.CAP_PROP_FPS) + 0.5)
    print("FPS", fps)
    success, frame = cap.read()

    # out = cv2.VideoWriter(save_video_path, fourcc, fps, size)
    success = True

    while success and cap.isOpened():

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        prediction = model.predict(frame)
        label = prediction["label"]
        conf = prediction["confidence"]
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = cv2.putText(
            frame, label.title(), (0, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2
        )
        cv2.imshow("Recording...", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        success, frame = cap.read()

    cap.release()
    cv2.destroyAllWindows()


model = model = Model()


def get_fight_img(img):
    frame = img.copy()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    prediction = model.predict(frame)
    label = prediction["label"]
    # conf = prediction['confidence']
    # frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    # frame = cv2.putText(frame, label.title(),
    #                     (0, 100),
    #                     cv2.FONT_HERSHEY_SIMPLEX, 1,
    #                     (0, 0, 255), 2)

    return label.title()


if __name__ == "__main__":
    video_path = "./data/office_fight.mp4"
    process_video(video_path, model=Model())
