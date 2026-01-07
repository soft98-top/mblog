/**
 * Test Python-JavaScript encryption compatibility
 * This test verifies that content encrypted in Python can be decrypted in JavaScript
 */

// Import Web Crypto API for Node.js
const { webcrypto } = require('crypto');
global.crypto = webcrypto;
global.atob = (str) => Buffer.from(str, 'base64').toString('binary');

// Constants - must match Python and JS implementations
const PBKDF2_ITERATIONS = 100000;
const KEY_SIZE = 256;  // bits
const SALT_SIZE = 16;  // bytes
const NONCE_SIZE = 12;  // bytes

/**
 * Base64 decode
 */
function base64ToBytes(base64) {
    const binaryString = atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes;
}

/**
 * Derive key from password using PBKDF2
 */
async function deriveKey(password, salt) {
    const encoder = new TextEncoder();
    const passwordBuffer = encoder.encode(password);
    
    const passwordKey = await crypto.subtle.importKey(
        'raw',
        passwordBuffer,
        'PBKDF2',
        false,
        ['deriveKey']
    );
    
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

/**
 * Decrypt content using AES-GCM
 */
async function decryptContent(encryptedData, password) {
    try {
        const parts = encryptedData.split(':');
        if (parts.length !== 3) {
            throw new Error('CORRUPTED_DATA');
        }
        
        const salt = base64ToBytes(parts[0]);
        const nonce = base64ToBytes(parts[1]);
        const ciphertext = base64ToBytes(parts[2]);
        
        if (salt.length !== SALT_SIZE || nonce.length !== NONCE_SIZE) {
            throw new Error('CORRUPTED_DATA');
        }
        
        const key = await deriveKey(password, salt);
        
        const decrypted = await crypto.subtle.decrypt(
            {
                name: 'AES-GCM',
                iv: nonce
            },
            key,
            ciphertext
        );
        
        const decoder = new TextDecoder('utf-8');
        return decoder.decode(decrypted);
        
    } catch (e) {
        if (e.message === 'CORRUPTED_DATA') {
            throw new Error('CORRUPTED_DATA');
        } else {
            throw new Error('WRONG_PASSWORD');
        }
    }
}

/**
 * Test function
 */
async function testDecryption() {
    // Read test data from stdin (will be provided by Python test)
    const testData = JSON.parse(process.argv[2]);
    
    try {
        const decrypted = await decryptContent(testData.encrypted, testData.password);
        
        if (decrypted === testData.original) {
            console.log('SUCCESS: Round-trip encryption works!');
            process.exit(0);
        } else {
            console.error('FAILURE: Decrypted content does not match original');
            console.error('Expected:', testData.original);
            console.error('Got:', decrypted);
            process.exit(1);
        }
    } catch (e) {
        console.error('FAILURE: Decryption failed:', e.message);
        process.exit(1);
    }
}

// Run test
testDecryption();
