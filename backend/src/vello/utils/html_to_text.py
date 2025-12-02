"""
Utility to convert HTML email content to plain text.
Uses html2text library (lightweight alternative to BeautifulSoup).
"""
import html2text


def html_to_text(html_content: str) -> str:
    """
    Convert HTML email content to plain text.
    
    Args:
        html_content: HTML string to convert
        
    Returns:
        Plain text version of the HTML content
    """
    # Configure html2text for email-friendly output
    h = html2text.HTML2Text()
    h.ignore_links = False  # Keep links as [text](url)
    h.ignore_images = True  # Remove images
    h.body_width = 0  # Don't wrap lines (preserve original formatting)
    h.unicode_snob = True  # Use unicode characters
    h.skip_internal_links = True  # Skip anchor links
    
    # Convert HTML to text
    text = h.handle(html_content)
    
    # Clean up extra whitespace while preserving structure
    lines = [line.rstrip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # Remove excessive blank lines (more than 2 consecutive)
    while '\n\n\n' in text:
        text = text.replace('\n\n\n', '\n\n')
    
    return text.strip()

