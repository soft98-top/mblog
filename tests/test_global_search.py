#!/usr/bin/env python3
"""
Test global search box implementation in base.html
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_base_template_has_search():
    """Test that base.html contains the global search box"""
    base_path = Path(__file__).parent.parent / "mblog" / "templates" / "themes" / "default" / "templates" / "base.html"
    
    with open(base_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for search box block
    assert '{% block search_box %}' in content, "base.html should have search_box block"
    assert 'global-search-container' in content, "base.html should have global-search-container"
    assert 'id="search-input"' in content, "base.html should have search input"
    assert 'id="search-results"' in content, "base.html should have search results container"
    
    print("✓ base.html contains global search box")
    return True


def test_index_no_search():
    """Test that index.html doesn't have its own search box"""
    index_path = Path(__file__).parent.parent / "mblog" / "templates" / "themes" / "default" / "templates" / "index.html"
    
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Should NOT have search-container in content block
    lines = content.split('\n')
    in_content_block = False
    has_search_in_content = False
    
    for line in lines:
        if '{% block content %}' in line:
            in_content_block = True
        elif '{% endblock %}' in line:
            in_content_block = False
        elif in_content_block and 'search-container' in line:
            has_search_in_content = True
    
    assert not has_search_in_content, "index.html should not have search-container in content block"
    
    print("✓ index.html doesn't have duplicate search box")
    return True


def test_post_no_search():
    """Test that post.html doesn't have its own search box"""
    post_path = Path(__file__).parent.parent / "mblog" / "templates" / "themes" / "default" / "templates" / "post.html"
    
    with open(post_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Should NOT have search-container in content block
    lines = content.split('\n')
    in_content_block = False
    has_search_in_content = False
    
    for line in lines:
        if '{% block content %}' in line:
            in_content_block = True
        elif '{% endblock %}' in line:
            in_content_block = False
        elif in_content_block and 'search-container' in line:
            has_search_in_content = True
    
    assert not has_search_in_content, "post.html should not have search-container in content block"
    
    print("✓ post.html doesn't have duplicate search box")
    return True


def test_archive_hides_search():
    """Test that archive.html hides the search box"""
    archive_path = Path(__file__).parent.parent / "mblog" / "templates" / "themes" / "default" / "templates" / "archive.html"
    
    with open(archive_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Should override search_box block to hide it
    assert '{% block search_box %}' in content, "archive.html should override search_box block"
    
    # Check that the block is empty or has a comment
    lines = content.split('\n')
    in_search_block = False
    search_block_content = []
    
    for line in lines:
        if '{% block search_box %}' in line:
            in_search_block = True
        elif in_search_block and '{% endblock %}' in line:
            break
        elif in_search_block:
            search_block_content.append(line.strip())
    
    # Block should be empty or only contain comments
    non_comment_lines = [l for l in search_block_content if l and not l.startswith('<!--')]
    assert len(non_comment_lines) == 0, "archive.html search_box block should be empty"
    
    print("✓ archive.html hides search box")
    return True


def test_css_has_global_styles():
    """Test that CSS has styles for global search container"""
    css_path = Path(__file__).parent.parent / "mblog" / "templates" / "themes" / "default" / "static" / "css" / "style.css"
    
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert '.global-search-container' in content, "CSS should have .global-search-container styles"
    
    print("✓ CSS has global search container styles")
    return True


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("GLOBAL SEARCH BOX - TEMPLATE STRUCTURE TESTS")
    print("=" * 60)
    
    tests = [
        ("Base template has search box", test_base_template_has_search),
        ("Index page no duplicate search", test_index_no_search),
        ("Post page no duplicate search", test_post_no_search),
        ("Archive page hides search", test_archive_hides_search),
        ("CSS has global styles", test_css_has_global_styles),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n=== {test_name} ===")
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if passed == len(tests):
        print("\n✅ All template structure tests passed!")
        print("\nGlobal search box implementation:")
        print("1. ✅ Search box in base.html (global)")
        print("2. ✅ Removed from index.html")
        print("3. ✅ Removed from post.html")
        print("4. ✅ Hidden in archive.html")
        print("5. ✅ CSS styles added")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
