/**
 * Negative cryptographic fixture in JavaScript.
 * Mentions crypto concepts in comments only.
 */

function formatUserKey(userId, keyPrefix) {
    // Variable name contains 'key', but no cryptographic algorithm is used
    // This function formats a composite cache key
    const cacheKey = `${keyPrefix}_user_${userId}`;
    return cacheKey.toLowerCase();
}

function calculateSum(numbers) {
    // Pure arithmetic
    return numbers.reduce((acc, curr) => acc + curr, 0);
}

module.exports = { formatUserKey, calculateSum };
