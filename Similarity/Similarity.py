import cv2
import imagehash
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import mean_squared_error as mse

class Similarity():
    def cal_similar(hash1, hash2):
        sim = 1 - (hash1 - hash2) / len(hash1.hash) ** 2
        return sim

    def similarity (image1, image2, method, threshold1, threshold2, threshold3):

        hash_size = 8
        mode = 'db4'
        image_scale = 64

        if method == "ssim":
            image1 = cv2.resize(image1, (5000, 5000))
            image2 = cv2.resize(image2, (5000, 5000))
            image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
            image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
            s = ssim(image1, image2, multichannel=True)
            if s > threshold1:
                return True
            return False

        elif method == "dhash":
            dhash1 = imagehash.dhash(image1, hash_size = hash_size)
            dhash2 = imagehash.dhash(image2, hash_size = hash_size)
            s = self.cal_similar(dhash1, dhash2)
            if s > threshold2:
                return True
            return False

        elif method == "whash":
            whash1 = imagehash.whash(image1, image_scale = image_scale, hash_size = hash_size, mode = mode)
            whash2 = imagehash.whash(image2, image_scale = image_scale, hash_size = hash_size, mode = mode)
            s = self.cal_similar(dhash1, dhash2)
            if s > threshold3:
                return True
            return False