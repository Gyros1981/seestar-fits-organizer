"""
Image Quality Analysis Module

Provides automated detection of problematic astrophotography images:
- Satellite/airplane streaks (using Hough Line Transform)
- Stretched/trailing stars (using star detection and shape analysis)
- Background gradients and uneven illumination
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import scikit-image, provide fallback if not available
try:
    from skimage.transform import hough_line, hough_line_peaks
    from skimage.feature import canny
    from skimage.filters import sobel, threshold_otsu
    from skimage.morphology import remove_small_objects
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False
    logger.warning("scikit-image not available. Image quality analysis will be limited.")

try:
    from photutils.detection import DAOStarFinder
    from photutils.aperture import CircularAperture, aperture_photometry
    PHOTUTILS_AVAILABLE = True
except ImportError:
    PHOTUTILS_AVAILABLE = False
    logger.warning("photutils not available. Star quality analysis will be limited.")


@dataclass
class QualityReport:
    """Quality analysis report for a single image."""
    file_path: Path
    has_streaks: bool
    streak_count: int
    streak_confidence: float  # 0.0 to 1.0
    star_quality: str  # 'good', 'fair', 'poor'
    avg_fwhm: float
    avg_eccentricity: float
    background_gradient: float  # 0.0 to 1.0
    issues: List[str]
    is_problematic: bool
    analysis_time_ms: float


class ImageQualityAnalyzer:
    """Analyzes FITS images for quality issues."""
    
    def __init__(self, 
                 streak_threshold: float = 0.3,
                 min_streak_length: int = 50,
                 fwhm_threshold: float = 5.0,
                 eccentricity_threshold: float = 0.5,
                 gradient_threshold: float = 0.3):
        """
        Initialize analyzer with detection thresholds.
        
        Args:
            streak_threshold: Sensitivity for streak detection (0.0-1.0, lower = more sensitive)
            min_streak_length: Minimum pixel length to consider as streak
            fwhm_threshold: Maximum FWHM in pixels for 'good' stars
            eccentricity_threshold: Max eccentricity for round stars (0.0 = perfect circle, 1.0 = line)
            gradient_threshold: Max background gradient for even illumination
        """
        self.streak_threshold = streak_threshold
        self.min_streak_length = min_streak_length
        self.fwhm_threshold = fwhm_threshold
        self.eccentricity_threshold = eccentricity_threshold
        self.gradient_threshold = gradient_threshold
        
        self.has_full_analysis = SKIMAGE_AVAILABLE and PHOTUTILS_AVAILABLE
        
        if not self.has_full_analysis:
            logger.warning(
                f"Full analysis unavailable. Missing: "
                f"{'scikit-image ' if not SKIMAGE_AVAILABLE else ''}"
                f"{'photutils' if not PHOTUTILS_AVAILABLE else ''}"
            )
    
    def analyze_image(self, image_data: np.ndarray, file_path: Optional[Path] = None) -> QualityReport:
        """
        Analyze a single image for quality issues.
        
        Args:
            image_data: 2D numpy array of image data
            file_path: Optional path for reporting
            
        Returns:
            QualityReport with detection results
        """
        import time
        start_time = time.time()
        
        # Ensure 2D grayscale
        if len(image_data.shape) == 3:
            image_data = np.mean(image_data, axis=2)
        
        issues = []
        
        # Detect streaks
        if SKIMAGE_AVAILABLE:
            has_streaks, streak_count, streak_conf = self._detect_streaks(image_data)
        else:
            has_streaks, streak_count, streak_conf = self._detect_streaks_simple(image_data)
        
        if has_streaks:
            issues.append(f"{streak_count} streak(s) detected")
        
        # Analyze star quality
        if PHOTUTILS_AVAILABLE and SKIMAGE_AVAILABLE:
            star_quality, avg_fwhm, avg_ecc = self._analyze_star_shapes(image_data)
        else:
            star_quality, avg_fwhm, avg_ecc = self._analyze_star_shapes_simple(image_data)
        
        if star_quality == 'poor':
            issues.append("Poor star quality (trailing/stretched)")
        elif star_quality == 'fair':
            issues.append("Fair star quality")
        
        # Background gradient
        gradient = self._detect_background_gradient(image_data)
        if gradient > self.gradient_threshold:
            issues.append("Uneven background illumination")
        
        # Determine if problematic
        is_problematic = has_streaks or star_quality == 'poor' or gradient > self.gradient_threshold
        
        analysis_time = (time.time() - start_time) * 1000
        
        return QualityReport(
            file_path=file_path or Path("unknown"),
            has_streaks=has_streaks,
            streak_count=streak_count,
            streak_confidence=streak_conf,
            star_quality=star_quality,
            avg_fwhm=avg_fwhm,
            avg_eccentricity=avg_ecc,
            background_gradient=gradient,
            issues=issues,
            is_problematic=is_problematic,
            analysis_time_ms=analysis_time
        )
    
    def _detect_streaks(self, image: np.ndarray) -> Tuple[bool, int, float]:
        """
        Detect straight line streaks using Hough Transform.
        
        Returns:
            (has_streaks, streak_count, confidence)
        """
        # Normalize image
        img_norm = (image - image.min()) / (image.max() - image.min() + 1e-8)
        
        # Edge detection
        edges = canny(img_norm, sigma=2, low_threshold=0.1, high_threshold=0.3)
        
        # Hough Line Transform
        tested_angles = np.linspace(-np.pi / 2, np.pi / 2, 180)
        h, theta, d = hough_line(edges, theta=tested_angles)
        
        # Find peaks
        peaks = hough_line_peaks(h, theta, d, min_distance=20, min_angle=10, threshold=np.max(h) * 0.3)
        
        if len(peaks[0]) == 0:
            return False, 0, 0.0
        
        # Count significant lines
        streak_count = len(peaks[0])
        confidence = min(1.0, streak_count / 5.0)  # Cap at 5 streaks = 100% confidence
        
        # Filter by checking if lines are long enough
        valid_streaks = 0
        for _, angle, dist in zip(peaks[0], peaks[1], peaks[2]):
            # Extract line and check length
            line_mask = self._extract_line_mask(edges, angle, dist)
            line_length = np.sum(line_mask)
            if line_length > self.min_streak_length:
                valid_streaks += 1
        
        has_streaks = valid_streaks > 0
        confidence = min(1.0, valid_streaks / 3.0)
        
        return has_streaks, valid_streaks, confidence
    
    def _extract_line_mask(self, edges: np.ndarray, angle: float, dist: float) -> np.ndarray:
        """Extract a mask of pixels along a Hough line."""
        h, w = edges.shape
        mask = np.zeros_like(edges, dtype=bool)
        
        # Calculate line points
        if np.abs(np.sin(angle)) > 0.1:
            # Line is not horizontal
            for x in range(w):
                y = int((dist - x * np.cos(angle)) / np.sin(angle))
                if 0 <= y < h:
                    mask[y, x] = edges[y, x]
        else:
            # Nearly horizontal line
            for y in range(h):
                x = int((dist - y * np.sin(angle)) / np.cos(angle))
                if 0 <= x < w:
                    mask[y, x] = edges[y, x]
        
        return mask
    
    def _detect_streaks_simple(self, image: np.ndarray) -> Tuple[bool, int, float]:
        """Simple streak detection without scikit-image."""
        # Look for high variance regions in specific directions
        img_norm = (image - image.min()) / (image.max() - image.min() + 1e-8)
        
        # Sobel edges
        grad_x = np.abs(np.diff(img_norm, axis=1, prepend=0))
        grad_y = np.abs(np.diff(img_norm, axis=0, prepend=0))
        
        # Check for linear structures by looking at row/column variance
        row_max = np.max(grad_x, axis=1)
        col_max = np.max(grad_y, axis=0)
        
        # Count rows/columns with strong gradients
        strong_rows = np.sum(row_max > 0.5)
        strong_cols = np.sum(col_max > 0.5)
        
        # Suspicious if many rows or columns have strong edges
        h, w = image.shape
        row_ratio = strong_rows / h
        col_ratio = strong_cols / w
        
        has_streaks = row_ratio > 0.1 or col_ratio > 0.1
        streak_count = max(int(row_ratio * 10), int(col_ratio * 10))
        confidence = max(row_ratio, col_ratio)
        
        return has_streaks, streak_count, confidence
    
    def _analyze_star_shapes(self, image: np.ndarray) -> Tuple[str, float, float]:
        """
        Analyze star shapes using DAOStarFinder and photometry.
        
        Returns:
            (quality_label, avg_fwhm, avg_eccentricity)
        """
        # Normalize and convert to float
        img_float = image.astype(np.float64)
        
        # Subtract background estimate
        from scipy.ndimage import median_filter
        background = median_filter(img_float, size=50)
        img_subtracted = img_float - background
        
        # Detect stars
        mean_val = np.median(img_subtracted)
        std_val = np.std(img_subtracted)
        threshold = mean_val + 3 * std_val
        
        daofind = DAOStarFinder(fwhm=3.0, threshold=threshold, exclude_border=True)
        sources = daofind(img_subtracted)
        
        if sources is None or len(sources) == 0:
            return 'unknown', 0.0, 0.0
        
        # Limit to brightest 50 stars for speed
        if len(sources) > 50:
            sources = sources[:50]
        
        fwhm_values = []
        eccentricities = []
        
        for source in sources:
            # Get star properties
            x = source['xcentroid']
            y = source['ycentroid']
            
            # Extract small cutout around star
            cutout_size = 15
            x1, x2 = int(max(0, x - cutout_size)), int(min(image.shape[1], x + cutout_size))
            y1, y2 = int(max(0, y - cutout_size)), int(min(image.shape[0], y + cutout_size))
            
            if x2 - x1 < 5 or y2 - y1 < 5:
                continue
            
            cutout = img_subtracted[y1:y2, x1:x2]
            
            # Calculate moments for shape analysis
            moments = self._calculate_moments(cutout)
            if moments['eccentricity'] is not None:
                eccentricities.append(moments['eccentricity'])
            
            # Estimate FWHM from Gaussian fit approximation
            fwhm = self._estimate_fwhm(cutout)
            if fwhm > 0:
                fwhm_values.append(fwhm)
        
        if not fwhm_values:
            return 'unknown', 0.0, 0.0
        
        avg_fwhm = np.median(fwhm_values)
        avg_ecc = np.median(eccentricities) if eccentricities else 0.0
        
        # Determine quality
        if avg_fwhm > self.fwhm_threshold * 1.5 or avg_ecc > self.eccentricity_threshold * 1.5:
            quality = 'poor'
        elif avg_fwhm > self.fwhm_threshold or avg_ecc > self.eccentricity_threshold:
            quality = 'fair'
        else:
            quality = 'good'
        
        return quality, avg_fwhm, avg_ecc
    
    def _calculate_moments(self, image: np.ndarray) -> Dict:
        """Calculate image moments for shape analysis."""
        h, w = image.shape
        
        # Create coordinate grids
        y, x = np.mgrid[:h, :w]
        
        # Total intensity
        total = np.sum(image)
        if total == 0:
            return {'eccentricity': None}
        
        # Centroid
        x_c = np.sum(x * image) / total
        y_c = np.sum(y * image) / total
        
        # Central moments
        mu_20 = np.sum((x - x_c)**2 * image) / total
        mu_02 = np.sum((y - y_c)**2 * image) / total
        mu_11 = np.sum((x - x_c) * (y - y_c) * image) / total
        
        # Eccentricity
        if mu_20 + mu_02 > 0:
            ecc = np.sqrt((mu_20 - mu_02)**2 + 4*mu_11**2) / (mu_20 + mu_02)
        else:
            ecc = 0.0
        
        return {'eccentricity': ecc}
    
    def _estimate_fwhm(self, cutout: np.ndarray) -> float:
        """Estimate FWHM from star cutout using simple method."""
        # Find peak
        peak_idx = np.unravel_index(np.argmax(cutout), cutout.shape)
        peak_val = cutout[peak_idx]
        
        if peak_val <= 0:
            return 0.0
        
        # Half maximum
        half_max = peak_val / 2
        
        # Count pixels above half max
        above_half = cutout > half_max
        area = np.sum(above_half)
        
        # Approximate FWHM as diameter of equivalent circle
        fwhm = 2 * np.sqrt(area / np.pi)
        
        return fwhm
    
    def _analyze_star_shapes_simple(self, image: np.ndarray) -> Tuple[str, float, float]:
        """Simple star analysis without photutils."""
        # Detect bright spots using threshold
        img_norm = (image - image.min()) / (image.max() - image.min() + 1e-8)
        
        # Simple threshold for bright objects
        threshold = np.percentile(img_norm, 95)
        bright_mask = img_norm > threshold
        
        # Label connected components
        from scipy.ndimage import label
        labeled, num_features = label(bright_mask)
        
        if num_features == 0:
            return 'unknown', 0.0, 0.0
        
        # Analyze each bright spot
        eccentricities = []
        for i in range(1, min(num_features + 1, 51)):
            mask = labeled == i
            
            # Calculate eccentricity from bounding box
            coords = np.where(mask)
            if len(coords[0]) < 5:
                continue
            
            y_range = coords[0].max() - coords[0].min()
            x_range = coords[1].max() - coords[1].min()
            
            if y_range + x_range > 0:
                # Approximate eccentricity
                major = max(y_range, x_range)
                minor = min(y_range, x_range) + 1e-6
                ecc = np.sqrt(1 - (minor/major)**2)
                eccentricities.append(ecc)
        
        if not eccentricities:
            return 'unknown', 0.0, 0.0
        
        avg_ecc = np.median(eccentricities)
        avg_fwhm = 3.0  # Placeholder
        
        if avg_ecc > self.eccentricity_threshold * 1.5:
            quality = 'poor'
        elif avg_ecc > self.eccentricity_threshold:
            quality = 'fair'
        else:
            quality = 'good'
        
        return quality, avg_fwhm, avg_ecc
    
    def _detect_background_gradient(self, image: np.ndarray) -> float:
        """Detect uneven background illumination."""
        # Divide into quadrants and compare
        h, w = image.shape
        
        # Sample at corners and center
        corner_size = min(h, w) // 10
        
        corners = [
            image[:corner_size, :corner_size].mean(),  # Top-left
            image[:corner_size, -corner_size:].mean(),  # Top-right
            image[-corner_size:, :corner_size].mean(),  # Bottom-left
            image[-corner_size:, -corner_size:].mean(),  # Bottom-right
        ]
        
        center_size = corner_size
        cy, cx = h // 2, w // 2
        center = image[cy-center_size//2:cy+center_size//2, 
                      cx-center_size//2:cx+center_size//2].mean()
        
        # Calculate relative variance
        all_samples = corners + [center]
        mean_val = np.mean(all_samples)
        
        if mean_val == 0:
            return 0.0
        
        # Coefficient of variation
        std_val = np.std(all_samples)
        cv = std_val / mean_val
        
        return min(1.0, cv * 2)  # Scale to 0-1 range


# Convenience function for simple usage
def analyze_image_quality(image_data: np.ndarray, 
                          file_path: Optional[Path] = None,
                          **kwargs) -> QualityReport:
    """
    Quick analysis of image quality.
    
    Args:
        image_data: 2D numpy array
        file_path: Optional path for reference
        **kwargs: Threshold settings passed to ImageQualityAnalyzer
        
    Returns:
        QualityReport
    """
    analyzer = ImageQualityAnalyzer(**kwargs)
    return analyzer.analyze_image(image_data, file_path)
