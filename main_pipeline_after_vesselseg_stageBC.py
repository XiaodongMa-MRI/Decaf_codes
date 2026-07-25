#!/usr/bin/env python3
#!/usr/bin/env python3
"""
Step 3: Vessel segmentation + analysis pipeline
================================================
For a new subject, change CONFIG, then run in stages:

  [Manual: open ITK-SNAP, check skeleton_segments.nii.gz + p01_multilabel.nii.gz,
           set SKIP_SEGMENTS, confirm nnInteractive green light]

  Stage B (after review):
    python run_step3.py   with RUN_PART_B=True, others=False

  Stage C (analysis):
    python run_step3.py   with RUN_BUILD_GRAPH=True, RUN_AREA_PI=True,
                               RUN_EXPORT=True, others=False
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


#!!! Manually set SKIP_SEGMENTS: 
# open ITK-SNAP, check skeleton_segments.nii.gz + p01_multilabel.nii.gz,
# set SKIP_SEGMENTS, confirm nnInteractive green light

SUBJECT_SKIP_SEGMENTS_LIST = {
    "20260512_Tsinghua_Subj1": [4],
}

# number of cardiac phases
N_PHASES    = 25

def main():
    
    for SUBJECT_ID, SKIP_SEGMENTS in SUBJECT_SKIP_SEGMENTS_LIST.items():

        print('Processing subject:', SUBJECT_ID)
       
        function_step3.function_step3_stage_b(
            BASE_DICOM,
            SUBJECT_ID,
            N_PHASES,
            SKIP_SEGMENTS,
        )
        function_step3.function_step3_stage_c(
            BASE_DICOM,
            SUBJECT_ID,
            N_PHASES,
            SKIP_SEGMENTS,
            HAS_CSF=True,
            RUN_BUILD_GRAPH=True,
            RUN_AREA_PI=True,
            RUN_EXPORT=True,
        )    
        
    print("\n" + "=" * 60)
    print("Step 3 - Stage B and C complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
