import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import {
    encryptData,
    decryptData,
    deriveKeyFromPassword
} from './crypto';

export const useBankStore = defineStore('bank', () => {

    const baseState = ref({
        accounts: [
            { id: 'a1', name: 'Checking', balance: 1250.77 },
            { id: 'a2', name: 'Savings', balance: 5800.00 },
        ],
        loans: [],
        lastUpdated: null,
    });

    const stagedTransactions = ref([]);
    const committedTransactions = ref([]);

    // --- NEW MFA STATE ---
    // This authorizes the "git push" (upload)
    const mfaToken = ref(null);
    const mfaTokenExpiry = ref(null);

    const sessionKey = ref(null); // In-memory encryption key
    const isLoading = ref(false); // Changed to false so UI renders immediately with mock data
    const syncError = ref(null);

    // A new state to signal the UI
    const isMfaRequired = ref(false);

    // --- GETTERS (Computed Properties) ---

    const projectedState = computed(() => {
        const projected = JSON.parse(JSON.stringify(baseState.value));
        for (const tx of stagedTransactions.value) {
            applyTransaction(projected, tx);
        }
        return projected;
    });

    // --- ACTIONS (Methods) ---

    function applyTransaction(state, tx) {
        if (tx.type === 'TRANSFER') {
            const fromAccount = state.accounts.find(a => a.id === tx.from);
            const toAccount = state.accounts.find(a => a.id === tx.to);
            if (fromAccount) fromAccount.balance -= tx.amount;
            if (toAccount) toAccount.balance += tx.amount;
        } else if (tx.type === 'LOAN_ORDER') {
            state.loans.push({
                id: tx.id,
                amount: tx.amount,
                principal: tx.amount, // Adding more detail
                term: tx.term,
                status: 'PENDING',
            });
        }
    }

    async function initializeSession(password) {
        try {
            console.log('🔐 Initializing bank session...');
            isLoading.value = true;
            sessionKey.value = await deriveKeyFromPassword(password);
            console.log('✓ Session key derived');

            // Load all encrypted data first
            await loadEncryptedData();
            console.log('✓ Encrypted data loaded');

            // Then fetch base state from backend
            await fetchBaseState();
            console.log('✓ Base state fetched');

            isLoading.value = false;
            // Start the upload worker
            triggerUploadWorker();
            console.log('✓ Bank session initialized successfully');
        } catch (err) {
            console.error("Initialization failed:", err);
            isLoading.value = false;
            throw err; // Re-throw so caller knows initialization failed
        }
    }

    async function fetchBaseState() {
        // const newState = await api.fetchBackendState();
        // mock for hackathon
        const newState = {
            accounts: [
                { id: 'a1', name: 'Checking', balance: 1250.77 },
                { id: 'a2', name: 'Savings', balance: 5800.00 },
            ],
            loans: [],
            lastUpdated: new Date().toISOString(),
        };

        baseState.value = newState;
        await saveEncryptedState();
    }

    async function addTransactionToStage(tx) {
        const newTx = { ...tx, id: crypto.randomUUID(), timestamp: Date.now() };
        console.log('Adding transaction to stage:', newTx);
        stagedTransactions.value.push(newTx);
        console.log('Total staged transactions:', stagedTransactions.value.length);
        await saveEncryptedQueues();
    }

    /**
     * NEW ACTION: Called by Review view after face verification
     */
    async function commitAndAuthorizeStagedChanges(token, expiry) {
        // 1. Store the new MFA token
        mfaToken.value = token;
        mfaTokenExpiry.value = expiry;
        isMfaRequired.value = false; // We just got it
        await saveEncryptedMfaToken(); // Persist it

        // 2. Move all staged transactions to the committed queue
        committedTransactions.value.push(...stagedTransactions.value);
        stagedTransactions.value = [];

        // 3. Save the queues
        await saveEncryptedQueues();

        // 4. Wake up the upload worker
        triggerUploadWorker();
    }

    async function discardStagedChanges() {
        stagedTransactions.value = [];
        await saveEncryptedQueues();
    }

    // --- ENCRYPTION & PERSISTENCE ---

    async function saveEncryptedQueues() {
        if (!sessionKey.value) {
            console.warn('Cannot save queues: sessionKey not set');
            return;
        }
        try {
            console.log('Saving staged transactions:', stagedTransactions.value.length);
            const stagedData = await encryptData(JSON.stringify(stagedTransactions.value), sessionKey.value);
            localStorage.setItem('STAGED_TX_QUEUE', stagedData);
            console.log('✓ Saved STAGED_TX_QUEUE to localStorage');

            console.log('Saving committed transactions:', committedTransactions.value.length);
            const committedData = await encryptData(JSON.stringify(committedTransactions.value), sessionKey.value);
            localStorage.setItem('COMMITTED_TX_QUEUE', committedData);
            console.log('✓ Saved COMMITTED_TX_QUEUE to localStorage');
        } catch (err) {
            console.error("Failed to save queues:", err);
        }
    }

    async function saveEncryptedState() {
        if (!sessionKey.value) return;
        try {
            const stateData = await encryptData(JSON.stringify(baseState.value), sessionKey.value);
            localStorage.setItem('BASE_STATE', stateData);
        } catch (err) { console.error("Failed to save base state:", err); }
    }

    async function saveEncryptedMfaToken() {
        if (!sessionKey.value) return;
        try {
            const tokenData = {
                token: mfaToken.value,
                expiry: mfaTokenExpiry.value
            };
            const encryptedToken = await encryptData(JSON.stringify(tokenData), sessionKey.value);
            localStorage.setItem('MFA_TOKEN', encryptedToken);
        } catch (err) { console.error("Failed to save MFA token:", err); }
    }

    /**
     * NEW: Loads all encrypted data at once.
     */
    async function loadEncryptedData() {
        if (!sessionKey.value) return;

        try {
            // Load Queues
            const encryptedStaged = localStorage.getItem('STAGED_TX_QUEUE');
            if (encryptedStaged) {
                const decrypted = await decryptData(encryptedStaged, sessionKey.value);
                stagedTransactions.value = JSON.parse(decrypted);
            } else {
                stagedTransactions.value = []; // Ensure it's an array
            }

            const encryptedCommitted = localStorage.getItem('COMMITTED_TX_QUEUE');
            if (encryptedCommitted) {
                const decrypted = await decryptData(encryptedCommitted, sessionKey.value);
                committedTransactions.value = JSON.parse(decrypted);
            } else {
                committedTransactions.value = []; // Ensure it's an array
            }

            // Load Base State if exists
            const encryptedState = localStorage.getItem('BASE_STATE');
            if (encryptedState) {
                const decrypted = await decryptData(encryptedState, sessionKey.value);
                baseState.value = JSON.parse(decrypted);
            }

            // Load MFA Token
            const encryptedToken = localStorage.getItem('MFA_TOKEN');
            if (encryptedToken) {
                const tokenData = JSON.parse(await decryptData(encryptedToken, sessionKey.value));
                // Check if token is expired
                if (new Date(tokenData.expiry) > new Date()) {
                    mfaToken.value = tokenData.token;
                    mfaTokenExpiry.value = tokenData.expiry;
                } else {
                    // Token is expired, clear it
                    await clearMfaToken();
                }
            }

        } catch (err) {
            console.error("Failed to load/decrypt data:", err);
            // This will fail if the password is wrong. Clear everything.
            localStorage.removeItem('STAGED_TX_QUEUE');
            localStorage.removeItem('COMMITTED_TX_QUEUE');
            localStorage.removeItem('BASE_STATE');
            localStorage.removeItem('MFA_TOKEN');
            throw new Error("Decryption failed. Invalid password or tampered data.");
        }
    }

    async function clearMfaToken() {
        mfaToken.value = null;
        mfaTokenExpiry.value = null;
        localStorage.removeItem('MFA_TOKEN');
    }

    /**
     * Check if there's encrypted data in localStorage
     */
    function hasEncryptedData() {
        return !!(localStorage.getItem('STAGED_TX_QUEUE') ||
                 localStorage.getItem('COMMITTED_TX_QUEUE') ||
                 localStorage.getItem('BASE_STATE'));
    }

    // --- UPLOAD WORKER ("Git Push") ---

    let isWorkerRunning = false;

    function triggerUploadWorker() {
        if (isWorkerRunning) return;
        isWorkerRunning = true;
        _uploadQueue(); // Fire and forget
    }

    async function _uploadQueue() {
        // 1. Check for connection
        if (!navigator.onLine) {
            isWorkerRunning = false;
            return; // Offline, stop
        }

        // 2. Check for items
        if (committedTransactions.value.length === 0) {
            isWorkerRunning = false;
            return; // Queue empty, stop
        }

        // 3. --- NEW MFA CHECK ---
        if (!mfaToken.value || new Date(mfaTokenExpiry.value) <= new Date()) {
            // We have items to push, but no valid MFA token!
            isMfaRequired.value = true; // Signal UI to prompt for 2FA
            isWorkerRunning = false;
            syncError.value = "Face Verification required to sync changes.";
            await clearMfaToken(); // Clear expired token
            return; // Stop
        }

        // --- We are online, have items, and have a valid token ---
        isWorkerRunning = true;
        isMfaRequired.value = false;

        const txToUpload = committedTransactions.value[0];

        try {
            syncError.value = null;

            // MOCK API CALL - This must match your new backend endpoint
            // const response = await api.submitTransaction(txToUpload, mfaToken.value);
            const response = await fetch('/api/submit-transaction', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${mfaToken.value}` // Send the token
                },
                body: JSON.stringify(txToUpload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                // Handle specific MFA errors
                if (response.status === 401) {
                    syncError.value = `Sync failed: ${errorData.message}`;
                    isMfaRequired.value = true; // Token was rejected, need a new one
                    await clearMfaToken();
                    isWorkerRunning = false;
                    return; // Stop worker
                }
                throw new Error(errorData.message || 'Upload failed');
            }

            // SUCCESS!
            committedTransactions.value.shift();
            await saveEncryptedQueues();
            await fetchBaseState(); // "git pull" after "push"

            // Recurse to process the next item
            // If the queue is now empty, this will stop the worker
            _uploadQueue();

        } catch (err) {
            console.error("Upload failed:", err);
            syncError.value = `Failed to sync transaction ${txToUpload.id}: ${err.message}`;
            isWorkerRunning = false; // Stop on error to avoid spamming
        }
    }

    window.addEventListener('online', triggerUploadWorker);

    return {
        baseState,
        stagedTransactions,
        committedTransactions,
        isLoading,
        syncError,
        projectedState,
        isMfaRequired, // Expose this
        initializeSession,
        addTransactionToStage,
        commitAndAuthorizeStagedChanges, // Expose the new action
        discardStagedChanges,
        fetchBaseState,
        triggerUploadWorker, // Allow UI to trigger a sync check
        hasEncryptedData // Allow checking for encrypted data
    };
});