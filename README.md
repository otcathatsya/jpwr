# JSC power tool

Heavily WIP.

## Build and install
```
cd jpwr
python -m build
pip install dist/jwpr-0.0.1-py3-none-any.whl
```

## CLI tool
```
jpwr --gpu_method rocm <command>
jpwr --gpu_method pynvml <command>
```

see `test/` or `src/jwpr/clitool.py` for programmatic usage


