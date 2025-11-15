// --- CONFIGURATION ---
const SALT = "super-secure-salt-for-hackathon"; // In prod, this should be unique per-user
const ITERATIONS = 100000; // PBKDF2 iterations
const KEY_ALGORITHM = "PBKDF2";
const HASH_ALGORITHM = "SHA-256";
const ENCRYPT_ALGORITHM = "AES-GCM";
const KEY_LENGTH = 256;

/**
 * Derives a 256-bit AES key from a user's password.
 * @param {string} password - The user's password.
 * @returns {Promise<CryptoKey>} - A key for AES-GCM encryption.
 */
export async function deriveKeyFromPassword(password) {
    const enc = new TextEncoder();
    const passwordBuffer = enc.encode(password);

    // Import the password as a "raw" key
    const importedKey = await crypto.subtle.importKey(
        "raw",
        passwordBuffer,
        KEY_ALGORITHM,
        false,
        ["deriveKey"]
    );

    // Derive the actual encryption key
    const saltBuffer = enc.encode(SALT);
    const derivedKey = await crypto.subtle.deriveKey(
        {
            name: KEY_ALGORITHM,
            salt: saltBuffer,
            iterations: ITERATIONS,
            hash: HASH_ALGORITHM,
        },
        importedKey,
        { name: ENCRYPT_ALGORITHM, length: KEY_LENGTH },
        true, // extractable
        ["encrypt", "decrypt"] // key usages
    );

    return derivedKey;
}

/**
 * Encrypts a plaintext string using the derived key.
 * Uses AES-GCM for authenticated encryption.
 * @param {string} plaintext - The data to encrypt (e.g., JSON string).
 * @param {CryptoKey} key - The key from deriveKeyFromPassword.
 * @returns {Promise<string>} - A base64 string containing (iv + ciphertext).
 */
export async function encryptData(plaintext, key) {
    const enc = new TextEncoder();
    const dataBuffer = enc.encode(plaintext);

    // Generate a random 12-byte Initialization Vector (IV)
    const iv = crypto.getRandomValues(new Uint8Array(12));

    const encryptedBuffer = await crypto.subtle.encrypt(
        {
            name: ENCRYPT_ALGORITHM,
            iv: iv,
        },
        key,
        dataBuffer
    );

    // Combine IV and ciphertext into one buffer
    // We store iv (12 bytes) + ciphertext
    const ivAndCiphertext = new Uint8Array(iv.length + encryptedBuffer.byteLength);
    ivAndCiphertext.set(iv, 0);
    ivAndCiphertext.set(new Uint8Array(encryptedBuffer), iv.length);

    // Convert to base64 to store in LocalStorage
    return btoa(String.fromCharCode.apply(null, ivAndCiphertext));
}

/**
 * Decrypts a base64 string using the derived key.
 * @param {string} base64EncryptedData - The base64 string (iv + ciphertext).
 * @param {CryptoKey} key - The key from deriveKeyFromPassword.
 * @returns {Promise<string>} - The original plaintext.
 */
export async function decryptData(base64EncryptedData, key) {
    // Convert base64 back to Uint8Array
    const binaryData = atob(base64EncryptedData);
    const dataBuffer = new Uint8Array(binaryData.length);
    for (let i = 0; i < binaryData.length; i++) {
        dataBuffer[i] = binaryData.charCodeAt(i);
    }

    // Extract the IV (first 12 bytes)
    const iv = dataBuffer.slice(0, 12);

    // Extract the ciphertext
    const ciphertext = dataBuffer.slice(12);

    const decryptedBuffer = await crypto.subtle.decrypt(
        {
            name: ENCRYPT_ALGORITHM,
            iv: iv,
        },
        key,
        ciphertext
    );

    // Decode the buffer back to a string
    const dec = new TextDecoder();
    return dec.decode(decryptedBuffer);
}