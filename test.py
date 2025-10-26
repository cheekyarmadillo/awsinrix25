import kagglehub
import cv2
import glob

DEBUG = True

KAGGLE_DATA_PATH: str = kagglehub.dataset_download("farzadnekouei/pothole-image-segmentation-dataset")
KAGGLE_IMAGES_PATH: str = f"{KAGGLE_DATA_PATH}/Pothole_Segmentation_YOLOv8/train/images/*"
KAGGLE_LABELS_PATH: str = f"{KAGGLE_DATA_PATH}/Pothole_Segmentation_YOLOv8/train/labels/*"

if DEBUG:
    print("Path to dataset files:", KAGGLE_DATA_PATH)
    print(glob.glob(KAGGLE_IMAGES_PATH))
    print(glob.glob(KAGGLE_LABELS_PATH))

images = [cv2.imread(image) for image in glob.glob(KAGGLE_IMAGES_PATH)]

for image in images:
    cv2.imshow("Image", image)
    cv2.waitKey(500)

cv2.destroyAllWindows()

