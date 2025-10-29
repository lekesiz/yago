"""
Compression Middleware for FastAPI
Gzip compression for responses > 1KB
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
import gzip
import io


class GZipMiddleware(BaseHTTPMiddleware):
    """
    Compress responses with gzip if:
    - Client supports gzip (Accept-Encoding header)
    - Response is larger than minimum_size
    - Content type is compressible
    """

    def __init__(
        self,
        app,
        minimum_size: int = 1024,  # 1KB
        compresslevel: int = 6,  # Compression level (1-9, 6 is default)
    ):
        super().__init__(app)
        self.minimum_size = minimum_size
        self.compresslevel = compresslevel

        # Content types that should be compressed
        self.compressible_types = {
            "text/html",
            "text/css",
            "text/plain",
            "text/xml",
            "application/json",
            "application/javascript",
            "application/xml",
            "application/xhtml+xml",
            "application/rss+xml",
            "application/atom+xml",
            "image/svg+xml",
        }

    async def dispatch(self, request: Request, call_next):
        """Process request and compress response if applicable"""

        # Check if client accepts gzip
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding.lower():
            return await call_next(request)

        # Get response
        response = await call_next(request)

        # Check if response should be compressed
        if not self._should_compress(response):
            return response

        # Compress response body
        if isinstance(response, StreamingResponse):
            # For streaming responses, wrap the iterator
            return await self._compress_streaming_response(response)
        else:
            # For regular responses, compress the body
            return await self._compress_response(response)

    def _should_compress(self, response: Response) -> bool:
        """Determine if response should be compressed"""

        # Don't compress if already compressed
        if "content-encoding" in response.headers:
            return False

        # Check content type
        content_type = response.headers.get("content-type", "").split(";")[0].strip()
        if content_type not in self.compressible_types:
            return False

        # Check content length
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) < self.minimum_size:
            return False

        return True

    async def _compress_response(self, response: Response) -> Response:
        """Compress regular response"""

        # Get response body
        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        # Check if body is large enough to compress
        if len(body) < self.minimum_size:
            return response

        # Compress body
        compressed_body = gzip.compress(body, compresslevel=self.compresslevel)

        # Only use compression if it actually reduces size
        if len(compressed_body) >= len(body):
            return response

        # Create new response with compressed body
        response.headers["content-encoding"] = "gzip"
        response.headers["content-length"] = str(len(compressed_body))
        response.headers["vary"] = "Accept-Encoding"

        # Update response body
        return Response(
            content=compressed_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

    async def _compress_streaming_response(self, response: StreamingResponse) -> StreamingResponse:
        """Compress streaming response"""

        async def compress_stream():
            """Generator that compresses chunks on the fly"""
            compressor = gzip.GzipFile(
                mode='wb',
                fileobj=io.BytesIO(),
                compresslevel=self.compresslevel
            )

            async for chunk in response.body_iterator:
                compressor.write(chunk)
                # Yield compressed data
                compressed = compressor.fileobj.getvalue()
                if compressed:
                    yield compressed
                    # Reset buffer
                    compressor.fileobj.seek(0)
                    compressor.fileobj.truncate()

            # Flush remaining data
            compressor.close()
            final_data = compressor.fileobj.getvalue()
            if final_data:
                yield final_data

        # Update headers
        response.headers["content-encoding"] = "gzip"
        response.headers["vary"] = "Accept-Encoding"
        del response.headers["content-length"]  # Unknown length for streaming

        # Return new streaming response
        return StreamingResponse(
            compress_stream(),
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )


# Brotli compression (higher compression ratio but slower)
try:
    import brotli

    class BrotliMiddleware(BaseHTTPMiddleware):
        """
        Compress responses with Brotli
        Better compression than gzip but slower
        """

        def __init__(self, app, minimum_size: int = 1024, quality: int = 4):
            super().__init__(app)
            self.minimum_size = minimum_size
            self.quality = quality  # 0-11, higher = better compression but slower

            self.compressible_types = {
                "text/html",
                "text/css",
                "text/plain",
                "text/xml",
                "application/json",
                "application/javascript",
                "application/xml",
                "application/xhtml+xml",
                "application/rss+xml",
                "application/atom+xml",
                "image/svg+xml",
            }

        async def dispatch(self, request: Request, call_next):
            """Process request and compress response if applicable"""

            # Check if client accepts brotli
            accept_encoding = request.headers.get("accept-encoding", "")
            if "br" not in accept_encoding.lower():
                return await call_next(request)

            # Get response
            response = await call_next(request)

            # Check if response should be compressed
            if not self._should_compress(response):
                return response

            # Get response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            # Check size
            if len(body) < self.minimum_size:
                return response

            # Compress with brotli
            compressed_body = brotli.compress(body, quality=self.quality)

            # Only use compression if it reduces size
            if len(compressed_body) >= len(body):
                return response

            # Update headers
            response.headers["content-encoding"] = "br"
            response.headers["content-length"] = str(len(compressed_body))
            response.headers["vary"] = "Accept-Encoding"

            return Response(
                content=compressed_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        def _should_compress(self, response: Response) -> bool:
            """Determine if response should be compressed"""
            if "content-encoding" in response.headers:
                return False

            content_type = response.headers.get("content-type", "").split(";")[0].strip()
            if content_type not in self.compressible_types:
                return False

            return True

except ImportError:
    BrotliMiddleware = None
    print("[Warning] brotli module not installed, BrotliMiddleware disabled")
