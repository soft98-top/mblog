# Implementation Plan: Search Functionality

## Overview

This implementation plan breaks down the search functionality into discrete coding tasks. The implementation will be done in Python (for backend index generation) and JavaScript (for frontend search logic). Each task builds on previous steps to create a complete, working search feature.

## Tasks

- [x] 1. Generate search index JSON file
  - Modify `mblog/templates/runtime/generator.py` to add `_generate_search_index()` method
  - Create JSON file at `{output_dir}/search-index.json` containing post metadata
  - Include fields: title, url, date, tags, description, relative_path
  - Call this method from `_generate_pages()` after generating all pages
  - _Requirements: 4.1, 4.2, 4.3_

- [ ]* 1.1 Write unit test for search index generation
  - Test that index file is created with correct structure
  - Test that all posts are included in the index
  - Test that all required fields are present
  - _Requirements: 4.1, 4.2, 4.3_

- [ ]* 1.2 Write property test for search index completeness
  - **Property 6: Search index contains all required fields**
  - **Validates: Requirements 4.2**

- [x] 2. Create search engine JavaScript module
  - Create new file `mblog/templates/themes/default/static/js/search.js`
  - Implement `SearchEngine` class with methods: `loadIndex()`, `parseQuery()`, `search()`
  - Implement query parser to extract tags (prefixed with #) and keywords
  - Implement search algorithm that filters by tags AND keywords
  - _Requirements: 2.1, 2.4, 2.6, 2.7, 2.8, 7.1, 7.2, 7.4_

- [ ]* 2.1 Write property test for multi-keyword matching
  - **Property 1: Multi-keyword title matching**
  - **Validates: Requirements 2.1, 2.4, 2.6**

- [ ]* 2.2 Write property test for tag filtering
  - **Property 2: Tag filtering**
  - **Validates: Requirements 2.7**

- [ ]* 2.3 Write property test for combined filtering
  - **Property 3: Combined tag and keyword filtering**
  - **Validates: Requirements 2.8**

- [ ]* 2.4 Write property test for query parsing
  - **Property 4: Query parsing separates tags and keywords**
  - **Validates: Requirements 7.1, 7.2, 7.4**

- [ ]* 2.5 Write property test for Unicode support
  - **Property 10: Unicode support in search**
  - **Validates: Requirements 6.4**

- [ ]* 2.6 Write unit tests for edge cases
  - Test empty query returns all posts
  - Test no results scenario
  - Test Chinese character searches
  - Test mixed language queries
  - Test malformed tag syntax (e.g., "# keyword")
  - _Requirements: 2.2, 2.3, 6.1, 6.2, 6.3, 7.5_

- [x] 3. Implement search results display and highlighting
  - Add `displayResults()` method to SearchEngine class
  - Add `highlightMatch()` method to wrap matched keywords in `<mark>` tags
  - Ensure results maintain date ordering (newest first)
  - Render results with title, date, description, and link
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ]* 3.1 Write property test for date ordering
  - **Property 5: Search results maintain date ordering**
  - **Validates: Requirements 3.4**

- [ ]* 3.2 Write property test for result display fields
  - **Property 7: Result display includes required information**
  - **Validates: Requirements 3.1**

- [ ]* 3.3 Write property test for result links
  - **Property 8: Result links are valid**
  - **Validates: Requirements 3.2**

- [ ]* 3.4 Write property test for keyword highlighting
  - **Property 9: Matched keywords are highlighted**
  - **Validates: Requirements 3.3**

- [x] 4. Add search box UI to index page
  - Modify `mblog/templates/themes/default/templates/index.html`
  - Add search container with input box and results div
  - Add placeholder text: "搜索文章... (支持 #标签 多关键字)"
  - Position search box prominently at the top of the page
  - _Requirements: 1.1, 1.4_

- [x] 5. Add search box UI to archive page
  - Modify `mblog/templates/themes/default/templates/archive.html`
  - Add same search container as index page
  - Ensure consistent styling and behavior
  - _Requirements: 1.2, 1.4_

- [x] 6. Add search box styling
  - Modify `mblog/templates/themes/default/static/css/style.css`
  - Add styles for `.search-container`, `.search-box`, `.search-results`
  - Add focus styles for visual feedback
  - Add styles for result items and highlighting (`<mark>` tags)
  - Ensure responsive design for mobile devices
  - _Requirements: 1.3_

- [x] 7. Wire search functionality to UI
  - Modify `mblog/templates/themes/default/static/js/main.js` or create initialization code
  - Initialize SearchEngine on page load
  - Load search index from `/search-index.json`
  - Attach event listeners to search input for real-time filtering
  - Handle index load errors gracefully
  - _Requirements: 4.4, 2.5_

- [ ]* 7.1 Write integration test for search UI
  - Test that search box appears on index and archive pages
  - Test that search index is loaded successfully
  - Test that typing in search box triggers filtering
  - _Requirements: 1.1, 1.2, 4.4_

- [x] 8. Checkpoint - Ensure all tests pass
  - Run all unit tests and property tests
  - Verify search functionality works end-to-end
  - Test with sample blog containing various posts
  - Ask the user if questions arise

- [x] 9. Add error handling and edge case handling
  - Implement error message display for failed index load
  - Implement "No results found" message
  - Handle very long queries (truncate if needed)
  - Ensure graceful degradation if JavaScript is disabled
  - _Requirements: Error Handling section_

- [ ]* 9.1 Write unit tests for error handling
  - Test index load failure shows error message
  - Test no results shows appropriate message
  - Test malformed JSON in index is handled
  - _Requirements: Error Handling section_

- [x] 10. Final checkpoint - Verify all requirements
  - Test search with Chinese characters
  - Test search with multiple keywords
  - Test search with tags
  - Test combined tag and keyword search
  - Verify performance with large post collections
  - Ensure all tests pass
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The implementation uses existing Python and JavaScript infrastructure
- Search operates entirely client-side for fast performance
