/**
 * Convert absoule URL to full URL in case the application is hosted on a subpath.
 *
 * ```js
 * convertAbsolutePathtoFullURL("/assets/image.png", "http://localhost:3000/hello/?foo=bar")
 * // => 'http://localhost:3000/hello/assets/image.png'
 * ```
 */
export function convertAbsolutePathtoFullURL(
	path: string,
	base = window.location.toString(),
) {
	return new URL(`.${path}`, base).toString();
}
