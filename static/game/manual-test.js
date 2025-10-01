// Manual test to simulate the exact game flow
// Paste this in browser console after page loads

console.log('🧪 Manual FSRS Test Starting...');

// Wait for game to be initialized
setTimeout(() => {
    console.log('📝 Testing direct FSRS operations...');

    // Get the actual game instance
    const game = window.vocabularyGame || document.vocabularyGame;
    if (!game) {
        console.error('❌ Game instance not found. Make sure page is fully loaded.');
        return;
    }

    // Test 1: Manually call recordResponse
    console.log('🎯 Test 1: Manual recordResponse call');
    game.learningClient.recordResponse('Photosynthesis', true, 2500, false)
        .then(() => {
            console.log('✅ recordResponse completed');

            // Check localStorage immediately
            const stored = JSON.parse(localStorage.getItem('fsrs_word_states') || '{}');
            console.log('💾 localStorage after manual record:', stored);

            if (stored['Photosynthesis']) {
                console.log('✅ Found Photosynthesis data:', stored['Photosynthesis']);

                // Test 2: Check heatmap data retrieval
                console.log('🗺️ Test 2: Check heatmap data retrieval');
                const heatmapData = game.learningClient.getOfflineWordStates();
                console.log('📊 Heatmap data:', heatmapData);

            } else {
                console.error('❌ Photosynthesis data not found in localStorage!');
            }
        })
        .catch(error => {
            console.error('❌ recordResponse failed:', error);
        });

}, 2000);

// Store reference to game for debugging
setTimeout(() => {
    if (window.vocabularyGame || document.vocabularyGame) {
        window.testGame = window.vocabularyGame || document.vocabularyGame;
        console.log('✅ Game reference stored as window.testGame');
    }
}, 1000);