/**
 * Image Optimization Utilities
 * Handles lazy loading, webp format, and responsive images
 */

interface ImageOptimizationOptions {
  lazy?: boolean;
  quality?: number;
  format?: 'webp' | 'jpeg' | 'png';
  sizes?: string;
}

/**
 * Get optimized image props for lazy loading
 */
export const getOptimizedImageProps = (
  src: string,
  alt: string,
  options: ImageOptimizationOptions = {}
) => {
  const { lazy = true, quality = 85, format = 'webp' } = options;

  // Base props
  const props: Record<string, any> = {
    src,
    alt,
    decoding: 'async',
  };

  // Add lazy loading
  if (lazy) {
    props.loading = 'lazy';
  }

  // Add data attributes for quality and format
  props['data-quality'] = quality;
  props['data-format'] = format;

  return props;
};

/**
 * Check if WebP is supported
 */
export const supportsWebP = (): boolean => {
  if (typeof window === 'undefined') return false;

  const canvas = document.createElement('canvas');
  if (canvas.getContext && canvas.getContext('2d')) {
    return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
  }
  return false;
};

/**
 * Get image URL with format conversion
 */
export const getImageUrl = (src: string, preferWebP: boolean = true): string => {
  if (!preferWebP || !supportsWebP()) {
    return src;
  }

  // If source is already webp, return as is
  if (src.endsWith('.webp')) {
    return src;
  }

  // Convert extension to webp
  return src.replace(/\.(jpg|jpeg|png)$/i, '.webp');
};

/**
 * Preload critical images
 */
export const preloadImages = (urls: string[]) => {
  if (typeof window === 'undefined') return;

  urls.forEach((url) => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.as = 'image';
    link.href = url;
    document.head.appendChild(link);
  });
};

/**
 * Lazy load images with Intersection Observer
 */
export class LazyImageLoader {
  private observer: IntersectionObserver | null = null;

  constructor() {
    if (typeof window !== 'undefined' && 'IntersectionObserver' in window) {
      this.observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              const img = entry.target as HTMLImageElement;
              const src = img.getAttribute('data-src');
              if (src) {
                img.src = src;
                img.removeAttribute('data-src');
                this.observer?.unobserve(img);
              }
            }
          });
        },
        {
          rootMargin: '50px 0px', // Start loading 50px before entering viewport
          threshold: 0.01,
        }
      );
    }
  }

  observe(element: HTMLImageElement) {
    if (this.observer) {
      this.observer.observe(element);
    }
  }

  disconnect() {
    if (this.observer) {
      this.observer.disconnect();
    }
  }
}

/**
 * Generate responsive image srcset
 */
export const generateSrcSet = (
  baseSrc: string,
  widths: number[] = [320, 640, 768, 1024, 1280, 1536]
): string => {
  const extension = baseSrc.split('.').pop();
  const baseWithoutExt = baseSrc.replace(`.${extension}`, '');

  return widths
    .map((width) => `${baseWithoutExt}-${width}w.${extension} ${width}w`)
    .join(', ');
};

/**
 * Image loading placeholder blur effect
 */
export const getBlurDataURL = (width: number = 10, height: number = 10): string => {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');

  if (ctx) {
    // Create gradient placeholder
    const gradient = ctx.createLinearGradient(0, 0, width, height);
    gradient.addColorStop(0, '#6366f1'); // purple-500
    gradient.addColorStop(1, '#8b5cf6'); // violet-500
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);
  }

  return canvas.toDataURL();
};
