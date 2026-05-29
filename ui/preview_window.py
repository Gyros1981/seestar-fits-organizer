"""
FITS Image Preview Window Module

Provides a popup window for previewing FITS images with auto-stretch.
Supports stacking multiple images with basic alignment for dithered sequences.
"""

import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
import logging
import threading
import numpy as np
from astropy.io import fits
from PIL import Image, ImageTk

logger = logging.getLogger(__name__)

# Try to import OpenCV for alignment, fallback to numpy if not available
try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False
    logger.warning("OpenCV not available, using basic numpy alignment")


class PreviewWindow(ctk.CTkToplevel):
    """Window for previewing FITS images with optional stacking."""
    
    def __init__(self, parent, image_path: Path, stack_paths: list = None):
        """
        Initialize preview window.
        
        Args:
            parent: Parent window
            image_path: Primary image to display (or first in stack)
            stack_paths: Optional list of additional paths to stack
        """
        super().__init__(parent)
        self.parent = parent
        self.image_path = image_path
        self.stack_paths = stack_paths or []
        self.is_stacking = len(self.stack_paths) > 0
        
        title = f"Stack Preview ({len(self.stack_paths) + 1} images)" if self.is_stacking else f"Preview - {image_path.name}"
        self.title(title)
        self.geometry("800x600")
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        self.setup_ui()
        
        # Load image in background thread
        if self.is_stacking:
            self.loading_label.configure(text=f"Loading and stacking {len(self.stack_paths) + 1} images...")
            thread = threading.Thread(target=self.load_and_stack)
        else:
            self.loading_label.configure(text="Loading image...")
            thread = threading.Thread(target=self.load_single)
        thread.daemon = True
        thread.start()
    
    def setup_ui(self):
        """Setup the preview window UI."""
        # Main container
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title label
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Loading...",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.pack(pady=(0, 10))
        
        # Progress bar for stacking
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(0, 10))
        self.progress_bar.pack_forget()  # Hidden initially
        
        # Loading label
        self.loading_label = ctk.CTkLabel(self.main_frame, text="Loading...", font=ctk.CTkFont(size=14))
        self.loading_label.pack(pady=50)
        
        # Image container
        self.image_frame = ctk.CTkFrame(self.main_frame, fg_color="black")
        self.image_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.image_frame.pack_forget()  # Hidden initially
        
        # Image label
        self.image_label = ctk.CTkLabel(self.image_frame, text="")
        self.image_label.pack(expand=True)
        
        # Info frame
        self.info_frame = ctk.CTkFrame(self.main_frame)
        self.info_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.info_frame.pack_forget()  # Hidden initially
        
        self.info_label = ctk.CTkLabel(
            self.info_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.info_label.pack(pady=5)
        
        # Close button
        self.close_button = ctk.CTkButton(
            self.main_frame,
            text="Close",
            command=self.destroy,
            height=35
        )
        self.close_button.pack(pady=(0, 10))
    
    def update_progress(self, message: str, value: float):
        """Update loading progress."""
        self.after(0, lambda: self.loading_label.configure(text=message))
        self.after(0, lambda: self.progress_bar.set(value))
    
    def load_single(self):
        """Load and display a single FITS image."""
        try:
            self.update_progress("Loading FITS file...", 0.5)
            
            # Load FITS data
            with fits.open(self.image_path) as hdul:
                data = hdul[0].data
                header = hdul[0].header
                
                if data is None:
                    self.after(0, lambda: self.show_error("No image data found"))
                    return
                
                height, width, is_color = self._get_dimensions(data)
                
                self.update_progress("Applying auto-stretch...", 0.8)
                stretched = self.auto_stretch(data)
                
                self.update_progress("Creating preview...", 0.9)
                ctk_image = self._create_ctk_image(stretched)
                
                bitpix = header.get('BITPIX', 'Unknown')
                
                self.after(0, lambda: self._show_result(ctk_image, width, height, bitpix, 1))
                
        except Exception as e:
            logger.error(f"Failed to load preview: {e}")
            error_msg = str(e)
            self.after(0, lambda msg=error_msg: self.show_error(msg))
    
    def load_and_stack(self):
        """Load multiple FITS images, align and stack them."""
        try:
            all_paths = [self.image_path] + self.stack_paths
            total = len(all_paths)
            
            self.after(0, self.progress_bar.pack)
            
            # Load all images
            images = []
            for i, path in enumerate(all_paths):
                progress = (i + 1) / (total + 3)  # Reserve space for align and stack
                self.update_progress(f"Loading image {i+1} of {total}...", progress)
                
                try:
                    with fits.open(path) as hdul:
                        data = hdul[0].data
                        if data is not None:
                            # Normalize to float32 for processing
                            data = data.astype(np.float32)
                            images.append(data)
                except Exception as e:
                    logger.warning(f"Failed to load {path}: {e}")
                    continue
            
            if not images:
                self.after(0, lambda: self.show_error("No valid images to stack"))
                return
            
            # Store image count for later use
            num_images = len(images)
            
            if len(images) == 1:
                # Fallback to single image
                self.update_progress("Only one image loaded, displaying...", 0.9)
                height, width, is_color = self._get_dimensions(images[0])
                stretched = self.auto_stretch(images[0])
                ctk_image = self._create_ctk_image(stretched)
                self.after(0, lambda: self._show_result(ctk_image, width, height, 16, 1))
                return
            
            # Align images to first
            self.update_progress("Aligning images...", (total + 1) / (total + 3))
            aligned = self._align_images(images)
            
            # Stack (median for outlier rejection)
            self.update_progress("Stacking images (median)...", (total + 2) / (total + 3))
            stacked = np.median(aligned, axis=0)
            
            # Create preview
            self.update_progress("Creating preview...", 0.95)
            height, width, is_color = self._get_dimensions(stacked)
            stretched = self.auto_stretch(stacked)
            ctk_image = self._create_ctk_image(stretched)
            
            self.after(0, lambda img=ctk_image, w=width, h=height, n=num_images: self._show_result(img, w, h, 32, n))
            
        except Exception as e:
            logger.error(f"Failed to stack preview: {e}")
            error_msg = str(e)
            self.after(0, lambda msg=error_msg: self.show_error(msg))
    
    def _get_dimensions(self, data: np.ndarray) -> tuple:
        """Get dimensions and color info from numpy array."""
        if len(data.shape) == 3:
            if data.shape[0] == 3:
                # CHW format
                data = np.transpose(data, (1, 2, 0))
            height, width = data.shape[:2]
            is_color = True
        else:
            height, width = data.shape
            is_color = False
        return height, width, is_color
    
    def _create_ctk_image(self, data: np.ndarray):
        """Create CTkImage from numpy array."""
        is_color = len(data.shape) == 3 and data.shape[2] == 3
        
        if is_color:
            image = Image.fromarray((data * 255).astype(np.uint8), mode='RGB')
        else:
            image = Image.fromarray((data * 255).astype(np.uint8), mode='L')
        
        # Resize to fit window
        max_size = (750, 450)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        return ctk.CTkImage(light_image=image, dark_image=image, size=image.size)
    
    def _align_images(self, images: list) -> np.ndarray:
        """Align images using star pattern matching."""
        if len(images) < 2:
            return np.array(images)
        
        reference = images[0]
        aligned = [reference]  # First image is reference
        
        # For color images, convert to grayscale for alignment
        ref_gray = self._to_grayscale(reference)
        
        # Detect stars in reference image
        ref_stars = self._detect_stars(ref_gray, max_stars=10)
        
        if len(ref_stars) < 3:
            logger.warning("Not enough stars detected for alignment, using simple shift")
            # Fallback to simple center-of-mass alignment
            ref_com = self._center_of_mass(ref_gray)
            for img in images[1:]:
                img_gray = self._to_grayscale(img)
                img_com = self._center_of_mass(img_gray)
                shift = (ref_com[0] - img_com[0], ref_com[1] - img_com[1])
                aligned_img = self._shift_image(img, shift)
                aligned.append(aligned_img)
            return np.array(aligned)
        
        # Align each image to reference using star matching
        for img in images[1:]:
            img_gray = self._to_grayscale(img)
            
            # Detect stars in this image
            img_stars = self._detect_stars(img_gray, max_stars=10)
            
            if len(img_stars) < 3:
                logger.warning(f"Only {len(img_stars)} stars found, using simple shift")
                img_com = self._center_of_mass(img_gray)
                ref_com = self._center_of_mass(ref_gray)
                shift = (ref_com[0] - img_com[0], ref_com[1] - img_com[1])
                aligned_img = self._shift_image(img, shift)
                aligned.append(aligned_img)
                continue
            
            # Find matching stars and calculate transform
            transform = self._find_star_transform(ref_stars, img_stars)
            aligned_img = self._apply_transform(img, transform, reference.shape)
            aligned.append(aligned_img)
        
        return np.array(aligned)
    
    def _to_grayscale(self, img: np.ndarray) -> np.ndarray:
        """Convert image to grayscale for alignment."""
        if len(img.shape) == 3:
            return np.mean(img, axis=2)
        return img
    
    def _detect_stars(self, img: np.ndarray, max_stars: int = 10) -> list:
        """Detect bright stars in image using local maxima."""
        # Apply mild Gaussian blur to reduce noise
        if HAS_OPENCV:
            blurred = cv2.GaussianBlur(img.astype(np.float32), (5, 5), 1.0)
        else:
            blurred = img.astype(np.float32)
        
        # Find local maxima
        try:
            from scipy.ndimage import maximum_filter, generate_binary_structure
            # Create a footprint for local maxima detection
            footprint = generate_binary_structure(2, 2)
            local_max = maximum_filter(blurred, footprint=footprint, mode='constant', cval=0)
            # Points that are equal to local max are peaks
            peaks = (blurred == local_max) & (blurred > np.percentile(blurred, 95))
        except ImportError:
            # Fallback: simple threshold-based detection
            threshold = np.percentile(blurred, 98)
            peaks = blurred > threshold
        
        # Get coordinates of peaks
        y_coords, x_coords = np.where(peaks)
        peak_values = blurred[y_coords, x_coords]
        
        # Sort by brightness and take top max_stars
        sorted_indices = np.argsort(peak_values)[::-1]
        top_indices = sorted_indices[:max_stars]
        
        stars = [(x_coords[i], y_coords[i], peak_values[i]) for i in top_indices]
        
        return stars
    
    def _find_star_transform(self, ref_stars: list, img_stars: list) -> tuple:
        """Find best translation transform by matching star patterns."""
        # Simple approach: find shift that aligns most stars
        # Try matching the brightest star in reference to each star in image
        
        best_shift = (0, 0)
        best_matches = 0
        
        # Use top 3 brightest stars from reference
        ref_bright = ref_stars[:3]
        
        for ref_star in ref_bright:
            for img_star in img_stars[:5]:  # Try top 5 stars in target
                # Calculate shift needed to align these stars
                shift_x = ref_star[0] - img_star[0]
                shift_y = ref_star[1] - img_star[1]
                
                # Count how many other stars align with this shift
                matches = 0
                for rs in ref_stars:
                    expected_x = rs[0] - shift_x
                    expected_y = rs[1] - shift_y
                    
                    # Check if any image star is close to expected position
                    for is_star in img_stars:
                        dist = np.sqrt((expected_x - is_star[0])**2 + (expected_y - is_star[1])**2)
                        if dist < 3:  # Within 3 pixels
                            matches += 1
                            break
                
                if matches > best_matches:
                    best_matches = matches
                    best_shift = (shift_x, shift_y)
        
        return best_shift
    
    def _apply_transform(self, img: np.ndarray, shift: tuple, output_shape: tuple) -> np.ndarray:
        """Apply translation transform to image."""
        shift_x, shift_y = shift
        
        if HAS_OPENCV:
            # Use OpenCV for high-quality warping
            M = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
            shifted = cv2.warpAffine(
                np.float32(img), 
                M, 
                (output_shape[1], output_shape[0]),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=0
            )
            return shifted
        else:
            # Simple numpy roll for integer shifts
            shifted = np.roll(img, int(round(shift_y)), axis=0)
            shifted = np.roll(shifted, int(round(shift_x)), axis=1)
            return shifted
    
    def _center_of_mass(self, img: np.ndarray) -> tuple:
        """Calculate center of mass of image."""
        # Threshold to avoid noise
        threshold = np.percentile(img, 90)
        mask = img > threshold
        
        if not np.any(mask):
            return (img.shape[1] / 2, img.shape[0] / 2)
        
        y_indices, x_indices = np.indices(img.shape)
        
        total = np.sum(img[mask])
        if total == 0:
            return (img.shape[1] / 2, img.shape[0] / 2)
        
        com_x = np.sum(x_indices[mask] * img[mask]) / total
        com_y = np.sum(y_indices[mask] * img[mask]) / total
        
        return (com_x, com_y)
    
    def _shift_image(self, img: np.ndarray, shift: tuple) -> np.ndarray:
        """Simple shift for fallback alignment."""
        return self._apply_transform(img, shift, img.shape)
    
    def auto_stretch(self, data: np.ndarray) -> np.ndarray:
        """Apply auto-stretch to FITS data for visibility."""
        # Handle different data types
        if data.dtype == np.uint16:
            # 16-bit data
            data = data.astype(np.float32) / 65535.0
        elif data.dtype == np.uint8:
            # 8-bit data
            data = data.astype(np.float32) / 255.0
        else:
            # Already float or other - normalize
            data = data.astype(np.float32)
        
        # For RGB, process each channel
        if len(data.shape) == 3 and data.shape[2] == 3:
            result = np.zeros_like(data)
            for i in range(3):
                result[:, :, i] = self._stretch_channel(data[:, :, i])
            return result
        else:
            return self._stretch_channel(data)
    
    def _stretch_channel(self, channel: np.ndarray) -> np.ndarray:
        """Apply percentile stretch to a single channel."""
        # Clip extreme values
        low, high = np.percentile(channel[channel > 0], [1, 99]) if np.any(channel > 0) else (0, 1)
        
        if high > low:
            stretched = (channel - low) / (high - low)
        else:
            stretched = channel
        
        # Clip to 0-1 range
        return np.clip(stretched, 0, 1)
    
    def _show_result(self, image, width: int, height: int, bitpix: int, num_images: int):
        """Display the final result."""
        self.loading_label.pack_forget()
        self.progress_bar.pack_forget()
        
        self.title_label.configure(text=f"Preview: {self.image_path.name}")
        self.image_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.image_label.configure(image=image)
        self.image_label.image = image  # Keep reference
        
        self.info_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Update info
        bit_depth = {
            8: '8-bit',
            16: '16-bit',
            32: '32-bit',
            -32: '32-bit float',
            -64: '64-bit float'
        }.get(bitpix, f'BITPIX={bitpix}')
        
        if num_images > 1:
            info_text = f"Dimensions: {width} x {height} | Bit depth: {bit_depth} | Stacked: {num_images} images"
        else:
            info_text = f"Dimensions: {width} x {height} | Bit depth: {bit_depth}"
        
        self.info_label.configure(text=info_text)
    
    def show_error(self, message: str):
        """Show error message."""
        self.loading_label.pack_forget()
        self.progress_bar.pack_forget()
        self.title_label.configure(text="Error")
        error_label = ctk.CTkLabel(
            self.main_frame,
            text=f"Error loading image:\n{message}",
            font=ctk.CTkFont(size=12),
            text_color="red"
        )
        error_label.pack(pady=50)
        messagebox.showerror("Preview Error", f"Failed to load image preview: {message}")
