import cv2
import imagehash
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import mean_squared_error as mse

# Class Similarity
class Similarity:
    # calculate similarity of 2 images (image1 and image2)
    # Input:
    #       hash1: hash of image1
    #       hash2: hash of image2
    # Output:
    #       sim: the similarity of 2 images in the value of 0-1
    def cal_similar(self, hash1, hash2):
        sim = 1 - (hash1 - hash2) / len(hash1.hash) ** 2
        return sim

    # calculate the ssim of 2 images (image1 and image2)
    # Input:
    #       image1: file path of image1
    #       image2: file path of image2
    # Output:
    #       s: the similarity of 2 images in the value of 0-1 regarding SSIM
    def ssim_sim(self, image1, image2):
        image1 = cv2.imread(image1)
        image2 = cv2.imread(image2)
        image1 = cv2.resize(image1, (5000, 5000))
        image2 = cv2.resize(image2, (5000, 5000))            
        image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
        s = ssim(image1, image2)     
        return s
    
    # calculate the similarity using dhash
    # Input:
    #       image1: file path of image1
    #       image2: file path of image2
    # Output:
    #       s: the similarity of 2 images in the value of 0-1 regarding dhash
    def dhash(self, image1, image2):
        hash_size = 8
        image1 = Image.open(image1)
        image2 = Image.open(image2)
        dhash1 = imagehash.dhash(image1, hash_size = hash_size)
        dhash2 = imagehash.dhash(image2, hash_size = hash_size)
        s = self.cal_similar(dhash1, dhash2)
        return s

    # calculate the similarity using whash
    # mode = 'db4'
    # Input:
    #       image1: file path of image1
    #       image2: file path of image2
    # Output:
    #       s: the similarity of 2 images in the value of 0-1 regarding whash
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
    
    # Compare if the calculated similarity is greater than the threshold
    # Input:
    #       s: the calculated similarity
    #       threshold: the similarity threshold
    # Output:
    #       If s > threshold, return True
    #       Otherwise, return False
    def sim_compare(self, s, threshold):
        if s > threshold:
            return True
        return False

    # Compare the similarity of image1 and image2 (with method = 'ssim', 'dhash', 'whash', 'all')
    # Input:
    #       image1: the file path of image1
    #       image2: the file path of image2
    #       method: which method to use for the comparison, method = ['ssim', 'dhash', 'whash', 'all'], default = "all", 
    #       threshold1: the threshold for SSIM method, default = 0.85, 
    #       threshold2: the threshold for dhash method, default = 0.8, 
    #       threshold3: the threshold for whash method, default = 0.8, 
    #       threshold_sum: the threshold for all method (count the number of True), default = 3
    #                      i.e. return True in all methods ('ssim', 'dhash', and 'whash')
    # Output:
    # A tuple of (boolean, similarity)
    #       If s >= threshold, return True
    #       Otherwise, return False
    #       similarity: method = 'ssim', 'dhash' or 'whash': the calculated similarity
    #                   method = 'all': the calculated similarities from 'ssim', 'dhash' and 'whash' method
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
