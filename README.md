# JSC power tool

Heavily WIP.

## Build and install
```
cd jpwr
python -m build
pip install dist/jwpr-0.0.4-py3-none-any.whl
```

## CLI tool
ROCM-supported GPU:
```
ᐅ jpwr --methods rocm --df-out energy_meas --df-filetype csv stress-ng --gpu 8 -t 5
Measuring Energy while executing ['stress-ng', '--gpu', '8', '-t', '5']
stress-ng: info:  [79366] setting to a 5 secs run per stressor
stress-ng: info:  [79366] dispatching hogs: 8 gpu
stress-ng: info:  [79375] gpu: GL_VENDOR: AMD
stress-ng: info:  [79375] gpu: GL_VERSION: OpenGL ES 3.2 Mesa 24.1.3-arch1.2
stress-ng: info:  [79375] gpu: GL_RENDERER: AMD Radeon RX 6800 XT (radeonsi, navi21, LLVM 18.1.8, DRM 3.57, 6.9.6-273-tkg-bore)
stress-ng: info:  [79366] skipped: 0
stress-ng: info:  [79366] passed: 8: gpu (8)
stress-ng: info:  [79366] failed: 0
stress-ng: info:  [79366] metrics untrustworthy: 0
stress-ng: info:  [79366] successful run completed in 5.03 secs
Power data:
       timestamps  rocm:0
0    1.720624e+09    17.0
1    1.720624e+09    20.0
2    1.720624e+09    20.0
3    1.720624e+09    33.0
4    1.720624e+09    33.0
..            ...     ...
96   1.720624e+09    45.0
97   1.720624e+09    46.0
98   1.720624e+09    46.0
99   1.720624e+09    46.0
100  1.720624e+09    46.0

[101 rows x 2 columns]
Energy data:
rocm:0    0.061672
dtype: float64
Additional data:
energy_from_counter:
   rocm:0
0     0.0
Writing measurements to energy_meas
Writing power df to energy_meas/power.csv
Writing energy df to energy_meas/energy.csv
Writing energy_from_counter df to energy_meas/energy_from_counter.csv
```
Grace-Hopper node:
```
ᐅ jpwr --methods gh --df-out energy_meas --df-filetype h5 stress-ng --cpu 24 -t 10
Measuring Energy while executing ['stress-ng', '--cpu', '24', '-t', '10']
stress-ng: info:  [28202] setting to a 10 secs run per stressor
stress-ng: info:  [28202] dispatching hogs: 24 cpu
stress-ng: info:  [28202] skipped: 0
stress-ng: info:  [28202] passed: 24: cpu (24)
stress-ng: info:  [28202] failed: 0
stress-ng: info:  [28202] metrics untrustworthy: 0
stress-ng: info:  [28202] successful run completed in 10.05 secs
Power data:
       timestamps  gh:Module  gh:Grace  gh:CPU  gh:SysIO
0    1.720624e+09    134.209    48.309  46.131     0.409
1    1.720624e+09    134.209    48.309  46.131     0.409
2    1.720624e+09    134.209    48.309  46.131     0.409
3    1.720624e+09    134.209    48.309  46.131     0.409
4    1.720624e+09    134.209    48.309  46.131     0.409
..            ...        ...       ...     ...       ...
196  1.720624e+09    184.575   101.150  98.596     1.048
197  1.720624e+09    184.575   101.150  98.596     1.048
198  1.720624e+09    184.575   101.150  98.596     1.048
199  1.720624e+09    184.533   101.057  98.552     1.064
200  1.720624e+09    184.533   101.057  98.552     1.064

[201 rows x 5 columns]
Energy data:
gh:Module    0.498618
gh:Grace     0.268936
gh:CPU       0.261719
gh:SysIO     0.002778
dtype: float64
Writing measurements to energy_meas
Writing power df to energy_meas/power.h5
Writing energy df to energy_meas/energy.h5
```

see `src/jwpr/clitool.py` for programmatic usage


