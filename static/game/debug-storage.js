// Simple localStorage debugger - paste in browser console
console.log('🔍 FSRS Storage Debug Check');
console.log('');

// Check what's in localStorage
const fsrsData = localStorage.getItem('fsrs_word_states');
console.log('📦 Raw FSRS data in localStorage:', fsrsData);

if (fsrsData) {
    const parsed = JSON.parse(fsrsData);
    console.log('📊 Parsed FSRS data:', parsed);
    console.log('🔢 Number of words with data:', Object.keys(parsed).length);

    // Show details for each word
    Object.entries(parsed).forEach(([word, state]) => {
        console.log(`  📝 ${word}:`, {
            repsTotal: state.repsTotal,
            repsCorrect: state.repsCorrect,
            accuracy: state.repsTotal > 0 ? (state.repsCorrect / state.repsTotal * 100).toFixed(1) + '%' : '0%'
        });
    });
} else {
    console.log('❌ No FSRS data found in localStorage');
    console.log('💡 Try playing the game first, then run this check again');
}

console.log('');
console.log('🎮 To test: Play a few rounds, then run this debug script again');
console.log('🗺️ Then open the heatmap to see if it shows the progress');