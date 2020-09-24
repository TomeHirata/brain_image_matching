import os
# CT image file directory
dicom_file_path = '../dicom_files'
# 染色image directory
template_file_path = '../templates'
# start image of CT images
image_start = 143
# end image index - start image index
image_length = 103

dicom_files = sorted(os.listdir(dicom_file_path))
template_files = sorted(os.listdir(template_file_path))