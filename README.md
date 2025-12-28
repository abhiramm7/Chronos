# Chronos

**Version: 0.0.0**

This is yet another time series analysis library in python. 
This library is implemented in functional programming style to facilitate its use in data pipelines and daisy-chaining it with other libraries.

This library is organized based on the steps involved in time series forecasting:
1. Filtering noisy data
2. Feature engineering
3. Normalization
4. Sequencing
5. Model building
6. Model evaluation
7. Visualization

I am still figuring out what to name this library, so any suggestions are welcome! :)

## Installation

```bash
pip install chronos
```

Or install from source:

```bash
git clone https://github.com/yourusername/chronos.git
cd chronos
pip install -e .
```

## Features

- **Time Series Preprocessing**: Tools for preparing time series data for analysis
  - Shingling: Create sliding window features from time series data

## Usage

### Shingling Time Series

Create sliding window features from uniformly sampled time series data:

```python
import pandas as pd
import numpy as np
from chronos.core import shingle_timeseries

# Create sample data
index = pd.date_range(start='2025-01-01', end='2025-01-31', freq='6h')
data = pd.DataFrame({
    'temperature': np.random.rand(len(index)),
    'humidity': np.random.rand(len(index))
}, index=index)

# Apply shingling with a 12-hour window
shingled_data = shingle_timeseries(data, window_size=pd.Timedelta('12h'))

# Or use an integer window size (number of samples)
shingled_data = shingle_timeseries(data, window_size=2)
```

The resulting DataFrame will have columns like `temperature_t-0`, `temperature_t-1`, `humidity_t-0`, `humidity_t-1`, where `t-0` represents the current time and `t-1` represents one time step back.

## Requirements

- Python >= 3.14
- pandas >= 2.3.3
- numpy >= 2.4.0
- matplotlib >= 3.10.8

## Development

### Setup

```bash
# Install dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
```

## License

MIT License