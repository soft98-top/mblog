# Implementation Plan: AES-GCM Encryption Upgrade

## Overview

Upgrade the article encryption system from custom XOR encryption to industry-standard AES-GCM encryption. This implementation will provide password verification, preventing garbled text display when incorrect passwords are entered.

## Tasks

- [x] 1. Update Python dependencies and add encryption constants
  - Add `cryptography` library to requirements.txt
  - Define encryption constants in renderer.py (PBKDF2_ITERATIONS, KEY_SIZE, SALT_SIZE, NONCE_SIZE)
  - _Requirements: 1.1, 1.5, 5.1, 5.2, 5.3, 5.4_

- [ ] 2. Implement Python AES-GCM encryption
  - [x] 2.1 Implement `_derive_key()` method using PBKDF2-HMAC-SHA256
    - Use cryptography library's PBKDF2HMAC
    - Accept password and salt, return 256-bit key
    - Use 100,000 iterations with SHA-256
    - _Requirements: 1.2, 1.5_

  - [x] 2.2 Implement `_encrypt_content()` method using AES-GCM
    - Generate random salt (16 bytes) and nonce (12 bytes)
    - Derive key using `_derive_key()`
    - Encrypt content using AES-GCM-256
    - Return format: `salt:nonce:ciphertext` (Base64 encoded)
    - _Requirements: 1.1, 1.3, 1.4, 1.6, 1.7_

  - [ ]* 2.3 Write property test for encryption format validation
    - **Property 2: Encrypted Data Format Validation**
    - **Validates: Requirements 1.3, 1.4, 1.6**

  - [ ]* 2.4 Write property test for salt uniqueness
    - **Property 6: Salt Uniqueness**
    - **Validates: Requirements 1.4**

  - [ ]* 2.5 Write property test for nonce uniqueness
    - **Property 5: Nonce Uniqueness**
    - **Validates: Requirements 1.3**

- [x] 3. Remove old XOR encryption code
  - Remove `_simple_hash()` method from renderer.py
  - Remove old XOR encryption logic from `_encrypt_content()`
  - Clean up any XOR-related comments
  - _Requirements: 8.3, 8.4_

- [x] 4. Implement JavaScript AES-GCM decryption
  - [x] 4.1 Define encryption constants in crypto.js
    - Match Python constants (PBKDF2_ITERATIONS, KEY_SIZE, SALT_SIZE, NONCE_SIZE)
    - _Requirements: 5.5_

  - [x] 4.2 Implement `deriveKey()` async function using PBKDF2
    - Use Web Crypto API's PBKDF2
    - Accept password and salt, return CryptoKey
    - Use 100,000 iterations with SHA-256
    - _Requirements: 2.3, 2.4_

  - [x] 4.3 Implement `decryptContent()` async function using AES-GCM
    - Parse format: `salt:nonce:ciphertext`
    - Derive key using `deriveKey()`
    - Decrypt using AES-GCM
    - Handle authentication failures (wrong password)
    - Return UTF-8 decoded plaintext
    - _Requirements: 2.1, 2.2, 2.5, 2.6, 2.7_

  - [x] 4.4 Implement error handling and validation
    - Validate encrypted data format (3 parts separated by colons)
    - Validate salt and nonce sizes
    - Distinguish between WRONG_PASSWORD and CORRUPTED_DATA errors
    - _Requirements: 3.1, 3.2, 3.3, 3.5_

  - [ ]* 4.5 Write property test for format parsing
    - **Property 4: Format Parsing**
    - **Validates: Requirements 2.2**

  - [ ]* 4.6 Write property test for wrong password rejection
    - **Property 3: Wrong Password Rejection**
    - **Validates: Requirements 2.5, 3.1, 3.5**

- [x] 5. Remove old XOR decryption code
  - Remove `simpleHash()` function from crypto.js
  - Remove old XOR decryption logic
  - Remove `decryptContentAsync()` function (if it exists)
  - Clean up any XOR-related comments
  - _Requirements: 8.3, 8.4_

- [x] 6. Update UI integration for async decryption
  - [x] 6.1 Update `attemptDecrypt()` to be async
    - Add async/await for `decryptContent()` call
    - Add loading state (disable button, show "解密中...")
    - _Requirements: 2.7, 4.1, 4.2_

  - [x] 6.2 Implement error message handling
    - Display "密码错误，请重试" for WRONG_PASSWORD
    - Display "数据损坏，无法解密" for CORRUPTED_DATA
    - Display "请输入密码" for empty password
    - Clear password field on error
    - _Requirements: 3.2, 3.3_

  - [x] 6.3 Implement success handling
    - Hide password form on successful decryption
    - Display decrypted content
    - Save password to sessionStorage
    - _Requirements: 3.4, 4.4_

  - [x] 6.4 Ensure button state management
    - Re-enable button after decryption completes (success or failure)
    - Restore button text after decryption
    - _Requirements: 4.3_

  - [ ]* 6.5 Write integration tests for UI behavior
    - Test loading state display
    - Test error message display
    - Test sessionStorage auto-unlock
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 7. Checkpoint - Test Python-JavaScript compatibility
  - Ensure all tests pass, verify round-trip encryption works

- [ ] 8. Write cross-language compatibility tests
  - [ ]* 8.1 Write property test for encryption-decryption round trip
    - **Property 1: Encryption-Decryption Round Trip**
    - **Validates: Requirements 1.2, 2.3, 2.4, 2.6, 5.5**
    - Test with various content types (ASCII, Unicode, HTML, special characters)
    - Test with various password types (short, long, Unicode, special characters)

  - [ ]* 8.2 Write unit tests for known test vectors
    - Create test vectors with known salt, nonce, password, and expected output
    - Verify Python encryption matches expected output
    - Verify JavaScript decryption matches expected output
    - _Requirements: 6.1, 6.2, 6.6_

  - [ ]* 8.3 Write integration test for error handling
    - Test wrong password produces clear error
    - Test corrupted data produces clear error
    - Test empty password produces clear error
    - _Requirements: 6.4, 6.5_

- [ ] 9. Update documentation
  - [ ] 9.1 Update docs/encrypted-posts.md
    - Replace XOR encryption description with AES-GCM
    - Document new encryption format (salt:nonce:ciphertext)
    - Explain security properties of AES-GCM
    - Update security considerations section
    - Note breaking change from old XOR encryption
    - _Requirements: 7.1, 7.2, 7.3, 7.5_

  - [ ] 9.2 Add password best practices section
    - Recommend 12+ character passwords
    - Explain PBKDF2 protection against brute force
    - Note HTTPS requirement for Web Crypto API
    - _Requirements: 7.4_

  - [ ] 9.3 Create migration notes
    - Explain that regenerating blog will re-encrypt all posts
    - Note that old encrypted posts are not compatible
    - Document that no manual migration is needed
    - _Requirements: 8.2_

- [ ] 10. Final checkpoint - Ensure all tests pass
  - Run full test suite
  - Verify encryption/decryption works in browser
  - Test with real blog content
  - Verify error messages display correctly
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The `cryptography` library is a well-maintained, widely-used Python package
- Web Crypto API is built into all modern browsers (no external dependencies)
- PBKDF2 with 100,000 iterations meets OWASP security guidelines
- AES-GCM provides both encryption and authentication (AEAD)

