# Examples Directory

This directory contains example scripts and test cases for the Symphony LIVING System.

## Prerequisites

Before running any examples, install the required dependencies:

```bash
cd /path/to/symphony_living_system
pip install -r protocol/requirements.txt
```

## Available Examples

### test_drawing_interpretation.py

Comprehensive test suite for the Drawing Interpretation System.

**Run with:**
```bash
python examples/test_drawing_interpretation.py
```

**Tests:**
- Full drawing analysis with multiple geometric patterns
- Platonic solid recognition (all 5 solids)
- Fibonacci spiral detection
- Resonance frequency mapping
- Divine message generation

**Expected Output:**
- Pattern detection results
- Resonance profiles
- Activation levels
- Spiritual interpretations
- Suggested next steps

## Creating Your Own Tests

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'layers'))

from drawing_interpreter import create_interpreter

# Your test code here
```

## Note

Tests use simulated feature data and do not require actual image files. For testing with real images, use the API endpoints or load images directly with the `image_processor` module.
