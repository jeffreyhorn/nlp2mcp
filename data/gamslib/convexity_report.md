# GAMSLIB Convexity Verification Report

**Generated:** 2026-01-01
**Total Models:** 219

## Summary Statistics

| Classification       | Count | Percentage |
|---------------------|-------|------------|
| Verified Convex (LP) | 57    | 26.0%      |
| Likely Convex (NLP/QCP) | 103 | 47.0%      |
| Excluded            | 4     | 1.8%       |
| Errors              | 55    | 25.1%      |

## Classification Criteria

- **Verified Convex**: LP models with MODEL STATUS = 1 (Optimal) and SOLVER STATUS = 1. These are mathematically guaranteed to be convex.
- **Likely Convex**: NLP/QCP models with MODEL STATUS = 1 or 2 (Optimal/Locally Optimal) and SOLVER STATUS = 1. These solved successfully but convexity cannot be guaranteed from solver output alone.
- **Excluded**: Models that are infeasible (MODEL STATUS = 4 or 5). Not suitable for convexity testing.
- **Error**: Models that could not be verified due to license limits, compilation errors, missing solve statements, or other issues.

## Verified Convex Models (57)

Models with mathematically guaranteed convexity (LP with optimal solution):

| Model | Objective Value |
|-------|-----------------|
| agreste | 17706.43 |
| aircraft | 1566.04 |
| ajax | 441003.60 |
| ampl | 79.34 |
| apl1p | 24515.65 |
| apl1pca | 15902.49 |
| blend | 4.98 |
| china | 40561.57 |
| clearlak | 93.75 |
| danwolfe | 3359.47 |
| decomp | 60.00 |
| demo1 | 1898.52 |
| dinam | 251.37 |
| egypt | 4134175.70 |
| fawley | 2899.25 |
| feasopt1 | 96.75 |
| ferts | 58793.82 |
| ibm1 | 287.14 |
| imsl | 1.13 |
| indus | 901.16 |
| iswnm | 114.04 |
| jobt | 21343.06 |
| kand | 2613.00 |
| lands | 381.85 |
| lop | 20244.00 |
| marco | 0.00 |
| markov | 2401.58 |
| mexls | 27569.60 |
| mexss | 538.81 |
| mine | 17500.00 |
| nebrazil | 3385.43 |
| orani | -1.60 |
| pak | 1075.55 |
| paklive | 19468.09 |
| paperco | 4615.42 |
| pdi | 294070.00 |
| port | 0.30 |
| prodmix | 18666.67 |
| prodsp2 | 17845.61 |
| robert | 11025.00 |
| robustlp | -2.33 |
| sarf | 79122.66 |
| senstran | 163.98 |
| shale | 9354.86 |
| solveopt | 6.00 |
| sparta | 3466.38 |
| spatequ | 7906.95 |
| srkandw | 2613.00 |
| sroute | 6468.00 |
| srpchase | 0.40 |
| tabora | 8471.96 |
| tfordy | 102.04 |
| tforss | 2177.80 |
| trnsport | 153.68 |
| turkpow | 12657.77 |
| uimp | 1571.05 |
| whouse | -600.00 |

## Likely Convex Models (103)

NLP/QCP models that solved successfully (local or global optimum found):

| Model | Objective Value | Model Status |
|-------|-----------------|--------------|
| abel | 225.19 | 2 |
| alkyl | -1.77 | 2 |
| bearing | 19517.33 | 2 |
| camcge | 191.73 | 2 |
| camshape | 4.28 | 2 |
| catmix | -0.05 | 2 |
| cclinpts | -3.00 | 2 |
| cesam | 0.01 | 1 |
| cesam2 | 0.51 | 2 |
| chain | 5.07 | 2 |
| chakra | 179.13 | 2 |
| chem | -47.71 | 2 |
| chenery | 1058.92 | 2 |
| circle | 4.57 | 2 |
| cpack | 0.37 | 2 |
| dispatch | 7.95 | 2 |
| dyncge | 539570.50 | 2 |
| elec | 243.81 | 2 |
| etamac | 15.29 | 2 |
| fdesign | 1.05 | 2 |
| feedtray | 13.41 | 2 |
| ganges | 6395.54 | 2 |
| gangesx | 6395.54 | 2 |
| gastrans | 89.09 | 2 |
| glider | 1282.40 | 2 |
| gtm | -543.57 | 2 |
| gussrisk | 148.21 | 1 |
| harker | 706.31 | 2 |
| hhfair | 87.16 | 2 |
| hhmax | 13.93 | 1 |
| himmel11 | -30665.54 | 2 |
| himmel16 | 0.68 | 2 |
| house | 4500.00 | 2 |
| hs62 | -26272.52 | 2 |
| hydro | 4366944.16 | 2 |
| iobalance | 7.62 | 2 |
| irscge | 26.09 | 2 |
| korcge | 339.21 | 2 |
| launch | 2257.80 | 2 |
| least | 14085.14 | 2 |
| like | -1138.41 | 2 |
| lmp2 | 4024.39 | 2 |
| lnts | 0.55 | 2 |
| lrgcge | 25.77 | 2 |
| mathopt1 | 1.00 | 2 |
| mathopt2 | 0.00 | 2 |
| mathopt3 | 0.00 | 2 |
| mathopt4 | 0.00 | 2 |
| maxmin | 0.35 | 2 |
| meanvar | 0.03 | 2 |
| mhw4d | 27.87 | 2 |
| mhw4dx | 27.87 | 2 |
| mingamma | -0.12 | 2 |
| mlbeta | 25.32 | 2 |
| mlgamma | -155.35 | 2 |
| moncge | 25.98 | 2 |
| nemhaus | 0.00 | 1 |
| nonsharp | 0.89 | 1 |
| otpop | 4217.80 | 2 |
| partssupply | 0.92 | 2 |
| pindyck | 1170.49 | 2 |
| pollut | 5353268.63 | 2 |
| polygon | 0.78 | 2 |
| process | 2410.83 | 2 |
| procmean | 14.17 | 2 |
| prolog | -0.00 | 2 |
| ps10_s | 0.53 | 2 |
| ps10_s_mn | 0.40 | 2 |
| ps2_f | 0.92 | 2 |
| ps2_f_eff | 1.25 | 2 |
| ps2_f_inf | 0.83 | 2 |
| ps2_f_s | 0.87 | 2 |
| ps2_s | 0.87 | 2 |
| ps3_f | 1.38 | 2 |
| ps3_s | 1.16 | 2 |
| ps3_s_gic | 1.16 | 2 |
| ps3_s_mn | 1.05 | 2 |
| ps3_s_scp | -0.61 | 2 |
| ps5_s_mn | 0.43 | 2 |
| qabel | 46965.04 | 2 |
| qdemo7 | 1589042.39 | 2 |
| qsambal | 3.97 | 2 |
| quocge | 25.68 | 2 |
| ramsey | 2.49 | 2 |
| rbrock | 0.00 | 2 |
| robot | 9.15 | 2 |
| rocket | 1.01 | 2 |
| sambal | 3.97 | 2 |
| sample | 726.68 | 2 |
| saras | 4351376.56 | 2 |
| ship | 5.54 | 2 |
| splcge | 27.14 | 2 |
| springchain | -185.45 | 2 |
| stdcge | 26.09 | 2 |
| tricp | 3838.27 | 2 |
| trig | 0.00 | 2 |
| trnspwl | 8.80 | 2 |
| trussm | 0.45 | 2 |
| turkey | 29078.21 | 1 |
| twocge | 56.78 | 2 |
| wall | 1.00 | 2 |
| weapons | 1735.57 | 2 |
| worst | 20941621.79 | 2 |

## Excluded Models (4)

Models excluded due to infeasibility:

| Model | Reason | Model Status |
|-------|--------|--------------|
| alan | Model is Infeasible | 4 |
| circpack | Model is Locally Infeasible | 5 |
| epscm | Model is Infeasible | 4 |
| trigx | Model is Locally Infeasible | 5 |

## Error Categories (55)

### License Limit Errors (11)

Models that exceed GAMS demo license limits (NLP: 1000 rows/cols, LP: 2000 rows/cols):

- airsp
- airsp2
- andean
- emfl
- indus89
- jbearing
- minsurf
- msm
- phosdis
- torsion

### No Solve Summary Found (15)

Models that don't produce a standard solve summary (may use special solve workflows, multiple solves, or no solve statement):

- asyncloop
- embmiex1
- gussgrid
- maxcut
- mhw4dxx
- netgen
- prodsp
- qfilter
- scenmerge
- sipres
- spbenders1
- spbenders2
- spbenders4
- tgridmix
- trnsgrid

### GAMS Compilation Errors (18)

Models with missing include files or other compilation dependencies:

- dqq
- gasoil
- gqapsdp
- kqkpsdp
- methanol
- pinene
- pool
- popdynm
- qcp1
- qp1
- qp1x
- qp2
- qp3
- qp4
- qp5
- qp7
- sddp
- t1000
- trnspwlx

### Unexpected Status Combinations (7)

Models with status combinations not covered by classification rules:

| Model | Solver Status | Model Status | Objective |
|-------|---------------|--------------|-----------|
| chance | 1 | 2 | 29.89 |
| demo7 | 1 | 2 | 1589042.39 |
| gancnsx | 1 | 16 | - |
| immun | 1 | 2 | 0.00 |
| minlphi | 1 | 10 | 316.69 |
| qalan | 1 | 8 | 2.93 |
| srcpm | 1 | 2 | -2109.78 |

Note: These models have solver status 1 but unusual model status codes (8=Integer Solution, 10=Integer Infeasible, 16=No Solution) or were classified as "unknown" due to model type detection issues.

### Solver Errors (4)

Models where the solver did not complete normally:

| Model | Solver Status | Model Status | Error |
|-------|---------------|--------------|-------|
| guss2dim | 1 | 14 | Model status 14 (No Solution Returned) |
| gussex1 | 1 | 14 | Model status 14 (No Solution Returned) |
| lmp1 | 5 | 6 | Solver status 5 (Evaluation Error) |
| lmp3 | 5 | 6 | Solver status 5 (Evaluation Error) |

## Notes

1. **Demo License Limitations**: The GAMS demo license restricts model size. Larger models require a full license for verification.

2. **Compilation Dependencies**: Some GAMSLIB models depend on external include files or data files not present in the standalone .gms files.

3. **Special Solve Workflows**: Models using async solves, grid solves, or scenario-based approaches may not produce standard solve summaries.

4. **Convexity Interpretation**:
   - "Verified convex" means the LP solver found a global optimum, confirming convexity.
   - "Likely convex" means an NLP solver found a local optimum; the model may or may not be convex.
   - Models with multiple local optima may still report success but are not convex.

5. **Verification Date**: 2026-01-01 09:02:17
