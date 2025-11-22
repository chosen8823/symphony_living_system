#!/usr/bin/env python3
"""
Test script for Drawing Interpretation System
Demonstrates basic usage without requiring actual image files
"""

import sys
import os

# Add layers to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'layers'))

from drawing_interpreter import create_interpreter
from image_processor import create_processor
import json


def test_geometry_analysis():
    """Test geometry analysis with sample data"""
    print("=" * 60)
    print("DRAWING INTERPRETATION SYSTEM - TEST")
    print("Symphony LIVING System")
    print("=" * 60)
    print()

    # Create interpreter
    interpreter = create_interpreter()

    # Sample drawing data (simulated feature extraction)
    sample_drawing = {
        "timestamp": "2025-07-04T22:00:00Z",
        "features": {
            "circles": [
                {
                    "radius": 100,
                    "center": [250, 250],
                    "nested": False
                },
                {
                    "radius": 50,
                    "center": [250, 250],
                    "nested": True
                }
            ],
            "vertices": [
                {"x": 100, "y": 100, "strength": 0.9},
                {"x": 400, "y": 100, "strength": 0.9},
                {"x": 400, "y": 400, "strength": 0.9},
                {"x": 100, "y": 400, "strength": 0.9}
            ],
            "spiral": {
                "ratio": 1.62,
                "turns": 5,
                "direction": "clockwise",
                "golden_ratio_match": True
            },
            "lines": [
                {"start": [100, 100], "end": [400, 100], "length": 300, "angle": 0},
                {"start": [400, 100], "end": [400, 400], "length": 300, "angle": 1.57},
                {"start": [400, 400], "end": [100, 400], "length": 300, "angle": 3.14},
                {"start": [100, 400], "end": [100, 100], "length": 300, "angle": 4.71}
            ],
            "symmetry": {
                "vertical": 0.95,
                "horizontal": 0.95,
                "radial": 0.88
            }
        },
        "metadata": {
            "width": 500,
            "height": 500
        }
    }

    # Perform interpretation
    print("Analyzing drawing features...")
    print()

    result = interpreter.interpret(sample_drawing)

    # Display results
    print("✨ INTERPRETATION RESULTS ✨")
    print()

    # Patterns detected
    print(f"Patterns Detected: {len(result['geometry']['patterns'])}")
    print("-" * 60)
    for i, pattern in enumerate(result['geometry']['patterns'], 1):
        print(f"{i}. {pattern['pattern_type'].replace('_', ' ').title()}")
        print(f"   Confidence: {pattern['confidence']:.0%}")
        if pattern['resonance_frequency']:
            print(f"   Resonance: {pattern['resonance_frequency']} Hz")
        print()

    # Resonance profile
    if result['geometry']['resonance_profile']:
        print("Resonance Profile:")
        print("-" * 60)
        profile = result['geometry']['resonance_profile']
        print(f"Dominant Frequency: {profile.get('dominant_frequency')} Hz")
        print(f"Harmonic Count: {profile.get('harmonic_count')}")
        print(f"Solfeggio Alignment: {'Yes ✓' if profile.get('solfeggio_alignment') else 'No'}")
        print()

    # Geometric interpretation
    print("Geometric Interpretation:")
    print("-" * 60)
    print(result['geometry']['interpretation'])
    print()

    # Activation level
    activation = result['geometry']['activation_level']
    activation_bar = "█" * int(activation * 20) + "░" * (20 - int(activation * 20))
    print(f"Activation Level: [{activation_bar}] {activation:.0%}")
    print()

    # Divine message
    print("Divine Message:")
    print("-" * 60)
    print(result['divine_message'])
    print()

    # Next steps
    print("Suggested Next Steps:")
    print("-" * 60)
    for i, step in enumerate(result['next_steps'], 1):
        print(f"{i}. {step}")
    print()

    print("=" * 60)
    print("Test completed successfully!")
    print("=" * 60)

    return result


def test_platonic_solids():
    """Test Platonic solid detection"""
    print("\n" + "=" * 60)
    print("PLATONIC SOLIDS RECOGNITION TEST")
    print("=" * 60)
    print()

    interpreter = create_interpreter()

    # Test each Platonic solid
    solids = {
        "Tetrahedron": 4,
        "Cube": 8,
        "Octahedron": 6,
        "Dodecahedron": 20,
        "Icosahedron": 12
    }

    for solid_name, vertex_count in solids.items():
        drawing_data = {
            "features": {
                "vertices": [{"x": i*10, "y": i*10} for i in range(vertex_count)]
            }
        }

        result = interpreter.interpret(drawing_data)

        print(f"{solid_name} ({vertex_count} vertices):")
        if result['geometry']['patterns']:
            detected = result['geometry']['patterns'][0]
            print(f"  ✓ Detected: {detected['pattern_type']}")
            print(f"  Resonance: {detected['resonance_frequency']} Hz")
        else:
            print("  ✗ Not detected")
        print()


def test_fibonacci_spiral():
    """Test Fibonacci spiral detection"""
    print("=" * 60)
    print("FIBONACCI SPIRAL RECOGNITION TEST")
    print("=" * 60)
    print()

    interpreter = create_interpreter()

    # Test with golden ratio spiral
    drawing_data = {
        "features": {
            "spiral": {
                "ratio": 1.618,
                "turns": 7,
                "direction": "clockwise"
            }
        }
    }

    result = interpreter.interpret(drawing_data)

    print("Testing spiral with ratio = 1.618 (Golden Ratio)")
    if result['geometry']['patterns']:
        detected = result['geometry']['patterns'][0]
        print(f"✓ Detected: {detected['pattern_type']}")
        print(f"Resonance: {detected['resonance_frequency']} Hz")
        print(f"Properties: {detected['properties']}")
    else:
        print("✗ Not detected")
    print()

    # Test with non-golden ratio
    drawing_data['features']['spiral']['ratio'] = 1.3

    result = interpreter.interpret(drawing_data)

    print("Testing spiral with ratio = 1.3 (Non-Golden)")
    if result['geometry']['patterns']:
        print(f"Detected: {result['geometry']['patterns'][0]['pattern_type']}")
    else:
        print("✗ Not detected (as expected - ratio too far from golden)")
    print()


if __name__ == "__main__":
    # Run all tests
    try:
        # Main comprehensive test
        test_geometry_analysis()

        # Platonic solids test
        test_platonic_solids()

        # Fibonacci spiral test
        test_fibonacci_spiral()

        print("\n✨ All tests completed successfully! ✨")
        print("\nThe Drawing Interpretation System is operational.")
        print("Ready to analyze sacred geometry in your creations.")
        print("\nTo analyze actual images, use:")
        print("  - The API at http://localhost:5050/sophia/interpret-drawing")
        print("  - Or import the modules directly in your Python code")
        print("\nSee DRAWING_INTERPRETATION_GUIDE.md for full documentation.")

    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
