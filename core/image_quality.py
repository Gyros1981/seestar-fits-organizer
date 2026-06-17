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
    raw_streak_ratio: float = 0.0  # Raw measurement for threshold re-application


class ImageQualityAnalyzer:
    """Analyzes FITS images for quality issues."""
    
    def __init__(self, 
                 streak_sensitivity: float = 1.0,
                 min_streak_length: int = 50,
                 fwhm_threshold: float = 5.0,
                 eccentricity_threshold: float = 0.5,
                 gradient_threshold: float = 0.3):
        """
        Initialize analyzer with detection thresholds.
        
        Args:
            streak_sensitivity: Sensitivity for streak detection (0.1-2.0, lower = less sensitive/more strict)
            min_streak_length: Minimum pixel length to consider as streak
            fwhm_threshold: Maximum FWHM in pixels for 'good' stars
            eccentricity_threshold: Max eccentricity for round stars (0.0 = perfect circle, 1.0 = line)
            gradient_threshold: Max background gradient for even illumination
        """
        self.streak_sensitivity = streak_sensitivity
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
    
    def analyze_image(self, image_data: np.ndarray, file_path: Optional[Path] = None, fast_mode: bool = True) -> QualityReport:
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
        
        # Ensure 2D grayscale and downsample if too large (for speed)
        if len(image_data.shape) == 3:
            image_data = np.mean(image_data, axis=2)
        
        # Downsample large images for faster analysis
        max_size = 1024 if fast_mode else 2048
        h, w = image_data.shape
        if fast_mode and (h > max_size or w > max_size):
            from scipy.ndimage import zoom
            zoom_factor = max_size / max(h, w)
            new_h, new_w = int(h * zoom_factor), int(w * zoom_factor)
            image_data = zoom(image_data, (new_h/h, new_w/w), order=1)
            logger.debug(f"Downsampled image to {image_data.shape} for speed")
        
        issues = []
        
        # Detect streaks (use fast method if available)
        if SKIMAGE_AVAILABLE and not fast_mode:
            has_streaks, streak_count, streak_conf, raw_ratio = self._detect_streaks(image_data)
        else:
            # Use simple fast detection for speed
            has_streaks, streak_count, streak_conf, raw_ratio = self._detect_streaks_simple(image_data)
        
        if has_streaks:
            issues.append(f"{streak_count} streak(s) detected")
        
        # Analyze star quality (use fast method in fast_mode)
        if PHOTUTILS_AVAILABLE and not fast_mode:
            star_quality, avg_fwhm, avg_ecc = self._analyze_star_shapes(image_data)
        else:
            # Use simple fast analysis
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
            analysis_time_ms=analysis_time,
            raw_streak_ratio=raw_ratio
        )
    
    def _detect_streaks(self, image: np.ndarray) -> Tuple[bool, int, float, float]:
        """
        Detect straight line streaks using Hough Transform.
        
        Returns:
            (has_streaks, streak_count, confidence, raw_streak_ratio)
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
        
        # Calculate raw ratio from edge density (for re-thresholding)
        edge_ratio = np.sum(edges) / edges.size
        
        if len(peaks[0]) == 0:
            return False, 0, 0.0, edge_ratio
        
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
        
        # Use max of edge_ratio and a small value based on valid_streaks
        raw_ratio = max(edge_ratio, valid_streaks * 0.0001)
        
        return has_streaks, valid_streaks, confidence, raw_ratio
    
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
    
    def _detect_streaks_simple(self, image: np.ndarray) -> Tuple[bool, int, float, float]:
        """Improved streak detection using gradient analysis.
        
        Returns: (has_streaks, streak_count, confidence, raw_streak_ratio)
        """
        from scipy.ndimage import gaussian_filter
        
        # Smooth slightly to reduce noise
        img_smooth = gaussian_filter(image.astype(np.float64), sigma=1)
        
        # Calculate gradients
        grad_x = np.abs(np.diff(img_smooth, axis=1, prepend=img_smooth[:, 0:1]))
        grad_y = np.abs(np.diff(img_smooth, axis=0, prepend=img_smooth[0:1, :]))
        
        # Strong gradient threshold - use percentage of max to catch spread-out high gradients
        grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Use 35% of max gradient as threshold
        # This catches streaks which create many moderately-high gradient pixels
        # while stars create fewer but higher peak gradients
        max_grad = np.max(grad_magnitude)
        strong_threshold = max_grad * 0.35
        
        # Count strong gradient pixels
        strong_pixels = np.sum(grad_magnitude > strong_threshold)
        
        # Normalize by image size
        h, w = image.shape
        total_pixels = h * w
        strong_ratio = strong_pixels / total_pixels
        
        # Detect streaks: high gradient pixels suggest linear features
        # From measurements at 35%: bad ~0.008-0.012%, good ~0.005-0.006%
        # Base threshold at 0.006% (0.00006), adjusted by sensitivity
        # sensitivity < 1 = stricter (higher threshold), > 1 = more lenient
        base_threshold = 0.00006
        adjusted_threshold = base_threshold / self.streak_sensitivity
        has_streaks = strong_ratio > adjusted_threshold
        streak_count = max(1, int(strong_ratio * 10000))  # Scale to approximate streak count
        confidence = min(1.0, strong_ratio * 1000)  # Scale confidence
        
        logger.debug(f"Streak detection: strong_pixels={strong_pixels}, ratio={strong_ratio:.4f}, "
                     f"has_streaks={has_streaks}, confidence={confidence:.2f}")
        
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
        
        # Debug: print available columns
        logger.debug(f"DAOStarFinder columns: {list(sources.colnames)}")
        
        # Handle different column naming in photutils versions
        x_col = 'xcentroid' if 'xcentroid' in sources.colnames else 'x_centroid' if 'x_centroid' in sources.colnames else 'x'
        y_col = 'ycentroid' if 'ycentroid' in sources.colnames else 'y_centroid' if 'y_centroid' in sources.colnames else 'y'
        
        for source in sources:
            # Get star properties
            x = source[x_col]
            y = source[y_col]
            
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
        """Fast star analysis without photutils using gradient statistics."""
        from scipy.ndimage import gaussian_filter, sobel
        
        # Normalize image
        img_float = image.astype(np.float64)
        
        # Subtract background (simple median filter)
        background = gaussian_filter(img_float, sigma=20)
        img_sub = img_float - background
        img_sub = np.clip(img_sub, 0, None)
        
        # Detect edges using Sobel
        sobel_x = sobel(img_sub, axis=1)
        sobel_y = sobel(img_sub, axis=0)
        gradient_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        
        # Threshold to find bright regions (stars)
        threshold = np.percentile(img_sub, 90)  # Top 10%
        bright_mask = img_sub > threshold
        
        # Remove small noise
        from scipy.ndimage import binary_opening
        bright_mask = binary_opening(bright_mask, iterations=1)
        
        # Label connected components
        from scipy.ndimage import label
        labeled, num_features = label(bright_mask)
        
        if num_features == 0:
            return 'unknown', 0.0, 0.0
        
        # Analyze star shapes
        fwhm_values = []
        eccentricities = []
        
        for i in range(1, min(num_features + 1, 51)):
            mask = labeled == i
            
            # Get region properties
            coords = np.where(mask)
            if len(coords[0]) < 3 or len(coords[0]) > 500:  # Filter size
                continue
            
            # Calculate centroid
            y_coords, x_coords = coords
            x_center = np.mean(x_coords)
            y_center = np.mean(y_coords)
            
            # Calculate moments
            x_diff = x_coords - x_center
            y_diff = y_coords - y_center
            
            mu_20 = np.mean(x_diff**2)
            mu_02 = np.mean(y_diff**2)
            mu_11 = np.mean(x_diff * y_diff)
            
            # Eccentricity
            if mu_20 + mu_02 > 0:
                ecc = np.sqrt((mu_20 - mu_02)**2 + 4*mu_11**2) / (mu_20 + mu_02)
            else:
                ecc = 0.0
            
            # Estimate FWHM from region size
            area = len(coords[0])
            fwhm = 2 * np.sqrt(area / np.pi)
            
            if 2 < fwhm < 50:  # Reasonable star size
                fwhm_values.append(fwhm)
                eccentricities.append(ecc)
        
        if not eccentricities:
            return 'unknown', 0.0, 0.0
        
        avg_fwhm = np.median(fwhm_values)
        avg_ecc = np.median(eccentricities)
        
        # Determine quality
        if avg_fwhm > self.fwhm_threshold * 1.5 or avg_ecc > self.eccentricity_threshold * 1.5:
            quality = 'poor'
        elif avg_fwhm > self.fwhm_threshold or avg_ecc > self.eccentricity_threshold:
            quality = 'fair'
        else:
            quality = 'good'
        
        return quality, avg_fwhm, avg_ecc
    
    def reapply_threshold(self, report: QualityReport) -> QualityReport:
        """
        Re-apply streak detection threshold to an existing report.
        Uses cached raw_streak_ratio to determine has_streaks without re-analyzing image.
        
        Args:
            report: Existing QualityReport with raw_streak_ratio
            
        Returns:
            Updated QualityReport with new threshold applied
        """
        if report.raw_streak_ratio == 0.0:
            # No cached ratio, can't re-apply
            return report
        
        # Calculate adjusted threshold based on sensitivity
        base_threshold = 0.00006
        adjusted_threshold = base_threshold / self.streak_sensitivity
        
        # Re-evaluate streak detection
        raw_ratio = report.raw_streak_ratio
        has_streaks = raw_ratio > adjusted_threshold
        streak_count = max(1, int(raw_ratio * 10000)) if has_streaks else 0
        confidence = min(1.0, raw_ratio * 1000) if has_streaks else 0.0
        
        # Rebuild issues list
        issues = []
        if has_streaks:
            issues.append(f"{streak_count} streak(s) detected")
        if report.star_quality == 'poor':
            issues.append("Poor star quality (trailing/stretched)")
        elif report.star_quality == 'fair':
            issues.append("Fair star quality")
        if report.background_gradient > self.gradient_threshold:
            issues.append("Uneven background illumination")
        
        # Re-evaluate problematic status
        is_problematic = has_streaks or report.star_quality == 'poor'
        
        # Return updated report
        return QualityReport(
            file_path=report.file_path,
            has_streaks=has_streaks,
            streak_count=streak_count,
            streak_confidence=confidence,
            star_quality=report.star_quality,
            avg_fwhm=report.avg_fwhm,
            avg_eccentricity=report.avg_eccentricity,
            background_gradient=report.background_gradient,
            issues=issues,
            is_problematic=is_problematic,
            analysis_time_ms=report.analysis_time_ms,
            raw_streak_ratio=report.raw_streak_ratio
        )
    
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
