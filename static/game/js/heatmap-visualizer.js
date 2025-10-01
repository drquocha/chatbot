class HeatmapVisualizer {
    constructor() {
        this.createHeatmapContainer();
        this.isVisible = false;
    }

    createHeatmapContainer() {
        // Create heatmap overlay
        this.heatmapOverlay = document.createElement('div');
        this.heatmapOverlay.id = 'heatmap-overlay';
        this.heatmapOverlay.className = 'heatmap-overlay hidden';

        this.heatmapOverlay.innerHTML = `
            <div class="heatmap-container">
                <div class="heatmap-header">
                    <h2>📊 Learning Progress Heatmap</h2>
                    <button id="close-heatmap" class="close-button">✕</button>
                </div>
                <div class="heatmap-legend">
                    <div class="legend-item">
                        <div class="legend-color legend-new"></div>
                        <span>New (0% accuracy)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color legend-learning"></div>
                        <span>Learning (1-50%)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color legend-improving"></div>
                        <span>Improving (51-80%)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color legend-mastered"></div>
                        <span>Mastered (81-100%)</span>
                    </div>
                </div>
                <div id="heatmap-grid" class="heatmap-grid"></div>
                <div class="heatmap-stats">
                    <div class="stat-item">
                        <span class="stat-label">Total Words:</span>
                        <span id="total-words-stat">0</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Mastered:</span>
                        <span id="mastered-words-stat">0</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Learning:</span>
                        <span id="learning-words-stat">0</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Average Accuracy:</span>
                        <span id="avg-accuracy-stat">0%</span>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(this.heatmapOverlay);

        // Bind close event
        document.getElementById('close-heatmap').addEventListener('click', () => {
            this.hide();
        });

        // Close on overlay click
        this.heatmapOverlay.addEventListener('click', (e) => {
            if (e.target === this.heatmapOverlay) {
                this.hide();
            }
        });

        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isVisible) {
                this.hide();
            }
        });
    }

    async show(learningClient, dataManager) {
        this.isVisible = true;
        this.heatmapOverlay.classList.remove('hidden');

        // Get learning data
        const analytics = await learningClient.getAnalytics();
        const wordStatesResponse = await learningClient.getWordStates();
        const currentVocab = dataManager.getData();

        // Convert FSRS word states object to array format expected by heatmap
        const wordStatesObject = wordStatesResponse.word_states || {};
        const wordStatesArray = Object.entries(wordStatesObject).map(([wordId, state]) => ({
            word_id: wordId,
            concept: wordId,
            total_reviews: state.repsTotal || 0,
            correct_reviews: state.repsCorrect || 0,
            accuracy: state.repsTotal > 0 ? (state.repsCorrect / state.repsTotal) : 0,
            difficulty: state.difficulty || 0.5,
            stability: state.stability || 1,
            retrievability: state.retrievability || 1,
            state: state.state || 'new',
            lastReviewTime: state.lastReviewTime || 0
        }));

        console.log('🗺️ Heatmap opening - Found stored data for', wordStatesArray.length, 'words');
        console.log('📚 Checking', currentVocab.length, 'vocabulary items for progress');
        if (wordStatesArray.length > 0) {
            console.log('📈 Sample stored data:', {
                concept: wordStatesArray[0].concept,
                repsTotal: wordStatesArray[0].total_reviews,
                accuracy: wordStatesArray[0].accuracy
            });
        }
        this.renderHeatmap(wordStatesArray, currentVocab, analytics);
    }

    hide() {
        this.isVisible = false;
        this.heatmapOverlay.classList.add('hidden');
    }

    renderHeatmap(wordStates, vocabulary, analytics) {
        const heatmapGrid = document.getElementById('heatmap-grid');
        heatmapGrid.innerHTML = '';

        // Check if we have any data to display
        if (vocabulary.length === 0) {
            heatmapGrid.innerHTML = `
                <div class="heatmap-empty">
                    <h3>No vocabulary data available</h3>
                    <p>Start playing the game to see your progress here!</p>
                </div>
            `;
            this.updateStatistics([], analytics);
            return;
        }

        // Create grid container
        const gridContainer = document.createElement('div');
        gridContainer.className = 'heatmap-grid-container';

        // Create word state map for quick lookup
        const wordStateMap = new Map();
        wordStates.forEach(word => {
            wordStateMap.set(word.word_id || word.concept, word);
        });

        // Process each word in vocabulary
        const processedWords = vocabulary.map(vocabWord => {
            const wordState = wordStateMap.get(vocabWord.concept);

            if (!wordState || wordState.total_reviews === 0) {
                return {
                    concept: vocabWord.concept,
                    definition: vocabWord.definition,
                    accuracy: 0,
                    total_reviews: 0,
                    correct_reviews: 0,
                    difficulty: 0.5,
                    stability: 1,
                    category: 'new'
                };
            }

            const accuracy = wordState.total_reviews > 0 ? (wordState.correct_reviews / wordState.total_reviews) : 0;
            let category = 'new';

            if (accuracy > 0.8) category = 'mastered';
            else if (accuracy > 0.5) category = 'improving';
            else if (accuracy > 0) category = 'learning';

            return {
                concept: vocabWord.concept,
                definition: vocabWord.definition,
                accuracy: accuracy,
                total_reviews: wordState.total_reviews || 0,
                correct_reviews: wordState.correct_reviews || 0,
                difficulty: wordState.difficulty || 0.5,
                stability: wordState.stability || 1,
                category: category
            };
        });

        // Sort by accuracy (lowest first to prioritize struggling words)
        processedWords.sort((a, b) => a.accuracy - b.accuracy);

        // Debug summary
        const wordsWithData = processedWords.filter(w => w.total_reviews > 0);
        console.log('📊 Heatmap processing summary:', {
            totalWords: processedWords.length,
            wordsWithProgress: wordsWithData.length,
            sampleWordWithProgress: wordsWithData[0] || null
        });

        // Create heatmap cells
        processedWords.forEach((word, index) => {
            const cell = document.createElement('div');
            cell.className = `heatmap-cell heatmap-${word.category}`;

            // Create tooltip content
            const tooltipContent = `
                ${word.concept}<br>
                Accuracy: ${(word.accuracy * 100).toFixed(1)}%<br>
                Reviews: ${word.correct_reviews}/${word.total_reviews}<br>
                Difficulty: ${(word.difficulty * 10).toFixed(1)}/10
            `;

            cell.innerHTML = `
                <div class="cell-concept">${word.concept.substring(0, 8)}${word.concept.length > 8 ? '...' : ''}</div>
                <div class="cell-accuracy">${(word.accuracy * 100).toFixed(0)}%</div>
                <div class="cell-tooltip">${tooltipContent}</div>
            `;

            gridContainer.appendChild(cell);
        });

        heatmapGrid.appendChild(gridContainer);

        // Update statistics
        this.updateStatistics(processedWords, analytics);
    }

    updateStatistics(processedWords, analytics) {
        const stats = {
            total: processedWords.length,
            mastered: processedWords.filter(w => w.category === 'mastered').length,
            improving: processedWords.filter(w => w.category === 'improving').length,
            learning: processedWords.filter(w => w.category === 'learning').length,
            new: processedWords.filter(w => w.category === 'new').length
        };

        const avgAccuracy = processedWords.length > 0
            ? processedWords.reduce((sum, w) => sum + w.accuracy, 0) / processedWords.length
            : 0;

        document.getElementById('total-words-stat').textContent = stats.total;
        document.getElementById('mastered-words-stat').textContent = stats.mastered;
        document.getElementById('learning-words-stat').textContent = stats.learning + stats.improving;
        document.getElementById('avg-accuracy-stat').textContent = `${(avgAccuracy * 100).toFixed(1)}%`;
    }
}

