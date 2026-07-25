# DECAF Pipeline — Cerebrovascular Pulsatility & Glymphatic Analysis

Analysis pipeline for noninvasive MRI quantification of intracranial arterial pulsatility and paravascular CSF dynamics using diffusion-prepared bSSFP cine MRI (DECAF sequence).

## Overview

This pipeline processes 3D radial MRI data (960³, ~0.21mm isotropic) acquired with a diffusion-prepared bSSFP cine sequence across 25 cardiac phases. It quantifies vessel cross-sectional area pulsatility and paravascular CSF apparent diffusion coefficient (ADC) along cerebral arteries (A1, M1, M2, M3, P1, P2 territories), supporting scan-rescan reproducibility studies.

## Pipeline Structure

```
Decaf_codes/
├── step1_dicom2nifti/        # Data preprocessing
├── step1p5_CSFMask/          # Initial CSFMask generation using FSL
├── step2_ADCcalculation/     # CSF segmentation & ADC maps
├── step3_itksnapvessel/      # Vessel segmentation & graph analysis
└── step4_matlabpart/         # Visualization & statistics
```

### Step 1: DICOM → NIfTI preprocessing
**`function_step1.py`** — Convert reconstructed DICOM to NIfTI, with optional processing

| Sub-step | Function | Description |
|----------|----------|-------------|
| 1a | `convert_dicom_to_nifti.py` | b40 phases (25×) + b0 DICOM → NIfTI (960³) |
| 1b | `register.py` | Rigid registration of scan 2 → scan 1 (for reproducibility) |
| 1c | `downsample.py` | 960³ → 480³ (for FSL FAST input) |
| 1d | `crop.py` | Center-crop to 480³ cube (for ITK-SNAP labeling) |

### Step 1: DICOM → NIfTI preprocessing
**`function_step1p5CSFMask.py`** — generate CSF mask using FSL (fast)

### Step 2: ADC calculation
**`function_step2.py`** — CSF segmentation and ADC map generation (run in two stages)

| Sub-step | Function | Description |
|----------|----------|-------------|
| 2a | `upsample.py` | Upsample FSL FAST output 480³ → 960³ |
| 2b | `csf_segmentation.py` | Brain mask + CSF probability threshold |
| 2c | `csf_mask_utils.py` | Morphological opening + QC overlay image |
| 2d | MATLAB (auto) | Convert csfmask.nii.gz → .mat via subprocess |
| 2e | `adc_calculation.py` | ADC computation + bSSFP correction + CSF masking |

ADC correction accounts for bSSFP steady-state signal model with default imaging parameters: d=22ms, TEp=52ms, TR=240ms, segment=32, TE=2.79ms, α=π/4, b=40 s/mm². 
(change imaging parameters if different protocol is used)

### Step 3: Vessel segmentation & analysis
**`function_step3.py`** — nnInteractive-based vessel labeling, graph construction, and pulsatility analysis

| Sub-step | Function | Description |
|----------|----------|-------------|
| Part A | `planb_inference.py` | Skeleton extraction, seed allocation, soft Voronoi regions, phase 1 inference |
| Part B | `planb_inference.py` | Batch inference for all 25 phases |
| Graph | `build_graph.py` | Vessel graph (nodes/edges) + 3D HTML visualization |
| Area/PI | `area_pi.py` | Cross-sectional area measurement + pulsatility index (PI) |
| Export | `export_results.py` | Export to .mat (vessel-only or vessel+CSF) |

Vessel segmentation uses nnInteractive with soft Voronoi clipping to separate adjacent vessels. PI = (max − min) / mean across 25 cardiac phases.

### Step 4: Visualization & statistics (MATLAB)
**`plot_batch_jsoncompat.m`** — Batch plotting and statistical summary

| Component | Description |
|-----------|-------------|
| `vessel_config_editor.html` | Interactive GUI for selecting vessel segments and creating config files |
| `load_json_config.m` | Read JSON config → MATLAB struct (compatible with legacy .m configs) |
| `plot_batch_jsoncompat.m` | Dual-Y area/ADC curves, trace plots with proximal→distal gradient, PI summary |

Outputs per vessel segment: dual-Y mean curve (area + ADC), 2×2 grid (traces + mean±std), PI summary table, and .mat with statistics.

## Quick Start

```bash
# Steps 1-2: Preprocessing and ADC
python main_pipeline_before_vesselseg.py

# [External] After Steps 1-2, do AI-assisted vessel segmentation using ITK-SNAP:
# load the file "nifti_crop480_xxx/phase1.nii.gz" into ITK-SNAP, then segment the lumen of
# the major Circle-Willis arteries in AI mode: BA, PCA, MCA (M1,M2), ACA;
# save the segmentation file as "p1_m.nii.gz".

# Step 3: Vessel analysis
# [External] Start nnInteractive server (default: localhost:8913)

python main_pipeline_after_vesselseg_stageA.py # Part A: skeleton + phase 1
# Check if DICE is reasonable(>0.8)

# Review stageA results in ITK-SNAP, set SKIP_SEGMENTS in main_pipeline_after_vesselseg_stageBC.py
python main_pipeline_after_vesselseg_stageBC.py # Part B: all phases + Build graph + area/PI + export

# Step 4: Visualization (MATLAB)
cd step4_matlabpart
# Open vessel_config_editor.html, select segments, save JSON
# A matlab config file and json file are provided for your reference
# Run plot_curve_save.m in MATLAB, output curve figures and mat file for PI/ADC data summary
```

## Dependencies

**Python:**
- numpy, scipy, nibabel, SimpleITK, matplotlib
- hdf5storage (for MATLAB v7.3 .mat files)
- pydicom (for DICOM mode ADC)
- scikit-image (skeletonize, marching cubes)

**External tools:**
- FSL BET, FAST (brain/CSF segmentation)
- ITK-SNAP + nnInteractive (vessel labeling)
- MATLAB R2022b (visualization, jsondecode)

**MRI acquisition:**
- Siemens scanner (XA30)
- Diffusion-prepared bSSFP cine, 3D Kooshball radial sampling
- 960³ matrix, ~0.21mm isotropic, 25 cardiac phases
- b=0 and b=40 s/mm²

## File Naming Conventions

- `phase{n}.nii.gz` — cardiac phase n (1–25), b=40
- `b0.nii.gz` — b=0 reference volume
- `p{nn}_binary.nii.gz` / `p{nn}_multilabel.nii.gz` — vessel segmentation masks
- `adc_corrected_csf_phase{nn}_single.mat` — corrected ADC with CSF mask
- `paravascular_adc.mat` — final combined vessel area + CSF ADC data
- `case_config_{id}.json` — vessel annotation config (from config editor)

## References
- DECAF: Diffusion-Prepared Cine bSSFP https://onlinelibrary.wiley.com/doi/epdf/10.1002/mrm.70381

## Authors

Chang Ni (Nerissa) — Biomedical Engineering, University of Utah

Xiaodong Ma, Radiology and Imaging Sciences, University of Utah
