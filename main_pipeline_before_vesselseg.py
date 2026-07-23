#!/usr/bin/env python3
"""
This is the main pipeline for processing BBCine data before vessel segmentation
It includes the following 3 steps:
"""
"""
Step 1: DICOM -> NIfTI pipeline

Step 1p5: Generate CSF mask using FSL

Step 2: ADC Calculation Pipeline

"""

import step1_dicom2nifti.function_step1 as function_step1
import step1p5_CSFMask.function_step1p5 as function_step1p5
import step2_ADCcalculation.function_step2 as function_step2

import os
import glob

# Need to change information from here!!!!

# Note: in the subfolder of each subject, 
# there should be only one b0 folder containing "b0" in the name, 
# and only one b1 folder containing "grasp" in the name.

BASE_DICOM    = "/v/ai/nobackup/xma/Trufi_BBCine_results/Dicom_960_Tsinghua" # base dicom folder for all subjects
'''SUBJECT_ID_LIST = [
    "20260512_Tsinghua_Subj1",
    "20260512_Tsinghua_Subj2",
    "20260512_Tsinghua_Subj3",
    "20260512_Tsinghua_Subj4",
    "20260602_Tsinghua_Subj1",
    "20260602_Tsinghua_Subj2",
    "20260602_Tsinghua_Subj3",
    "20260602_Tsinghua_Subj4",
    "20260609_Tsinghua_Subj1",
    "20260609_Tsinghua_Subj2",
    "20260609_Tsinghua_Subj3",
]'''
SUBJECT_ID_LIST = [
    "20260512_Tsinghua_Subj1",
]

# number of cardiac phases
N_PHASES    = 25

# Imaging parameters for ADC calculation, which are used in step 2
ADC_PARAMS = dict(d=22, TEp=52, TR=280, segment=32, TE=2.9, fs=16, b=40)

def main():
    for SUBJECT_ID in SUBJECT_ID_LIST:
        
        print('Processing subject:', SUBJECT_ID)
        
        # find b1 folder (grasp) and b0 folder (b0) in the subject folder
        pattern = os.path.join(BASE_DICOM, SUBJECT_ID, "*grasp*")
        matches = [path for path in glob.glob(pattern) if os.path.isdir(path)]
        B40_DICOM_DIR_S1 = matches[0]

        pattern = os.path.join(BASE_DICOM, SUBJECT_ID, "*b0*")
        matches = [path for path in glob.glob(pattern) if os.path.isdir(path)]
        B0_DICOM_DIR_S1 = matches[0]

        # *** Step 1: DICOM -> NIfTI pipeline ***        
        #function_step1.function_step1(BASE_DICOM, SUBJECT_ID, B40_DICOM_DIR_S1, B0_DICOM_DIR_S1, N_PHASES)

        # *** Step 1p5: Generate CSF mask using FSL ***
        #function_step1p5.function_step1p5(BASE_DICOM, SUBJECT_ID)

        # *** Step 2: ADC Calculation Pipeline ***
        function_step2.function_step2(BASE_DICOM, SUBJECT_ID, B40_DICOM_DIR_S1, B0_DICOM_DIR_S1, N_PHASES, ADC_PARAMS)


if __name__ == "__main__":
    main()
