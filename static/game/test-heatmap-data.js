// Test script to manually add FSRS data for heatmap testing
// Open browser console and paste this to test heatmap with fake data

console.log('🧪 Creating test FSRS data...');

const testFSRSData = {
    "Photosynthesis": {
        wordId: "Photosynthesis",
        state: "review",
        stability: 5.2,
        difficulty: 0.4,
        retrievability: 0.85,
        repsTotal: 8,
        repsCorrect: 6,
        streakCorrect: 2,
        lapseCount: 2,
        lastResponseQuality: 2,
        avgResponseTime: 3500,
        lastResponseTime: 2800,
        hintUsedCount: 1,
        createdTime: Date.now() - (7 * 24 * 60 * 60 * 1000), // 7 days ago
        lastReviewTime: Date.now() - (2 * 60 * 60 * 1000), // 2 hours ago
        nextDueTime: Date.now() + (24 * 60 * 60 * 1000), // tomorrow
        interval: 86400000,
        uncertainty: 0.3,
        priority: 2.5,
        lastUpdated: Date.now()
    },
    "Democracy": {
        wordId: "Democracy",
        state: "learning",
        stability: 1.8,
        difficulty: 0.6,
        retrievability: 0.65,
        repsTotal: 4,
        repsCorrect: 2,
        streakCorrect: 0,
        lapseCount: 2,
        lastResponseQuality: 0,
        avgResponseTime: 5200,
        lastResponseTime: 6100,
        hintUsedCount: 3,
        createdTime: Date.now() - (3 * 24 * 60 * 60 * 1000), // 3 days ago
        lastReviewTime: Date.now() - (30 * 60 * 1000), // 30 min ago
        nextDueTime: Date.now() + (10 * 60 * 1000), // 10 min from now
        interval: 600000,
        uncertainty: 0.7,
        priority: 8.2,
        lastUpdated: Date.now()
    },
    "Algorithm": {
        wordId: "Algorithm",
        state: "review",
        stability: 12.5,
        difficulty: 0.2,
        retrievability: 0.95,
        repsTotal: 15,
        repsCorrect: 14,
        streakCorrect: 8,
        lapseCount: 1,
        lastResponseQuality: 3,
        avgResponseTime: 1800,
        lastResponseTime: 1200,
        hintUsedCount: 0,
        createdTime: Date.now() - (14 * 24 * 60 * 60 * 1000), // 14 days ago
        lastReviewTime: Date.now() - (5 * 24 * 60 * 60 * 1000), // 5 days ago
        nextDueTime: Date.now() + (7 * 24 * 60 * 60 * 1000), // 7 days from now
        interval: 604800000,
        uncertainty: 0.1,
        priority: 0.8,
        lastUpdated: Date.now()
    }
};

localStorage.setItem('fsrs_word_states', JSON.stringify(testFSRSData));

console.log('✅ Test data added to localStorage');
console.log('📊 Test data summary:');
console.log('  - Photosynthesis: 75% accuracy (6/8 correct)');
console.log('  - Democracy: 50% accuracy (2/4 correct)');
console.log('  - Algorithm: 93% accuracy (14/15 correct)');
console.log('');
console.log('🗺️ Now open the heatmap to see if it displays this test data correctly!');

// Auto-refresh page to ensure clean state
setTimeout(() => {
    console.log('🔄 Refreshing page...');
    location.reload();
}, 1000);