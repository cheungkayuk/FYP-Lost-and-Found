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

    def ssim_sim(self, image1, image2):
        image1 = cv2.imread(image1)
        image2 = cv2.imread(image2)
        image1 = cv2.resize(image1, (5000, 5000))
        image2 = cv2.resize(image2, (5000, 5000))            
        image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
        s = ssim(image1, image2)     
        return s
    
    def dhash(self, image1, image2):
        hash_size = 8
        image1 = Image.open(image1)
        image2 = Image.open(image2)
        dhash1 = imagehash.dhash(image1, hash_size = hash_size)
        dhash2 = imagehash.dhash(image2, hash_size = hash_size)
        s = self.cal_similar(dhash1, dhash2)
        return s

    def whash(self, image1, image2):
        hash_size = 8
        mode = 'db4'
        image_scale = 64
        image1 = Image.open(image1)
        image2 = Image.open(image2)
        whash1 = imagehash.whash(image1, image_scale = image_scale, hash_size = hash_size, mode = mode)
        whash2 = imagehash.whash(image2, image_scale = image_scale, hash_size = hash_size, mode = mode)           
        s = self.cal_similar(whash1, whash2)
        return s
    
    def sim_compare(self, s, threshold):
        if s > threshold:
            return True
        return False

    def similarity (self, image1, image2, method = "all", threshold1=0.85, threshold2=0.8, threshold3=0.8, threshold_sum=3):
        
        if method == "ssim":
            s_ssim = self.ssim_sim(image1, image2)
            if self.sim_compare(s_ssim, threshold1):
                return True,s_ssim
            return False,s_ssim

        elif method == "dhash":
            s_dhash = self.dhash(image1, image2)
            if self.sim_compare(s_dhash, threshold2):
                return True,s_dhash
            return False,s_dhash

        elif method == "whash":
            s_whash = self.whash(image1, image2)
            if self.sim_compare(s_whash, threshold3):
                return True,s_whash
            return False,s_whash

        elif method == "all":
            s_ssim = self.ssim_sim(image1, image2)
            s_dhash = self.dhash(image1, image2) 
            s_whash = self.whash(image1, image2)
            if sum([self.sim_compare(s_ssim, threshold1), self.sim_compare(s_dhash, threshold2), self.sim_compare(s_whash, threshold3)]) >= threshold_sum:
                 return True,s_ssim,s_dhash,s_whash
            return False,s_ssim,s_dhash,s_whash

# from Similarity import Similarity
# image1 = "crop1.png"
# image2 = "crop2.png"
# s = Similarity()
# s.similarity(image1, image2, method="ssim")
