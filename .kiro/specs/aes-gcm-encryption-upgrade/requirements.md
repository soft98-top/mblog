# Requirements Document

## Introduction

升级文章加密功能，从自定义 XOR 加密升级到标准的 AES-GCM 加密算法，以提供密码验证能力和更高的安全性。

## Glossary

- **System**: mblog 静态博客生成器
- **Encryption_Module**: Python 端的加密模块（renderer.py）
- **Decryption_Module**: JavaScript 端的解密模块（crypto.js）
- **AES-GCM**: Advanced Encryption Standard - Galois/Counter Mode，一种带认证的加密模式
- **Web_Crypto_API**: 浏览器提供的标准加密 API
- **PBKDF2**: Password-Based Key Derivation Function 2，密码派生函数
- **Encrypted_Post**: 需要密码才能查看的加密文章

## Requirements

### Requirement 1: Python 端 AES-GCM 加密实现

**User Story:** As a blog author, I want the system to use AES-GCM encryption for my posts, so that the content is securely encrypted with industry-standard algorithms.

#### Acceptance Criteria

1. THE Encryption_Module SHALL use AES-GCM-256 encryption algorithm
2. WHEN encrypting content, THE Encryption_Module SHALL derive a 256-bit key from the password using PBKDF2-HMAC-SHA256
3. WHEN encrypting content, THE Encryption_Module SHALL generate a random 96-bit (12-byte) nonce/IV
4. WHEN encrypting content, THE Encryption_Module SHALL generate a random 128-bit (16-byte) salt for PBKDF2
5. THE Encryption_Module SHALL use at least 100,000 iterations for PBKDF2 key derivation
6. THE Encryption_Module SHALL return encrypted data in format: `salt:nonce:ciphertext` (all Base64 encoded)
7. THE Encryption_Module SHALL include authentication tag in the ciphertext (GCM mode provides this automatically)

### Requirement 2: JavaScript 端 AES-GCM 解密实现

**User Story:** As a blog reader, I want to decrypt encrypted posts in my browser using the correct password, so that I can view the protected content.

#### Acceptance Criteria

1. THE Decryption_Module SHALL use Web Crypto API for AES-GCM decryption
2. WHEN decrypting content, THE Decryption_Module SHALL parse the format `salt:nonce:ciphertext`
3. WHEN decrypting content, THE Decryption_Module SHALL derive the same 256-bit key using PBKDF2-HMAC-SHA256 with the provided salt
4. THE Decryption_Module SHALL use the same PBKDF2 iteration count as the encryption module (100,000)
5. WHEN the password is incorrect, THE Decryption_Module SHALL throw a clear error (GCM authentication will fail)
6. WHEN decryption succeeds, THE Decryption_Module SHALL return the UTF-8 decoded plaintext
7. THE Decryption_Module SHALL be implemented as an async function

### Requirement 3: 密码验证和错误处理

**User Story:** As a blog reader, I want to see a clear error message when I enter the wrong password, so that I know to try again with the correct password.

#### Acceptance Criteria

1. WHEN an incorrect password is provided, THE Decryption_Module SHALL reject with an error
2. WHEN decryption fails due to wrong password, THE System SHALL display "密码错误，请重试" message
3. WHEN decryption fails due to corrupted data, THE System SHALL display "数据损坏，无法解密" message
4. WHEN decryption succeeds, THE System SHALL hide the password form and display the decrypted content
5. THE System SHALL NOT display garbled text when the password is incorrect

### Requirement 4: UI 集成和用户体验

**User Story:** As a blog reader, I want a smooth experience when entering passwords, so that I can easily access encrypted content.

#### Acceptance Criteria

1. WHEN the decrypt button is clicked, THE System SHALL show a loading indicator during decryption
2. WHEN decryption is in progress, THE System SHALL disable the decrypt button to prevent multiple submissions
3. WHEN decryption completes (success or failure), THE System SHALL re-enable the decrypt button
4. WHEN decryption succeeds, THE System SHALL save the password to sessionStorage for auto-unlock
5. WHEN the page loads with a saved password, THE System SHALL automatically attempt decryption

### Requirement 5: 加密参数配置

**User Story:** As a system administrator, I want the encryption parameters to be configurable, so that I can balance security and performance.

#### Acceptance Criteria

1. THE Encryption_Module SHALL define PBKDF2 iterations as a constant (default: 100,000)
2. THE Encryption_Module SHALL define key size as a constant (default: 256 bits)
3. THE Encryption_Module SHALL define nonce size as a constant (default: 96 bits / 12 bytes)
4. THE Encryption_Module SHALL define salt size as a constant (default: 128 bits / 16 bytes)
5. THE Decryption_Module SHALL use the same constants as the Encryption_Module

### Requirement 6: 测试和验证

**User Story:** As a developer, I want comprehensive tests for the encryption system, so that I can ensure it works correctly.

#### Acceptance Criteria

1. THE System SHALL provide unit tests for encryption with known test vectors
2. THE System SHALL provide unit tests for decryption with known test vectors
3. THE System SHALL provide integration tests for the full encrypt-decrypt cycle
4. THE System SHALL test error handling for incorrect passwords
5. THE System SHALL test error handling for corrupted data
6. THE System SHALL verify that Python and JavaScript implementations are compatible

### Requirement 7: 文档更新

**User Story:** As a user, I want updated documentation explaining the new encryption system, so that I understand how it works and its security properties.

#### Acceptance Criteria

1. THE System SHALL update docs/encrypted-posts.md to reflect AES-GCM encryption
2. THE documentation SHALL explain the security properties of AES-GCM
3. THE documentation SHALL document the encryption format (salt:nonce:ciphertext)
4. THE documentation SHALL explain password requirements and best practices
5. THE documentation SHALL note that this is a breaking change from the old XOR encryption

### Requirement 8: 向后兼容性处理

**User Story:** As a blog author, I want to know that old encrypted posts will be re-encrypted automatically, so that I don't need to manually update them.

#### Acceptance Criteria

1. THE System SHALL NOT attempt to decrypt old XOR-encrypted format
2. WHEN generating the blog, THE System SHALL re-encrypt all encrypted posts using AES-GCM
3. THE System SHALL remove any code related to XOR encryption
4. THE System SHALL remove the old `simpleHash` function and XOR encryption logic

