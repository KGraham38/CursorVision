#Will prepare the eye feature vectors for the tensor flow model

class Preprocess:

    features = [
        "left_iris_x_ratio", "right_iris_x_ratio", "avg_iris_x_ratio",
        "left_iris_y_ratio", "right_iris_y_ratio", "avg_iris_y_ratio",
        "left_eye_aspect", "right_eye_aspect", "avg_eye_aspect",
        "head_horiz_offset_ratio","head_vert_offset_ratio", "face_aspect_ratio"]

    left_eye = {
        "iris": [468, 469, 470, 471, 472],
        "outer": 33, "inner": 133,
        "upper": 159, "lower": 145,
        "brow": [70, 63, 105, 66, 107],}

    right_eye = {
        "iris": [473, 474, 475, 476, 477],
        "outer": 263, "inner": 362,
        "upper": 386, "lower": 374,
        "brow": [336, 296, 334, 293, 300]}

    #To hopefully help correct for head position, may need a few additional points, we shall see
    tip_nose = 1
    face_left = 234
    face_right = 454
    forehead = 10
    chin = 152

    def __init__(self):
        self.feature_buffer = 0

    def reset(self) -> None:
        self.feature_buffer.clear()

    def get_feat_names(self):
        return list(self.features)

    def extract_feat_dict(self, landmarks) -> Dict[str,float]:
        return None

    def extract_feat_vector(self, landmarks) -> float:

    def build_labeled_sample(self, landmarks):
        return None
    def build_labeled_samples(self, landmarks):
        return None

    def eye_feats(self,landmarks):
        return None

    #Just get point x and y
    def point(self,landmarks, index:int):
        landmark = landmarks[index]
        return float(landmark.x), float(landmark.y)

    def avg(self, landmarks):

    #Just going to be the xs added and then /2, same for y
    def middle(self, point1: Tuple[float,float], point2: Tuple[float,float]) -> Tuple[float,float]:
        return (point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2


    #Just take the two points and subtract x and y to find distance between them
    def distance(self, point1: Tuple[float,float], point2: Tuple[float,float]) -> float:
        return float(np.hypot(point1[0] - point2[0], point1[1] - point2[1]))

