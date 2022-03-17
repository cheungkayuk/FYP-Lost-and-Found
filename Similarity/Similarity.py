import cv2
import imagehash
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import mean_squared_error as mse

class Similarity:
    def cal_similar(self, hash1, hash2):
        sim = 1 - (hash1 - hash2) / len(hash1.hash) ** 2
        return sim

    def similarity (self, image1, image2, method = "dhash", threshold=None):
        threshold1 = 0.85
        threshold2 = 0.8
        threshold3 = 0.8
        if threshold:
            if threshold>=0 and threshold<=1:
                threshold1 = threshold
                threshold2 = threshold
                threshold3 = threshold


        hash_size = 8
        mode = 'db4'
        image_scale = 64
        
        if method == "ssim":
            image1 = cv2.imread(image1)
            image2 = cv2.imread(image2)
            image1 = cv2.resize(image1, (5000, 5000))
            image2 = cv2.resize(image2, (5000, 5000))
            image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
            image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
            s = ssim(image1, image2, multichannel=True)
            if s > threshold1:
                return True,s
            return False,s

        elif method == "dhash":
            image1 = Image.open(image1)
            image2 = Image.open(image2)
            dhash1 = imagehash.dhash(image1, hash_size = hash_size)
            dhash2 = imagehash.dhash(image2, hash_size = hash_size)
            s = self.cal_similar(dhash1, dhash2)
            if s > threshold2:
                return True,s
            return False,s

        elif method == "whash":
            image1 = Image.open(image1)
            image2 = Image.open(image2)
            whash1 = imagehash.whash(image1, image_scale = image_scale, hash_size = hash_size, mode = mode)
            whash2 = imagehash.whash(image2, image_scale = image_scale, hash_size = hash_size, mode = mode)
            s = self.cal_similar(whash1, whash2)
            if s > threshold3:
                return True,s
            return False,s

        if method == "all":
            pass

# from Similarity import Similarity
# image1 = "crop1.png"
# image2 = "crop2.png"
# s = Similarity()
# s.similarity(image1, image2, method="ssim")
