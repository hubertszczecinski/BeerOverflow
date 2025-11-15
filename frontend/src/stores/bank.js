import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import {
    encryptData,
    decryptData,
    deriveKeyFromPassword
} from './crypto';

export const useBankStore = defineStore('bank', () => {

    // Simple FX rates to USD (rough, hard-coded approximations)
    // 1 unit of CURRENCY = rate USD
    const FX_TO_USD = {
        USD: 1.0,
        EUR: 1.08,
        GBP: 1.25,
        JPY: 0.0067,
        CHF: 1.10,
        PLN: 0.25,
        CZK: 0.044
    };

    // Backend-driven state
    const accounts = ref([]);
    const transactions = ref([]);
    const lastUpdated = ref(null);

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

    const projectedAccounts = computed(() => {
        // Clone accounts and apply staged transactions
        const projected = JSON.parse(JSON.stringify(accounts.value));
        for (const tx of stagedTransactions.value) {
            applyTransactionToAccounts(projected, tx);
        }
        return projected;
    });

    function toUsd(amount, currency = 'USD') {
        const rate = FX_TO_USD[currency?.toUpperCase?.()] ?? 1.0;
        const val = typeof amount === 'number' ? amount : parseFloat(amount || 0);
        return val * rate;
    }

    const totalBalance = computed(() => {
        return accounts.value.reduce((sum, acc) => sum + toUsd(acc.balance, acc.currency), 0);
    });

    const projectedTotalBalance = computed(() => {
        return projectedAccounts.value.reduce((sum, acc) => sum + toUsd(acc.balance, acc.currency), 0);
    });

    // --- ACTIONS (Methods) ---

    function applyTransactionToAccounts(accountsList, tx) {
        if (tx.type === 'TRANSFER' || tx.type === 'transfer') {
            const fromAccount = accountsList.find(a => a.id === tx.from || a.id === tx.from_account_id);
            const toAccount = accountsList.find(a => a.id === tx.to || a.id === tx.to_account_id);
            if (fromAccount) fromAccount.balance -= tx.amount;
            if (toAccount) toAccount.balance += tx.amount;
        } else if (tx.type === 'debit') {
            const account = accountsList.find(a => a.id === tx.account_id);
            if (account) account.balance -= tx.amount;
        } else if (tx.type === 'credit') {
            const account = accountsList.find(a => a.id === tx.account_id);
            if (account) account.balance += tx.amount;
        } else if (tx.type === 'CREATE_ACCOUNT') {
            // Add a placeholder account for projection
            accountsList.push({
                id: `pending_${tx.id}`,
                account_type: tx.account_type,
                account_number: 'PENDING',
                balance: tx.initial_balance || 0,
                currency: tx.currency || 'USD',
                is_active: true,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
                _isPending: true
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
        try {
            const response = await fetch('/api/accounts', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error('Failed to fetch accounts');
            }

            const data = await response.json();
            accounts.value = data.accounts || [];
            lastUpdated.value = new Date().toISOString();
            await saveEncryptedState();
        } catch (err) {
            console.error('Failed to fetch base state:', err);
            throw err;
        }
    }

    async function fetchAccountTransactions(accountId) {
        try {
            const response = await fetch(`/api/accounts/${accountId}/transactions`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error('Failed to fetch transactions');
            }

            const data = await response.json();
            return data.transactions || [];
        } catch (err) {
            console.error('Failed to fetch transactions:', err);
            throw err;
        }
    }

    async function createAccount(accountType, currency = 'USD', initialBalance = 0) {
        if (!mfaToken.value || new Date(mfaTokenExpiry.value) <= new Date()) {
            isMfaRequired.value = true;
            throw new Error('MFA token required');
        }

        try {
            const response = await fetch('/api/accounts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${mfaToken.value}`
                },
                credentials: 'include',
                body: JSON.stringify({
                    account_type: accountType,
                    currency,
                    initial_balance: initialBalance
                })
            });

            if (!response.ok) {
                if (response.status === 401) {
                    isMfaRequired.value = true;
                    await clearMfaToken();
                }
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to create account');
            }

            const data = await response.json();
            await fetchBaseState(); // Refresh accounts
            return data.account;
        } catch (err) {
            console.error('Failed to create account:', err);
            throw err;
        }
    }

    async function createTransaction(accountId, amount, transactionType, description, channel = 'web', recipientId = null, location = null) {
        if (!mfaToken.value || new Date(mfaTokenExpiry.value) <= new Date()) {
            isMfaRequired.value = true;
            throw new Error('MFA token required');
        }

        try {
            const response = await fetch(`/api/accounts/${accountId}/transactions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${mfaToken.value}`
                },
                credentials: 'include',
                body: JSON.stringify({
                    amount,
                    transaction_type: transactionType,
                    description,
                    channel,
                    recipient_id: recipientId,
                    location
                })
            });

            if (!response.ok) {
                if (response.status === 401) {
                    isMfaRequired.value = true;
                    await clearMfaToken();
                }
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to create transaction');
            }

            const data = await response.json();
            return data.transaction;
        } catch (err) {
            console.error('Failed to create transaction:', err);
            throw err;
        }
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
            const stateData = await encryptData(JSON.stringify({
                accounts: accounts.value,
                lastUpdated: lastUpdated.value
            }), sessionKey.value);
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
                const state = JSON.parse(decrypted);
                accounts.value = state.accounts || [];
                lastUpdated.value = state.lastUpdated;
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

            let response;

            // Handle different transaction types with appropriate API endpoints
            if (txToUpload.type === 'CREATE_ACCOUNT') {
                // Create account via accounts endpoint
                response = await fetch('/api/accounts', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${mfaToken.value}`
                    },
                    credentials: 'include',
                    body: JSON.stringify({
                        account_type: txToUpload.account_type,
                        currency: txToUpload.currency,
                        initial_balance: txToUpload.initial_balance || 0
                    })
                });
            } else {
                // Default transaction submission
                response = await fetch('/api/submit-transaction', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${mfaToken.value}`
                    },
                    credentials: 'include',
                    body: JSON.stringify(txToUpload)
                });
            }

            if (!response.ok) {
                let message = 'Upload failed';
                try {
                    const ct = response.headers.get('content-type') || '';
                    const errorData = ct.includes('application/json') ? await response.json() : { message: await response.text() };
                    if (response.status === 401) {
                        syncError.value = `Sync failed: ${errorData.message}`;
                        isMfaRequired.value = true; // Token was rejected, need a new one
                        await clearMfaToken();
                        isWorkerRunning = false;
                        return; // Stop worker
                    }
                    message = errorData.message || message;
                } catch {}
                throw new Error(message);
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
        accounts,
        transactions,
        lastUpdated,
        stagedTransactions,
        committedTransactions,
        isLoading,
        syncError,
        projectedAccounts,
        totalBalance,
        projectedTotalBalance,
        isMfaRequired, // Expose this
        initializeSession,
        fetchBaseState,
        fetchAccountTransactions,
        createAccount,
        createTransaction,
        addTransactionToStage,
        commitAndAuthorizeStagedChanges, // Expose the new action
        discardStagedChanges,
        triggerUploadWorker, // Allow UI to trigger a sync check
        hasEncryptedData // Allow checking for encrypted data
    };
});
