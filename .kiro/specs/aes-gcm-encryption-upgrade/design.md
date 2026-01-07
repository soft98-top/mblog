# Design Document: AES-GCM Encryption Upgrade

## Overview

This design upgrades the article encryption system from a custom XOR-based encryption to industry-standard AES-GCM (Advanced Encryption Standard - Galois/Counter Mode). The primary goal is to provide password verification capability, preventing the display of garbled text when an incorrect password is entered.

### Key Benefits

- **Password Verification**: AES-GCM is an AEAD (Authenticated Encryption with Associated Data) mode that automatically validates the password during decryption
- **Security**: Industry-standard encryption algorithm with proven security properties
- **Compatibility**: Both Python (cryptography library) and JavaScript (Web Crypto API) have native support
- **User Experience**: Clear error messages instead of garbled text for wrong passwords

## Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Blog Generation (Python)                  │
│                                                              │
│  Markdown + Password  →  PBKDF2  →  AES-GCM  →  Encrypted   │
│                          ↓                        HTML       │
│                      256-bit Key                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    salt:nonce:ciphertext
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Browser (JavaScript)                       │
│                                                              │
│  Password Input  →  PBKDF2  →  AES-GCM  →  Decrypted        │
│                     ↓            Decrypt     Content         │
│                 256-bit Key        ↓                         │
│                              Auth Success/Fail               │
└─────────────────────────────────────────────────────────────┘
```

### Components

1. **Python Encryption Module** (`mblog/templates/runtime/renderer.py`)
   - Uses `cryptography` library
   - Implements AES-GCM-256 encryption
   - Derives keys using PBKDF2-HMAC-SHA256

2. **JavaScript Decryption Module** (`mblog/templates/themes/default/static/js/crypto.js`)
   - Uses Web Crypto API
   - Implements AES-GCM-256 decryption
   - Derives keys using PBKDF2-HMAC-SHA256

3. **UI Integration** (`mblog/templates/themes/default/templates/encrypted_post.html`)
   - Async password handling
   - Loading states
   - Error message display

## Components and Interfaces

### Python Encryption Module

#### Constants

```python
# Encryption parameters
PBKDF2_ITERATIONS = 100_000  # OWASP recommended minimum
KEY_SIZE = 32  # 256 bits
SALT_SIZE = 16  # 128 bits
NONCE_SIZE = 12  # 96 bits (recommended for GCM)
```

#### Key Functions

```python
def _derive_key(password: str, salt: bytes) -> bytes:
    """
    Derive a 256-bit encryption key from password using PBKDF2.
    
    Args:
        password: User's password (any length)
        salt: Random salt (16 bytes)
    
    Returns:
        256-bit (32-byte) encryption key
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(password.encode('utf-8'))

def _encrypt_content(content: str, password: str) -> str:
    """
    Encrypt content using AES-GCM-256.
    
    Args:
        content: Plaintext content (HTML)
        password: User's password
    
    Returns:
        Encrypted data in format: "salt:nonce:ciphertext" (Base64 encoded)
    """
    # Generate random salt and nonce
    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)
    
    # Derive key from password
    key = _derive_key(password, salt)
    
    # Encrypt using AES-GCM
    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(nonce),
    )
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(content.encode('utf-8')) + encryptor.finalize()
    
    # GCM mode automatically includes authentication tag in ciphertext
    # Tag is appended to ciphertext by the library
    
    # Encode components as Base64
    salt_b64 = base64.b64encode(salt).decode('utf-8')
    nonce_b64 = base64.b64encode(nonce).decode('utf-8')
    ciphertext_b64 = base64.b64encode(ciphertext + encryptor.tag).decode('utf-8')
    
    return f"{salt_b64}:{nonce_b64}:{ciphertext_b64}"
```

### JavaScript Decryption Module

#### Constants

```javascript
// Must match Python constants
const PBKDF2_ITERATIONS = 100000;
const KEY_SIZE = 256;  // bits
const SALT_SIZE = 16;  // bytes
const NONCE_SIZE = 12;  // bytes
```

#### Key Functions

```javascript
async function deriveKey(password, salt) {
    /**
     * Derive a 256-bit encryption key from password using PBKDF2.
     * 
     * @param {string} password - User's password
     * @param {Uint8Array} salt - Salt from encrypted data
     * @returns {Promise<CryptoKey>} - 256-bit AES key
     */
    const encoder = new TextEncoder();
    const passwordBuffer = encoder.encode(password);
    
    // Import password as key material
    const passwordKey = await crypto.subtle.importKey(
        'raw',
        passwordBuffer,
        'PBKDF2',
        false,
        ['deriveKey']
    );
    
    // Derive AES key using PBKDF2
    return await crypto.subtle.deriveKey(
        {
            name: 'PBKDF2',
            salt: salt,
            iterations: PBKDF2_ITERATIONS,
            hash: 'SHA-256'
        },
        passwordKey,
        {
            name: 'AES-GCM',
            length: KEY_SIZE
        },
        false,
        ['decrypt']
    );
}

async function decryptContent(encryptedData, password) {
    /**
     * Decrypt content using AES-GCM-256.
     * 
     * @param {string} encryptedData - Format: "salt:nonce:ciphertext" (Base64)
     * @param {string} password - User's password
     * @returns {Promise<string>} - Decrypted plaintext
     * @throws {Error} - If password is wrong or data is corrupted
     */
    try {
        // Parse encrypted data
        const parts = encryptedData.split(':');
        if (parts.length !== 3) {
            throw new Error('CORRUPTED_DATA');
        }
        
        const salt = base64ToBytes(parts[0]);
        const nonce = base64ToBytes(parts[1]);
        const ciphertext = base64ToBytes(parts[2]);
        
        // Validate sizes
        if (salt.length !== SALT_SIZE || nonce.length !== NONCE_SIZE) {
            throw new Error('CORRUPTED_DATA');
        }
        
        // Derive key
        const key = await deriveKey(password, salt);
        
        // Decrypt using AES-GCM
        // GCM mode will automatically verify authentication tag
        // If password is wrong, this will throw an error
        const decrypted = await crypto.subtle.decrypt(
            {
                name: 'AES-GCM',
                iv: nonce
            },
            key,
            ciphertext
        );
        
        // Decode UTF-8
        const decoder = new TextDecoder('utf-8');
        return decoder.decode(decrypted);
        
    } catch (e) {
        // Distinguish between wrong password and corrupted data
        if (e.message === 'CORRUPTED_DATA') {
            throw new Error('CORRUPTED_DATA');
        } else {
            // Web Crypto API throws generic error for auth failure
            throw new Error('WRONG_PASSWORD');
        }
    }
}

function base64ToBytes(base64) {
    /**
     * Decode Base64 string to Uint8Array.
     */
    const binaryString = atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes;
}
```

### UI Integration

#### Template Changes

The template needs to handle async decryption:

```javascript
async function attemptDecrypt() {
    const password = passwordInput.value.trim();
    
    if (!password) {
        showError('请输入密码');
        return;
    }
    
    // Show loading state
    decryptBtn.disabled = true;
    decryptBtn.textContent = '解密中...';
    errorMessage.style.display = 'none';
    
    try {
        // Async decryption
        const decrypted = await decryptContent(encryptedData, password);
        
        // Success - hide form and show content
        document.querySelector('.encrypted-content-wrapper').style.display = 'none';
        decryptedContent.innerHTML = decrypted;
        decryptedContent.style.display = 'block';
        
        // Save password for auto-unlock
        sessionStorage.setItem('post_password_{{ post.slug }}', password);
        
    } catch (e) {
        // Handle errors
        if (e.message === 'CORRUPTED_DATA') {
            showError('数据损坏，无法解密');
        } else if (e.message === 'WRONG_PASSWORD') {
            showError('密码错误，请重试');
        } else {
            showError('解密失败，请重试');
        }
        passwordInput.value = '';
        passwordInput.focus();
        
    } finally {
        // Restore button state
        decryptBtn.disabled = false;
        decryptBtn.textContent = '解锁';
    }
}
```

## Data Models

### Encrypted Data Format

```
Format: "salt:nonce:ciphertext"

Components:
- salt: 16 bytes (128 bits) - Random salt for PBKDF2
- nonce: 12 bytes (96 bits) - Random nonce/IV for AES-GCM
- ciphertext: Variable length - Encrypted content + authentication tag (16 bytes)

All components are Base64 encoded.

Example:
"dGVzdHNhbHQxMjM0NTY=:bm9uY2UxMjM0NTY=:Y2lwaGVydGV4dHdpdGh0YWc="
```

### Post Object

No changes to the Post dataclass - it already has `encrypted` and `password` fields.

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Encryption-Decryption Round Trip

*For any* valid UTF-8 content and any password, encrypting the content with that password and then decrypting with the same password should produce the original content.

**Validates: Requirements 1.2, 2.3, 2.4, 2.6, 5.5**

### Property 2: Encrypted Data Format Validation

*For any* encrypted content, the output format should be `salt:nonce:ciphertext` where salt is 16 bytes, nonce is 12 bytes, and all components are valid Base64 strings.

**Validates: Requirements 1.3, 1.4, 1.6**

### Property 3: Wrong Password Rejection

*For any* encrypted content and any incorrect password, attempting to decrypt should throw an error and not produce garbled text.

**Validates: Requirements 2.5, 3.1, 3.5**

### Property 4: Format Parsing

*For any* valid encrypted data string in format `salt:nonce:ciphertext`, the parser should correctly extract all three components as byte arrays of the correct sizes.

**Validates: Requirements 2.2**

### Property 5: Nonce Uniqueness

*For any* two encryption operations with the same password and content, the nonces should be different (with overwhelming probability).

**Validates: Requirements 1.3** (ensures randomness)

### Property 6: Salt Uniqueness

*For any* two encryption operations with the same password and content, the salts should be different (with overwhelming probability).

**Validates: Requirements 1.4** (ensures randomness)

## Error Handling

### Error Types

1. **WRONG_PASSWORD**: Authentication failure during GCM decryption
   - User message: "密码错误，请重试"
   - Action: Clear password field, refocus input

2. **CORRUPTED_DATA**: Invalid format or data corruption
   - User message: "数据损坏，无法解密"
   - Action: Suggest regenerating the blog

3. **EMPTY_PASSWORD**: User submitted empty password
   - User message: "请输入密码"
   - Action: Focus password input

### Error Flow

```
User enters password
        ↓
    Validate input
        ↓
   Parse encrypted data ──→ Invalid format ──→ CORRUPTED_DATA
        ↓
   Derive key (PBKDF2)
        ↓
   Decrypt (AES-GCM) ──→ Auth failure ──→ WRONG_PASSWORD
        ↓
   Decode UTF-8
        ↓
   Display content
```

## Testing Strategy

### Unit Tests

**Python Side:**
- Test key derivation with known test vectors
- Test encryption output format
- Test salt and nonce randomness
- Test encryption with various content sizes
- Test encryption with various password types (ASCII, Unicode, special chars)

**JavaScript Side:**
- Test key derivation with known test vectors (matching Python)
- Test format parsing with valid and invalid inputs
- Test decryption with known test vectors
- Test error handling for wrong passwords
- Test error handling for corrupted data

### Property-Based Tests

Each property test should run at least 100 iterations with randomized inputs.

**Property 1: Round Trip**
```python
@given(content=st.text(), password=st.text(min_size=1))
def test_round_trip(content, password):
    encrypted = encrypt_content(content, password)
    decrypted = decrypt_content(encrypted, password)
    assert decrypted == content
```

**Property 2: Format Validation**
```python
@given(content=st.text(), password=st.text(min_size=1))
def test_format_validation(content, password):
    encrypted = encrypt_content(content, password)
    parts = encrypted.split(':')
    assert len(parts) == 3
    
    salt = base64.b64decode(parts[0])
    nonce = base64.b64decode(parts[1])
    ciphertext = base64.b64decode(parts[2])
    
    assert len(salt) == 16
    assert len(nonce) == 12
    assert len(ciphertext) > 0
```

**Property 3: Wrong Password Rejection**
```python
@given(content=st.text(), password=st.text(min_size=1), wrong_password=st.text(min_size=1))
def test_wrong_password_rejection(content, password, wrong_password):
    assume(password != wrong_password)
    
    encrypted = encrypt_content(content, password)
    
    with pytest.raises(Exception):
        decrypt_content(encrypted, wrong_password)
```

**Property 4: Format Parsing**
```python
@given(content=st.text(), password=st.text(min_size=1))
def test_format_parsing(content, password):
    encrypted = encrypt_content(content, password)
    salt, nonce, ciphertext = parse_encrypted_data(encrypted)
    
    assert isinstance(salt, bytes) and len(salt) == 16
    assert isinstance(nonce, bytes) and len(nonce) == 12
    assert isinstance(ciphertext, bytes) and len(ciphertext) > 0
```

**Property 5: Nonce Uniqueness**
```python
def test_nonce_uniqueness():
    content = "test content"
    password = "test password"
    
    nonces = set()
    for _ in range(100):
        encrypted = encrypt_content(content, password)
        _, nonce, _ = parse_encrypted_data(encrypted)
        nonces.add(nonce)
    
    # All nonces should be unique
    assert len(nonces) == 100
```

**Property 6: Salt Uniqueness**
```python
def test_salt_uniqueness():
    content = "test content"
    password = "test password"
    
    salts = set()
    for _ in range(100):
        encrypted = encrypt_content(content, password)
        salt, _, _ = parse_encrypted_data(encrypted)
        salts.add(salt)
    
    # All salts should be unique
    assert len(salts) == 100
```

### Integration Tests

1. **Python-JavaScript Compatibility**
   - Encrypt in Python, decrypt in JavaScript (via Node.js test)
   - Verify round-trip works across languages

2. **UI Integration**
   - Test password form submission
   - Test loading states
   - Test error message display
   - Test sessionStorage auto-unlock

3. **End-to-End**
   - Generate blog with encrypted post
   - Load in browser
   - Test correct password
   - Test wrong password
   - Test auto-unlock

## Migration Notes

### Breaking Changes

- Old XOR-encrypted posts will not be readable
- All encrypted posts will be re-encrypted on next blog generation
- No migration path needed (regeneration handles it)

### Code Removal

Remove the following from `renderer.py` and `crypto.js`:
- `_simple_hash()` function
- XOR encryption/decryption logic
- `simpleHash()` JavaScript function
- `decryptContentAsync()` (replaced by main `decryptContent`)

### Dependencies

**Python:**
- Add `cryptography` library to requirements.txt
- Already widely used, no compatibility issues

**JavaScript:**
- Web Crypto API (built into modern browsers)
- No external dependencies needed
- Supported in all modern browsers (Chrome 37+, Firefox 34+, Safari 11+)

## Performance Considerations

### PBKDF2 Iterations

- 100,000 iterations is OWASP recommended minimum
- Python: ~50-100ms on modern hardware
- JavaScript: ~100-200ms in browser
- User experience: Acceptable delay for security benefit

### Encryption/Decryption Speed

- AES-GCM is hardware-accelerated on most platforms
- Python: Negligible impact on blog generation
- JavaScript: <10ms for typical article content

### Browser Compatibility

- Web Crypto API requires HTTPS (or localhost)
- Fallback: Display message if API not available
- All modern browsers supported

## Security Considerations

### Threat Model

**Protected Against:**
- ✅ Casual readers without password
- ✅ Search engine indexing
- ✅ Password guessing (PBKDF2 slows down attacks)
- ✅ Tampering (GCM authentication)

**Not Protected Against:**
- ❌ Determined attackers with source code access
- ❌ Weak passwords (user responsibility)
- ❌ Client-side JavaScript manipulation

### Best Practices

1. **Password Strength**: Recommend 12+ characters
2. **HTTPS Only**: Encryption requires secure context
3. **No Sensitive Data**: Still not suitable for truly confidential information
4. **Regular Updates**: Keep cryptography library updated

### Compliance

- PBKDF2 iterations meet OWASP guidelines
- AES-GCM is NIST approved
- Suitable for personal blog protection
- Not suitable for regulatory compliance (HIPAA, GDPR, etc.)

