// Quick heatmap data flow test - paste in browser console after game loads

console.log('🧪 Quick Heatmap Data Flow Test');
console.log('');

// Wait for game to load
setTimeout(() => {
    const game = window.vocabularyGame;
    if (!game) {
        console.error('❌ Game not found. Make sure page is loaded.');
        return;
    }

    console.log('✅ Game found:', typeof game);

    // Test the complete data flow
    console.log('1. Testing recordResponse directly...');

    // Simulate a correct response
    game.learningClient.recordResponse('TestWord', true, 2500, false)
        .then(() => {
            console.log('2. Response recorded, checking localStorage...');

            // Check localStorage directly
            const rawData = localStorage.getItem('fsrs_word_states');
            console.log('📦 Raw localStorage:', rawData ? 'exists' : 'null');

            if (rawData) {
                const parsed = JSON.parse(rawData);
                console.log('📊 Parsed data:', parsed);
                console.log('🔢 Words in storage:', Object.keys(parsed).length);

                if (parsed.TestWord) {
                    console.log('✅ TestWord found:', {
                        repsTotal: parsed.TestWord.repsTotal,
                        repsCorrect: parsed.TestWord.repsCorrect,
                        accuracy: parsed.TestWord.repsTotal > 0 ? (parsed.TestWord.repsCorrect / parsed.TestWord.repsTotal * 100).toFixed(1) + '%' : '0%'
                    });

                    console.log('3. Testing heatmap data retrieval...');

                    // Test getOfflineWordStates
                    const wordStatesResult = game.learningClient.getOfflineWordStates();
                    console.log('🗂️ getOfflineWordStates result:', wordStatesResult);

                    // Test heatmap data conversion
                    const wordStatesObject = wordStatesResult.word_states || {};
                    const wordStatesArray = Object.entries(wordStatesObject).map(([wordId, state]) => ({
                        word_id: wordId,
                        concept: wordId,
                        total_reviews: state.repsTotal || 0,
                        correct_reviews: state.repsCorrect || 0,
                        accuracy: state.repsTotal > 0 ? (state.repsCorrect / state.repsTotal) : 0,
                        state: state.state || 'new'
                    }));

                    console.log('🗺️ Converted heatmap data:', wordStatesArray);

                    if (wordStatesArray.length > 0 && wordStatesArray[0].accuracy > 0) {
                        console.log('✅ Data flow works! Accuracy calculated:', (wordStatesArray[0].accuracy * 100).toFixed(1) + '%');
                    } else {
                        console.log('❌ Issue found: accuracy is 0 despite data existing');
                    }
                } else {
                    console.log('❌ TestWord not found in localStorage');
                }
            }
        })
        .catch(error => {
            console.error('❌ Error in recordResponse:', error);
        });

}, 2000);

console.log('⏳ Starting test in 2 seconds...');