#Will prepare the eye feature vectors for the tensor flow model
#No longer used but keeping for easy reference to the landmark key values
#Logic for feeding tensorflow_model.py now going to come from face_features.py

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
        #set up buffer to smooth and hold feature data
        self.feature_buffer = 0

    #Clear old feature data
    def reset(self) -> None:
        self.feature_buffer.clear()

    #Must return in the same order that my model will expect
    def get_feat_names(self):
        return list(self.features)

    #Build dict of all extracted face and eye feats
    def extract_feat_dict(self, landmarks) -> Dict[str,float]:
        return None

    #Combine the extracted feat values into one vector
    def extract_feat_vector(self, landmarks) -> float:
         return None

    #Build one labeled training sample
    def build_labeled_sample(self, landmarks):
        return None

    #Build a bunch of labeled training samples from the landmark data
    def build_labeled_samples(self, landmarks):
        return None

    #Calc measurement for one eye, will need to include iris pos and eye aspect ratio
    def eye_feats(self,landmarks):
        return None

    #Just get point x and y
    def point(self,landmarks, index:int):
        landmark = landmarks[index]
        return float(landmark.x), float(landmark.y)

    def avg(self, landmarks, numLandmarks: int) -> Tuple[float,float]:
        return float(np.mean([self.point(landmarks, i) for i in range(numLandmarks)]))


    #Just going to be the xs added and then /2, same for y
    def middle(self, point1: Tuple[float,float], point2: Tuple[float,float]) -> Tuple[float,float]:
        return (point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2


    #Just take the two points and subtract x and y to find distance between them
    def distance(self, point1: Tuple[float,float], point2: Tuple[float,float]) -> float:
        return float(np.hypot(point1[0] - point2[0], point1[1] - point2[1]))

