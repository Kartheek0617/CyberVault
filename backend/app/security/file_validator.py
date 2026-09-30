"""
CyberVault — File validation utilities.
Security:
  - Validates file size, extension whitelist, and MIME type.
  - Does NOT trust user-provided Content-Type headers.
  - Uses python-magic for server-side MIME detection where available.
  - Prevents path traversal by rejecting any path separators in filenames.
"""
import os
import re
from pathlib import Path

# Allowed extensions mapped to their expected MIME types
ALLOWED_TYPES: dict[str, list[str]] = {
    ".pdf":  ["application/pdf"],
    ".txt":  ["text/plain"],
    ".csv":  ["text/plain", "text/csv", "application/csv"],
    ".jpg":  ["image/jpeg"],
    ".jpeg": ["image/jpeg"],
    ".png":  ["image/png"],
    ".mp4":  ["video/mp4"],
    ".zip":  ["application/zip", "application/x-zip-compressed"],
    ".pcap": ["application/octet-stream", "application/vnd.tcpdump.pcap"],
    ".dd":   ["application/octet-stream"],
    ".e01":  ["application/octet-stream"],
    ".json": ["application/json", "text/plain"],
    ".log":  ["text/plain"],
    ".xml":  ["text/xml", "application/xml", "text/plain"],
    ".doc":  ["application/msword"],
    ".docx": ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
}

MAX_FILE_SIZE_BYTES = 200 * 1024 * 1024  # 200 MB


def validate_filename(filename: str) -> tuple[bool, str]:
    """
    Security: Reject filenames containing path traversal characters.
    """
    if not filename or len(filename) > 255:
        return False, "Filename is empty or too long."
    # Reject any path separators or null bytes
    if any(c in filename for c in ["/", "\\", "\x00", ".."]):
        return False, "Filename contains invalid characters."
    # Must have an extension
    ext = Path(filename).suffix.lower()
    if not ext:
        return False, "Filename must have an extension."
    return True, ""


def validate_extension(filename: str) -> tuple[bool, str, str]:
    """
    Returns (is_valid, error_message, extension).
    """
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_TYPES:
        return False, f"File type '{ext}' is not permitted.", ext
    return True, "", ext


def validate_file_size(size_bytes: int) -> tuple[bool, str]:
    """Reject files exceeding the maximum allowed size."""
    if size_bytes <= 0:
        return False, "File is empty."
    if size_bytes > MAX_FILE_SIZE_BYTES:
        return False, f"File exceeds maximum size of {MAX_FILE_SIZE_BYTES // (1024*1024)} MB."
    return True, ""


def detect_mime_type(file_bytes: bytes) -> str:
    """
    Best-effort MIME type detection from file content (magic bytes).
    Falls back to 'application/octet-stream' if detection fails.
    """
    try:
        import magic
        mime = magic.from_buffer(file_bytes[:2048], mime=True)
        return mime
    except Exception:
        # Fallback: use simple magic byte checks
        return _simple_magic(file_bytes)


def _simple_magic(data: bytes) -> str:
    """Minimal magic-byte MIME detection without libmagic dependency."""
    if data[:4] == b"%PDF":
        return "application/pdf"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:3] in (b"\xff\xd8\xff",):
        return "image/jpeg"
    if data[:4] in (b"PK\x03\x04", b"PK\x05\x06"):
        return "application/zip"
    if data[:4] == b"\xa1\xb2\xc3\xd4" or data[:4] == b"\xd4\xc3\xb2\xa1":
        return "application/vnd.tcpdump.pcap"
    if data[:4] == b"\x00\x00\x00\x18" or data[:7] == b"ftyp":
        return "video/mp4"
    return "application/octet-stream"


def validate_mime_against_extension(detected_mime: str, extension: str) -> tuple[bool, str]:
    """
    Check the detected MIME type against the expected types for the extension.
    Allows some flexibility for ambiguous types like text/plain.
    """
    allowed = ALLOWED_TYPES.get(extension, [])
    if not allowed:
        return False, "Unknown extension."
    # Some formats (zip, binary) can appear as octet-stream — allow gracefully
    if detected_mime in allowed:
        return True, ""
    if "application/octet-stream" in allowed and detected_mime == "application/octet-stream":
        return True, ""
    # Text files are often detected as text/plain regardless of extension
    if detected_mime == "text/plain" and "text/plain" in [m.split(";")[0] for m in allowed]:
        return True, ""
    return False, f"File content does not match extension. Detected: {detected_mime}."
