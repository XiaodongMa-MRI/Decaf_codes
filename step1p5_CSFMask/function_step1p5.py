#!/usr/bin/env python3
"""
Step 1: DICOM -> NIfTI pipeline
================================
for new subject, change CONFIG, then run:
    python run_step1.py
Steps:
  1a. DICOM -> NIfTI (960)
  1b. Register scan2 to scan1     (for 2 scans reproducibility, if only one scan, ignore this)
  1c. Downsample 960 -> 480       (for fsl fast CSF input, if only want vessel result, ignore this)
  1d. Crop center 480^3 cube      (for itksnap labeling, need install itksnap nninteractive environment)
"""

import os
import subprocess


def function_step1p5(BASE_DICOM, SUBJECT_ID):
    
    nifti_dir_s1    = os.path.join(BASE_DICOM, f"{SUBJECT_ID}", f"nifti_480_{SUBJECT_ID}")
    
    cmd = f"""
    export FSLDIR=/APPS/bnl/fsl
    source ${{FSLDIR}}/etc/fslconf/fsl.sh
    export PATH=${{FSLDIR}}/bin:${{PATH}}

    bet2 "{nifti_dir_s1}/phase1.nii.gz" "{nifti_dir_s1}/phase1_480_brain.nii.gz" -f 0.25
    fast -t 2 "{nifti_dir_s1}/phase1_480_brain.nii.gz"
    """
    #print(cmd)
    
    subprocess.run(
    cmd,
    shell=True,
    executable="/usr/bin/bash"
    )
    
    print("\n" + "=" * 60)
    print("Step 1.5 complete.")
    print("=" * 60)

