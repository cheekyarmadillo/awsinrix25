import kagglehub
import cv2
import glob

DEBUG = True

kaggle_data_path: str = kagglehub.dataset_download("farzadnekouei/pothole-image-segmentation-dataset")
kaggle_images_path: str = f"{kaggle_data_path}/Pothole_Segmentation_YOLOv8/train/images/*"

if DEBUG:
    print("Path to dataset files:", kaggle_data_path)
    print(glob.glob("kaggle_images_path"))

images = [cv2.imread(image) for image in glob.glob(kaggle_images_path)]

for image in images:
    cv2.imshow("Image", image)

cv2.waitKey(0)
cv2.destroyAllWindows()

