#!/usr/bin/env python3
"""
Step 3: Vessel segmentation + analysis pipeline
================================================
  Stage A (before manual review):
    function_step3(..., RUN_STAGE_A=True, RUN_STAGE_B=False, RUN_STAGE_C=False)
    → outputs: skeleton visualizations + phase 1 segmentation

  [Manual: open ITK-SNAP, check skeleton_segments.nii.gz + p01_multilabel.nii.gz,
           set SKIP_SEGMENTS, confirm nnInteractive green light]

  Stage B (after review):
    function_step3(..., RUN_STAGE_A=False, RUN_STAGE_B=True, RUN_STAGE_C=False)

  Stage C (analysis):
    function_step3(..., RUN_STAGE_A=False, RUN_STAGE_B=False, RUN_STAGE_C=True)

Environment requirements:
  - nnInteractive annotation environment must be configured
  - ITK-SNAP must be installed and open
  - nnInteractive server must be running (green light in ITK-SNAP plugin)
  - Start server at: http://localhost:xxxx before running Part A or B
  - Check server address in step3_itksnapvessel/planb_inference.py
"""
import multiprocessing
multiprocessing.set_start_method('fork', force=True)

import os

try:
    from .area_pi import compute_area_pi
    from .build_graph import build_graph
    from .export_results import export_vessel_only, export_with_csf
    from .planb_inference import run_part_a, run_part_b
except ImportError:
    from area_pi import compute_area_pi
    from build_graph import build_graph
    from export_results import export_vessel_only, export_with_csf
    from planb_inference import run_part_a, run_part_b


def _make_step3_config(BASE_DICOM, SUBJECT_ID, N_PHASES=25):
    BASE_DIR = os.path.join(BASE_DICOM, SUBJECT_ID)
    NIFTI_DIR = os.path.join(BASE_DIR, f"nifti_crop480_{SUBJECT_ID}")
    PLANB_OUTPUT_DIR = os.path.join(BASE_DIR, f"output_{SUBJECT_ID}")
    STEP1_DIR = os.path.join(PLANB_OUTPUT_DIR, "results/step1_fromB")
    STEP2_DIR = os.path.join(PLANB_OUTPUT_DIR, "results/step2_multilabel")

    return dict(
        BASE_DIR=BASE_DIR,
        SUBJECT_ID=SUBJECT_ID,
        N_PHASES=N_PHASES,
        NIFTI_DIR=NIFTI_DIR,
        MASK_PATH=os.path.join(NIFTI_DIR, "p1_m.nii.gz"),
        PLANB_OUTPUT_DIR=PLANB_OUTPUT_DIR,
        STEP1_DIR=STEP1_DIR,
        STEP2_DIR=STEP2_DIR,
        ADC_FOLDER=os.path.join(BASE_DIR, f"adc_corrected_maps_{SUBJECT_ID}"),
        CROP_DIR=NIFTI_DIR,
        OUT_MAT_VESSEL=os.path.join(STEP2_DIR, f"vessel_pi_{SUBJECT_ID}.mat"),
        OUT_MAT_COMBINED=os.path.join(STEP2_DIR, f"vessel_csf_{SUBJECT_ID}.mat"),
    )


def print_step3_environment_check():
    print("""
    ┌─────────────────────────────────────────────────────┐
    │  ENVIRONMENT CHECK before running Part A or B:      │
    │  1. nnInteractive annotation environment configured  │
    │  2. ITK-SNAP is open, ssh to server                  |
    |  python -m itksnap_dls --host 0.0.0.0 --port 8912    │
    │  3. nnInteractive plugin shows GREEN light           │
    │  (server running at http://localhost:8912)  or others│
    └─────────────────────────────────────────────────────┘
    """)


def function_step3_part_a(
    config,
    total_points=100,
    min_branch_length=1,
    bp_dilation=0,
    min_spur_length=3,
    soft_margin=5,
    n_workers_edt=16,
    bbox_pad=80,
    skip_segments=None,
):

    print("\n[Step 3 Part A] Skeleton + seeds + phase 1 inference")
    run_part_a(
        nifti_dir=config["NIFTI_DIR"],
        mask_path=config["MASK_PATH"],
        output_dir=config["PLANB_OUTPUT_DIR"],
        total_points=total_points,
        min_branch_length=min_branch_length,
        bp_dilation=bp_dilation,
        min_spur_length=min_spur_length,
        soft_margin=soft_margin,
        n_workers=n_workers_edt,
        bbox_pad=bbox_pad,
        skip_segments=skip_segments,
    )
    print(f"""
    ┌─────────────────────────────────────────────────────┐
    │  MANUAL REVIEW in ITK-SNAP:                         │
    │  Open: {config["PLANB_OUTPUT_DIR"]}/
    │    - skeleton_segments.nii.gz                       │
    │    - p01_multilabel.nii.gz                          │
    │    - seed_points_vis.nii.gz                         │
    │  Note segment IDs to skip, update SKIP_SEGMENTS     │
    │  Then run Stage B                                  │
    └─────────────────────────────────────────────────────┘
    """)


def function_step3_part_b(config, skip_segments=None):
    if skip_segments is None:
        skip_segments = [10, 18]

    print("\n[Step 3 Part B] Batch all phases")
    run_part_b(
        nifti_dir=config["NIFTI_DIR"],
        mask_path=config["MASK_PATH"],
        output_dir=config["PLANB_OUTPUT_DIR"],
        n_phases=config["N_PHASES"],
        skip_segments=skip_segments,
    )


def function_step3_build_graph(
    config,
    skip_segments=None,
    bif_cluster_radius=3,
    ep_cluster_radius=2,
    mask_downsample=2,
):
    if skip_segments is None:
        skip_segments = [10, 18]

    print("\n[Step 3] Build vessel graph + 3D HTML")
    build_graph(
        planb_output_dir=config["PLANB_OUTPUT_DIR"],
        out_dir=config["STEP1_DIR"],
        n_phases=config["N_PHASES"],
        skip_segments=skip_segments,
        bif_cluster_radius=bif_cluster_radius,
        ep_cluster_radius=ep_cluster_radius,
        mask_downsample=mask_downsample,
    )
    print(f"  3D visualization: {config['STEP1_DIR']}/vessel_graph_3d.html")


def function_step3_area_pi(
    config,
    sample_spacing_mm=0.5,
    min_samples=5,
    max_samples=150,
    min_seg_length_mm=3.0,
    s_skip_mm=2.0,
    slab_half_mm=0.5,
    r_max_mm=20.0,
    recenter_radius_mm=2.5,
    recenter_slab_mm=1.0,
    smooth_window=15,
    path_smooth_mm=1.0,
    xsec_n_slices=9,
    xsec_radius_mm=5.0,
    xsec_resolution=0.2,
    xsec_phase=1,
):
    print("\n[Step 3] Cross-section area + pulsatility index")
    compute_area_pi(
        step1_dir=config["STEP1_DIR"],
        planb_output_dir=config["PLANB_OUTPUT_DIR"],
        out_dir=config["STEP2_DIR"],
        n_phases=config["N_PHASES"],
        sample_spacing_mm=sample_spacing_mm,
        min_samples=min_samples,
        max_samples=max_samples,
        min_seg_length_mm=min_seg_length_mm,
        s_skip_mm=s_skip_mm,
        slab_half_mm=slab_half_mm,
        r_max_mm=r_max_mm,
        recenter_radius_mm=recenter_radius_mm,
        recenter_slab_mm=recenter_slab_mm,
        smooth_window=smooth_window,
        path_smooth_mm=path_smooth_mm,
        xsec_n_slices=xsec_n_slices,
        xsec_radius_mm=xsec_radius_mm,
        xsec_resolution=xsec_resolution,
        xsec_phase=xsec_phase,
    )


def function_step3_export(
    config,
    has_csf=True,
    n_workers_adc=6,
    perivas_dist_mm=3.0,
    grid_res_mm=0.2,
    grid_half_mm=6.0,
):
    if has_csf:
        print("\n[Step 3] Export vessel PI + paravascular ADC -> combined .mat")
        export_with_csf(
            step1_dir=config["STEP1_DIR"],
            step2_dir=config["STEP2_DIR"],
            vessel_dir=config["PLANB_OUTPUT_DIR"],
            adc_folder=config["ADC_FOLDER"],
            crop_dir=config["CROP_DIR"],
            out_mat=config["OUT_MAT_COMBINED"],
            n_phases=config["N_PHASES"],
            n_workers=n_workers_adc,
            perivas_dist_mm=perivas_dist_mm,
            grid_res_mm=grid_res_mm,
            grid_half_mm=grid_half_mm,
        )
    else:
        print("\n[Step 3] Export vessel PI only -> .mat")
        export_vessel_only(
            step1_dir=config["STEP1_DIR"],
            step2_dir=config["STEP2_DIR"],
            out_mat=config["OUT_MAT_VESSEL"],
        )


def function_step3_stage_a(
    BASE_DICOM,
    SUBJECT_ID,
    N_PHASES=25,
    SKIP_SEGMENTS=None,
):
    config = _make_step3_config(BASE_DICOM, SUBJECT_ID, N_PHASES)
    print_step3_environment_check()
    function_step3_part_a(config, skip_segments=SKIP_SEGMENTS)


def function_step3_stage_b(
    BASE_DICOM,
    SUBJECT_ID,
    N_PHASES=25,
    SKIP_SEGMENTS=None,
):
    if SKIP_SEGMENTS is None:
        SKIP_SEGMENTS = [10, 18]

    config = _make_step3_config(BASE_DICOM, SUBJECT_ID, N_PHASES)
    print_step3_environment_check()
    function_step3_part_b(config, skip_segments=SKIP_SEGMENTS)


def function_step3_stage_c(
    BASE_DICOM,
    SUBJECT_ID,
    N_PHASES=25,
    SKIP_SEGMENTS=None,
    HAS_CSF=True,
    RUN_BUILD_GRAPH=True,
    RUN_AREA_PI=True,
    RUN_EXPORT=True,
):
    if SKIP_SEGMENTS is None:
        SKIP_SEGMENTS = [10, 18]

    config = _make_step3_config(BASE_DICOM, SUBJECT_ID, N_PHASES)

    if RUN_BUILD_GRAPH:
        function_step3_build_graph(config, skip_segments=SKIP_SEGMENTS)

    if RUN_AREA_PI:
        function_step3_area_pi(config)

    if RUN_EXPORT:
        function_step3_export(config, has_csf=HAS_CSF)

