"""
Image Processing Layer
Part of the LIVING System - Symphony Living System

This module handles image loading, preprocessing, and feature extraction
for drawing analysis.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import base64
import io


class ImageProcessor:
    """
    Handles image preprocessing and feature extraction
    Supports multiple input formats and prepares data for geometric analysis
    """

    def __init__(self):
        self.supported_formats = ['png', 'jpg', 'jpeg', 'gif', 'bmp']

    def load_from_path(self, image_path: str) -> Dict:
        """
        Load image from file path

        Args:
            image_path: Path to image file

        Returns:
            Dictionary containing image data and metadata
        """
        try:
            # Import PIL/Pillow only when needed
            from PIL import Image

            img = Image.open(image_path)
            return self._process_pil_image(img)

        except ImportError:
            return {"error": "PIL/Pillow not installed. Install with: pip install Pillow"}
        except Exception as e:
            return {"error": f"Failed to load image: {str(e)}"}

    def load_from_base64(self, base64_string: str) -> Dict:
        """
        Load image from base64 encoded string

        Args:
            base64_string: Base64 encoded image data

        Returns:
            Dictionary containing image data and metadata
        """
        try:
            from PIL import Image

            # Remove data URL prefix if present
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]

            # Decode and load
            image_data = base64.b64decode(base64_string)
            img = Image.open(io.BytesIO(image_data))

            return self._process_pil_image(img)

        except ImportError:
            return {"error": "PIL/Pillow not installed. Install with: pip install Pillow"}
        except Exception as e:
            return {"error": f"Failed to decode base64 image: {str(e)}"}

    def _process_pil_image(self, img) -> Dict:
        """
        Process PIL Image object and extract features

        Args:
            img: PIL Image object

        Returns:
            Dictionary with image data and extracted features
        """
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Convert to numpy array
        img_array = np.array(img)

        # Extract basic metadata
        width, height = img.size

        result = {
            "width": width,
            "height": height,
            "mode": img.mode,
            "array": img_array,
            "features": {}
        }

        # Extract features
        result["features"] = self.extract_features(img_array)

        return result

    def extract_features(self, img_array: np.ndarray) -> Dict:
        """
        Extract geometric features from image array

        Args:
            img_array: Numpy array representation of image

        Returns:
            Dictionary of extracted features (circles, lines, vertices, etc.)
        """
        features = {
            "circles": [],
            "lines": [],
            "vertices": [],
            "spiral": None,
            "symmetry": None
        }

        try:
            import cv2

            # Convert to grayscale
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array

            # Edge detection
            edges = cv2.Canny(gray, 50, 150)

            # Detect circles using Hough Circle Transform
            circles = cv2.HoughCircles(
                gray,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=20,
                param1=50,
                param2=30,
                minRadius=10,
                maxRadius=500
            )

            if circles is not None:
                circles = np.uint16(np.around(circles))
                for circle in circles[0, :]:
                    features["circles"].append({
                        "center": [int(circle[0]), int(circle[1])],
                        "radius": int(circle[2]),
                        "nested": False  # Will be determined by overlap analysis
                    })

                # Check for nested circles
                features["circles"] = self._analyze_circle_nesting(features["circles"])

            # Detect lines using Hough Line Transform
            lines = cv2.HoughLinesP(
                edges,
                rho=1,
                theta=np.pi/180,
                threshold=50,
                minLineLength=30,
                maxLineGap=10
            )

            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    features["lines"].append({
                        "start": [int(x1), int(y1)],
                        "end": [int(x2), int(y2)],
                        "length": float(np.sqrt((x2-x1)**2 + (y2-y1)**2)),
                        "angle": float(np.arctan2(y2-y1, x2-x1))
                    })

            # Detect corners/vertices using Harris Corner Detection
            corners = cv2.cornerHarris(gray, blockSize=2, ksize=3, k=0.04)
            corners = cv2.dilate(corners, None)

            # Threshold for corner detection
            threshold = 0.01 * corners.max()
            corner_coords = np.where(corners > threshold)

            for y, x in zip(*corner_coords):
                features["vertices"].append({
                    "x": int(x),
                    "y": int(y),
                    "strength": float(corners[y, x])
                })

            # Analyze spiral patterns (simplified detection)
            spiral_data = self._detect_spiral_pattern(features["circles"], features["lines"])
            if spiral_data:
                features["spiral"] = spiral_data

            # Analyze symmetry
            features["symmetry"] = self._analyze_symmetry(gray)

        except ImportError:
            features["error"] = "OpenCV not installed. Install with: pip install opencv-python"
        except Exception as e:
            features["error"] = f"Feature extraction failed: {str(e)}"

        return features

    def _analyze_circle_nesting(self, circles: List[Dict]) -> List[Dict]:
        """
        Determine which circles are nested within others
        """
        for i, circle_i in enumerate(circles):
            for j, circle_j in enumerate(circles):
                if i != j:
                    # Calculate distance between centers
                    c1 = np.array(circle_i["center"])
                    c2 = np.array(circle_j["center"])
                    distance = np.linalg.norm(c1 - c2)

                    # Check if one circle is inside the other
                    r1 = circle_i["radius"]
                    r2 = circle_j["radius"]

                    if distance + min(r1, r2) < max(r1, r2):
                        if r1 < r2:
                            circles[i]["nested"] = True
                        else:
                            circles[j]["nested"] = True

        return circles

    def _detect_spiral_pattern(self, circles: List[Dict], lines: List[Dict]) -> Optional[Dict]:
        """
        Attempt to detect spiral patterns from circles and lines
        """
        if len(circles) < 3:
            return None

        # Sort circles by radius
        sorted_circles = sorted(circles, key=lambda c: c["radius"])

        # Calculate ratio between consecutive circles
        ratios = []
        for i in range(len(sorted_circles) - 1):
            r1 = sorted_circles[i]["radius"]
            r2 = sorted_circles[i + 1]["radius"]
            if r1 > 0:
                ratios.append(r2 / r1)

        if ratios:
            avg_ratio = np.mean(ratios)

            # Check if close to golden ratio (1.618) or other significant ratios
            golden_ratio = 1.618033988749895

            if 1.5 < avg_ratio < 1.8:
                return {
                    "ratio": float(avg_ratio),
                    "turns": len(sorted_circles),
                    "direction": "unknown",  # Would need more analysis
                    "golden_ratio_match": abs(avg_ratio - golden_ratio) < 0.1
                }

        return None

    def _analyze_symmetry(self, gray_image: np.ndarray) -> Dict:
        """
        Analyze image for symmetry (vertical, horizontal, radial)
        """
        height, width = gray_image.shape

        # Vertical symmetry
        left_half = gray_image[:, :width//2]
        right_half = gray_image[:, width//2:]
        right_half_flipped = np.fliplr(right_half)

        # Handle unequal sizes
        min_width = min(left_half.shape[1], right_half_flipped.shape[1])
        left_half = left_half[:, :min_width]
        right_half_flipped = right_half_flipped[:, :min_width]

        vertical_diff = np.mean(np.abs(left_half.astype(float) - right_half_flipped.astype(float)))
        vertical_symmetry = 1.0 - (vertical_diff / 255.0)

        # Horizontal symmetry
        top_half = gray_image[:height//2, :]
        bottom_half = gray_image[height//2:, :]
        bottom_half_flipped = np.flipud(bottom_half)

        min_height = min(top_half.shape[0], bottom_half_flipped.shape[0])
        top_half = top_half[:min_height, :]
        bottom_half_flipped = bottom_half_flipped[:min_height, :]

        horizontal_diff = np.mean(np.abs(top_half.astype(float) - bottom_half_flipped.astype(float)))
        horizontal_symmetry = 1.0 - (horizontal_diff / 255.0)

        return {
            "vertical": float(vertical_symmetry),
            "horizontal": float(horizontal_symmetry),
            "radial": None  # Would require more complex analysis
        }


class ResonanceMapper:
    """
    Maps visual features to resonance frequencies and energy patterns
    """

    def __init__(self):
        self.color_frequency_map = {
            "red": 480,      # Root chakra region
            "orange": 510,   # Sacral
            "yellow": 540,   # Solar plexus
            "green": 528,    # Heart (also solfeggio)
            "blue": 600,     # Throat
            "indigo": 660,   # Third eye
            "violet": 720    # Crown
        }

    def map_colors_to_frequencies(self, img_array: np.ndarray) -> Dict:
        """
        Analyze dominant colors and map to resonance frequencies
        """
        try:
            # Calculate average color values
            avg_color = np.mean(img_array, axis=(0, 1))
            r, g, b = avg_color

            # Determine dominant color
            dominant = self._classify_color(r, g, b)

            return {
                "dominant_color": dominant,
                "resonance_frequency": self.color_frequency_map.get(dominant, 528),
                "rgb": [int(r), int(g), int(b)]
            }

        except Exception as e:
            return {"error": str(e)}

    def _classify_color(self, r: float, g: float, b: float) -> str:
        """
        Simple color classification
        """
        colors = {
            "red": (r > g and r > b),
            "green": (g > r and g > b),
            "blue": (b > r and b > g),
            "yellow": (r > 200 and g > 200 and b < 100),
            "orange": (r > 200 and g > 100 and g < 200 and b < 100),
            "violet": (r > 100 and b > 200),
            "indigo": (b > 150 and r > 50 and r < 150)
        }

        for color, condition in colors.items():
            if condition:
                return color

        # Default to green (heart chakra) if unclear
        return "green"


def create_processor():
    """Factory function to create image processor instance"""
    return ImageProcessor()


def create_resonance_mapper():
    """Factory function to create resonance mapper instance"""
    return ResonanceMapper()


# Example usage
if __name__ == "__main__":
    processor = create_processor()

    # Test with a sample image path (if available)
    # result = processor.load_from_path("sample_drawing.png")
    # print(result["features"])

    print("Image processor initialized and ready.")
    print("Supported formats:", processor.supported_formats)
