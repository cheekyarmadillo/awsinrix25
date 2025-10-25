import kagglehub

DEBUG = True

kaggle_data_path: str = kagglehub.dataset_download("farzadnekouei/pothole-image-segmentation-dataset")
kaggle_images_path: str = f"{kaggle_data_path}/Pothole_Segmentation_YOLOv8/train/images/*"

if DEBUG:
    import glob
    print("Path to dataset files:", kaggle_data_path)
    print(glob.glob(f"{kaggle_images_path}"))

