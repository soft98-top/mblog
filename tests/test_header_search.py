#!/usr/bin/env python3
"""
Test header search box implementation
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_search_in_header():
    """Test that search box is inside header"""
    base_path = Path(__file__).parent.parent / "mblog" / "templates" / "themes" / "default" / "templates" / "base.html"
    
    with open(base_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check structure
    assert '<header class="site-header">' in content
    assert 'class="header-search"' in content
    assert 'id="search-input"' in content
    
    # Verify search is inside header
    lines = content.split('\n')
    in_header = False
    found_search_in_header = False
    
    for line in lines:
        if '<header class="site-header">' in line:
            in_header = True
        elif '</header>' in line:
            in_header = False
        elif in_header and 'header-search' in line:
            found_search_in_header = True
    
    assert found_search_in_header, "Search box should be inside header"
    
    print("✓ Search box is inside header")
    return True


def test_css_header_search_styles():
    """Test CSS has header search styles"""
    css_path = Path(__file__).parent.parent / "mblog" / "templates" / "themes" / "default" / "static" / "css" / "style.css"
    
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert '.header-search' in content
    assert '.header-search .search-box' in content
    assert '.header-search .search-results' in content
    
    print("✓ CSS has header search styles")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("HEADER SEARCH BOX TESTS")
    print("=" * 60)
    
    try:
        print("\n=== Test 1: Search in Header ===")
        test_search_in_header()
        
        print("\n=== Test 2: CSS Styles ===")
        test_css_header_search_styles()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ FAILED: {e}")
        sys.exit(1)
