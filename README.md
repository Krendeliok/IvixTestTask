# Instalation and usage
### 1) Create virtual environment and activate it:
```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

### 2) Install the required packages:
```bash
    pip install -r requirements.txt
```

### 3.1) Run the phase1 script:
```bash
    python phase1/main.py
```

### 3.2) Run the phase2 script:
For this script I`ve added flags to control the source and output filename
```bash
    python phase2/main.py --source <{'api', 'html'}> --output <output_filename>
```
You can run the script without flags, in this case it will use the default values.
To get information about the flags, run:
```bash
    python phase2/main.py --help
```

# Phase 1
### Avarage Throughput: 0.16 requests/sec
### Lines of code: 58 

# Phase 2
## HTML 
### Avarage Throughput: 0.05 pages/sec (because I use selenium to get the data)
### Lines of code: 42

## API
### Avarage Throughput: 1 request for all data
### Lines of code: 32
## Additional 
* Added CLI interface for comfortable usage
* Writing data to .csv file