#!/usr/bin/env python3
"""
Step 3: Vessel segmentation + analysis pipeline
================================================
For a new subject, change CONFIG, then run in stages:

  Stage A (before manual review):
    python run_step3.py   with RUN_PART_A=True, others=False
    → outputs: skeleton visualizations + phase 1 segmentation

Environment requirements:
  - nnInteractive annotation environment must be configured
  - ITK-SNAP must be installed and open
  - nnInteractive server must be running (green light in ITK-SNAP plugin)
  - Start server at: http://localhost:xxxx before running Part A or B
  - Check server address in step3_itksnapvessel/planb_inference.py
"""

import step3_itksnapvessel.function_step3 as function_step3

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

def main():
    
    for SUBJECT_ID in SUBJECT_ID_LIST:
        
        print('Processing subject:', SUBJECT_ID)
        
        SKIP_SEGMENTS = None  # set to None for stage_a
        function_step3.function_step3_stage_a(
            BASE_DICOM,
            SUBJECT_ID,
            N_PHASES,
            SKIP_SEGMENTS,
        )

    print("\n" + "=" * 60)
    print("Step 3 - Stage A complete.")
    print("=" * 60)



if __name__ == "__main__":
    main()
