import type { ILogger } from "@/composables/useLogger";

/**
 * Optimizes an image file by resizing and compressing it if it's larger than 2MB.
 * Falls back to the original file if optimization fails.
 *
 * @param file - The image file to optimize
 * @param logger - Logger instance for debugging
 * @returns Promise that resolves to either the optimized file or the original file
 */
export const optimizeImage = async (
	file: File,
	logger: ILogger,
): Promise<File> => {
	// Only optimize if file is larger than 2MB
	if (file.size <= 2 * 1024 * 1024) {
		return file;
	}

	return new Promise((resolve) => {
		const canvas = document.createElement("canvas");
		const ctx = canvas.getContext("2d");

		if (!ctx) {
			logger.warn(
				`Canvas 2D context not available for image optimization: ${file.name}, using original`,
			);
			resolve(file);
			return;
		}

		const img = new Image();

		const objectUrl = URL.createObjectURL(file);

		img.onload = () => {
			// Calculate new dimensions (max 1920x1080)
			const maxWidth = 1920;
			const maxHeight = 1080;
			let { width, height } = img;

			if (width > maxWidth || height > maxHeight) {
				const ratio = Math.min(maxWidth / width, maxHeight / height);
				width = Math.floor(width * ratio);
				height = Math.floor(height * ratio);
			}

			canvas.width = width;
			canvas.height = height;

			// Draw and compress
			ctx.drawImage(img, 0, 0, width, height);

			// Clean up the object URL after use
			URL.revokeObjectURL(objectUrl);

			canvas.toBlob(
				(blob) => {
					if (blob) {
						resolve(
							new File([blob], file.name, { type: "image/jpeg" }),
						);
					} else {
						// Fall back to original file if compression fails
						logger.warn(
							`Failed to compress image: ${file.name}, using original`,
						);
						resolve(file);
					}
				},
				"image/jpeg",
				0.85,
			);
		};

		img.onerror = () => {
			// Clean up the object URL on error as well
			URL.revokeObjectURL(objectUrl);
			// Fall back to original file if image loading fails
			// This allows the user to still send the image even if optimization fails
			logger.warn(
				`Failed to optimize image: ${file.name}, using original`,
			);
			resolve(file);
		};

		img.src = objectUrl;
	});
};
