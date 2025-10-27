"""
Stream Handler
YAGO v6.1.0

Real-time streaming of AI responses for better UX.
- SSE (Server-Sent Events) support
- Progressive response rendering
- Token-by-token streaming
- Progress indicators
- Instant feedback
"""

import time
import logging
from typing import Iterator, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger("YAGO.StreamHandler")


@dataclass
class StreamChunk:
    """A chunk of streaming data"""
    content: str
    chunk_id: int
    timestamp: datetime
    tokens: int = 0
    is_final: bool = False
    metadata: dict = None


class StreamHandler:
    """
    Real-time Stream Handler

    Features:
    - Token-by-token streaming from AI providers
    - SSE (Server-Sent Events) for web interfaces
    - Progress indicators for CLI
    - Buffering and debouncing
    - Error recovery mid-stream
    """

    def __init__(
        self,
        buffer_size: int = 10,
        debounce_ms: int = 50,
        enable_progress: bool = True
    ):
        """
        Initialize stream handler

        Args:
            buffer_size: Number of tokens to buffer before sending
            debounce_ms: Milliseconds to wait before sending buffered tokens
            enable_progress: Show progress indicators
        """
        self.buffer_size = buffer_size
        self.debounce_ms = debounce_ms / 1000.0  # Convert to seconds
        self.enable_progress = enable_progress

        # Statistics
        self.total_streams = 0
        self.total_chunks = 0
        self.total_bytes_streamed = 0

    def stream_response(
        self,
        response_iterator: Iterator[str],
        on_chunk: Optional[Callable[[StreamChunk], None]] = None,
        on_complete: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None
    ) -> str:
        """
        Stream AI response with callbacks

        Args:
            response_iterator: Iterator yielding response chunks
            on_chunk: Callback for each chunk
            on_complete: Callback when streaming completes
            on_error: Callback on error

        Returns:
            Complete response string
        """
        logger.info("🌊 Starting response stream...")
        self.total_streams += 1

        buffer = []
        full_response = []
        chunk_id = 0
        last_send_time = time.time()

        try:
            for token in response_iterator:
                buffer.append(token)
                current_time = time.time()

                # Send buffer if size reached or debounce time elapsed
                should_send = (
                    len(buffer) >= self.buffer_size or
                    (current_time - last_send_time) >= self.debounce_ms
                )

                if should_send:
                    # Create chunk
                    chunk_content = ''.join(buffer)
                    chunk = StreamChunk(
                        content=chunk_content,
                        chunk_id=chunk_id,
                        timestamp=datetime.now(),
                        tokens=len(buffer),
                        is_final=False
                    )

                    # Send chunk
                    if on_chunk:
                        on_chunk(chunk)

                    # Update stats
                    self.total_chunks += 1
                    self.total_bytes_streamed += len(chunk_content)

                    # Add to full response
                    full_response.append(chunk_content)

                    # Reset buffer
                    buffer = []
                    chunk_id += 1
                    last_send_time = current_time

            # Send remaining buffer
            if buffer:
                chunk_content = ''.join(buffer)
                chunk = StreamChunk(
                    content=chunk_content,
                    chunk_id=chunk_id,
                    timestamp=datetime.now(),
                    tokens=len(buffer),
                    is_final=True
                )

                if on_chunk:
                    on_chunk(chunk)

                full_response.append(chunk_content)
                self.total_chunks += 1
                self.total_bytes_streamed += len(chunk_content)

            # Complete
            complete_response = ''.join(full_response)

            if on_complete:
                on_complete(complete_response)

            logger.info(f"✅ Stream complete: {len(full_response)} chunks, {len(complete_response)} chars")

            return complete_response

        except Exception as e:
            logger.error(f"❌ Stream error: {e}")

            if on_error:
                on_error(e)

            # Return partial response
            return ''.join(full_response)

    def get_stats(self) -> dict:
        """Get streaming statistics"""
        avg_chunks = (
            self.total_chunks / self.total_streams
            if self.total_streams > 0
            else 0
        )

        avg_bytes = (
            self.total_bytes_streamed / self.total_streams
            if self.total_streams > 0
            else 0
        )

        return {
            "total_streams": self.total_streams,
            "total_chunks": self.total_chunks,
            "total_bytes_streamed": self.total_bytes_streamed,
            "avg_chunks_per_stream": round(avg_chunks, 2),
            "avg_bytes_per_stream": round(avg_bytes, 2)
        }


# Singleton instance
_stream_handler_instance = None


def get_stream_handler() -> StreamHandler:
    """Get StreamHandler singleton"""
    global _stream_handler_instance
    if _stream_handler_instance is None:
        _stream_handler_instance = StreamHandler()
    return _stream_handler_instance


def reset_stream_handler():
    """Reset singleton (for testing)"""
    global _stream_handler_instance
    _stream_handler_instance = None
