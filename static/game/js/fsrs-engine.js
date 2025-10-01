/* =============================================================================
   FSRS (Free Spaced Repetition Scheduler) ENGINE
   ========================================================================== */

/**
 * Response quality levels for FSRS algorithm
 */
const ResponseQuality = {
    FAIL: 0,        // Wrong answer
    HARD: 1,        // Correct but struggled (slow RT, used hints)
    GOOD: 2,        // Correct with normal effort
    EASY: 3         // Correct and fast
};

/**
 * Word learning states
 */
const WordState = {
    NEW: 'new',
    LEARNING: 'learning',
    REVIEW: 'review'
};

/**
 * FSRS Engine - Complete offline implementation of FSRS algorithm
 */
class FSRSEngine {
    constructor() {
        // FSRS Parameters (scientifically optimized)
        this.fsrsParams = {
            // FSRS v4 weights (17 parameters)
            w: [0.4, 0.6, 2.4, 5.8, 4.93, 0.94, 0.86, 0.01, 1.49, 0.14, 0.94, 2.18, 0.05, 0.34, 1.26, 0.29, 2.61],
            retentionRate: 0.85,     // Target retention rate (85%)
            maxInterval: 36500,      // Max interval in days (~100 years)
            learningSteps: [1, 10],  // Learning steps in minutes
            graduatingInterval: 1,   // Days to graduate from learning
            easyInterval: 4          // Days for easy response
        };

        // Exploration parameters for intelligent selection
        this.explorationRate = 0.1;        // ε for ε-greedy exploration
        this.uncertaintyWeight = 0.2;      // Weight for uncertainty in selection

        // Data logging system
        this.dataLogger = new FSRSDataLogger();

        // Initialize storage
        this.initializeStorage();
    }

    /**
     * Initialize local storage for FSRS data
     */
    initializeStorage() {
        const existingData = localStorage.getItem('fsrs_word_states');
        if (!existingData) {
            localStorage.setItem('fsrs_word_states', JSON.stringify({}));
        }

        const existingLogs = localStorage.getItem('fsrs_learning_logs');
        if (!existingLogs) {
            localStorage.setItem('fsrs_learning_logs', JSON.stringify([]));
        }
    }

    /**
     * Get or create word state for a given word
     */
    getWordState(wordId) {
        const wordStates = JSON.parse(localStorage.getItem('fsrs_word_states') || '{}');

        if (!wordStates[wordId]) {
            // Create new word state
            wordStates[wordId] = this.createNewWordState(wordId);
            localStorage.setItem('fsrs_word_states', JSON.stringify(wordStates));
        }

        return wordStates[wordId];
    }

    /**
     * Create initial state for a new word
     */
    createNewWordState(wordId) {
        const now = Date.now();
        return {
            wordId: wordId,
            state: WordState.NEW,
            stability: 0.0,
            difficulty: 0.3,        // Initial difficulty (0-1, higher = harder)
            retrievability: 1.0,    // Current retrievability (0-1)
            repsTotal: 0,
            repsCorrect: 0,
            streakCorrect: 0,
            lapseCount: 0,
            lastResponseQuality: ResponseQuality.GOOD,
            avgResponseTime: 0,
            lastResponseTime: 0,
            hintUsedCount: 0,
            createdTime: now,
            lastReviewTime: 0,
            nextDueTime: now,       // Available immediately for new words
            interval: 0,
            uncertainty: 1.0,       // High uncertainty for new words (0-1)
            priority: 0.0,
            lastUpdated: now
        };
    }

    /**
     * Update word state after a review/practice
     */
    updateWordState(wordId, isCorrect, responseTimeMs, usedHint = false) {
        const wordState = this.getWordState(wordId);
        const currentTime = Date.now();

        // Determine response quality based on performance
        let responseQuality = this.determineResponseQuality(
            isCorrect, responseTimeMs, usedHint, wordState
        );

        // Log the review for data analysis
        this.dataLogger.logReview(wordId, wordState, responseQuality, responseTimeMs, usedHint);

        // Update basic statistics
        wordState.repsTotal += 1;
        wordState.lastResponseTime = responseTimeMs;
        wordState.lastReviewTime = currentTime;
        wordState.lastUpdated = currentTime;

        // Update response time average
        if (wordState.avgResponseTime === 0) {
            wordState.avgResponseTime = responseTimeMs;
        } else {
            const alpha = 0.1; // Learning rate for moving average
            wordState.avgResponseTime = (1 - alpha) * wordState.avgResponseTime + alpha * responseTimeMs;
        }

        // Update hint statistics
        if (usedHint) {
            wordState.hintUsedCount += 1;
        }

        // Update correctness statistics and streaks
        if (isCorrect) {
            wordState.repsCorrect += 1;
            wordState.streakCorrect += 1;
        } else {
            wordState.streakCorrect = 0;
            wordState.lapseCount += 1;
        }

        // Apply FSRS algorithm updates
        this.applyFSRSUpdate(wordState, responseQuality, currentTime);

        // Calculate new priority and uncertainty
        this.updateWordPriority(wordState, currentTime);
        this.updateUncertainty(wordState);

        // Save updated state
        this.saveWordState(wordState);

        // Log the update for CSV export
        this.dataLogger.logStateUpdate(wordState, responseQuality);

        return wordState;
    }

    /**
     * Determine response quality based on performance metrics
     */
    determineResponseQuality(isCorrect, responseTimeMs, usedHint, wordState) {
        if (!isCorrect) {
            return ResponseQuality.FAIL;
        }

        let quality = ResponseQuality.GOOD; // Default for correct answers

        // Adjust based on response time
        if (wordState.avgResponseTime > 0) {
            const timeRatio = responseTimeMs / wordState.avgResponseTime;

            if (timeRatio < 0.5) {
                quality = ResponseQuality.EASY; // Very fast
            } else if (timeRatio > 2.0) {
                quality = ResponseQuality.HARD; // Very slow
            }
        }

        // Adjust based on hint usage
        if (usedHint) {
            quality = Math.max(ResponseQuality.FAIL, quality - 1);
        }

        return quality;
    }

    /**
     * Apply FSRS algorithm to update stability, difficulty, and next due time
     */
    applyFSRSUpdate(wordState, responseQuality, currentTime) {
        const w = this.fsrsParams.w;

        // Update difficulty first
        this.updateDifficulty(wordState, responseQuality);

        // Update stability based on current state
        if (wordState.state === WordState.NEW) {
            this.handleNewWord(wordState, responseQuality);
        } else {
            this.handleKnownWord(wordState, responseQuality);
        }

        // Calculate retrievability
        wordState.retrievability = this.calculateRetrievability(wordState, currentTime);

        // Schedule next review
        this.scheduleNextReview(wordState, responseQuality, currentTime);
    }

    /**
     * Update word difficulty based on response quality
     */
    updateDifficulty(wordState, responseQuality) {
        const w = this.fsrsParams.w;

        // Difficulty adjustment based on FSRS formula
        const difficultyAdjustment = w[6] * (responseQuality - 3);
        wordState.difficulty = Math.max(1, Math.min(10, wordState.difficulty + difficultyAdjustment));

        // Normalize to 0-1 range
        wordState.difficulty = (wordState.difficulty - 1) / 9;
    }

    /**
     * Handle new word review
     */
    handleNewWord(wordState, responseQuality) {
        const w = this.fsrsParams.w;

        if (responseQuality === ResponseQuality.FAIL) {
            wordState.stability = w[0]; // Very short stability
            wordState.state = WordState.NEW;
        } else {
            // Calculate initial stability for correct responses
            wordState.stability = w[0] + w[1] * (responseQuality - 1);
            wordState.state = WordState.LEARNING;
        }
    }

    /**
     * Handle known word review
     */
    handleKnownWord(wordState, responseQuality) {
        const w = this.fsrsParams.w;

        // Calculate stability increment/decrement
        const stabilityMultiplier = this.calculateStabilityMultiplier(responseQuality, wordState.difficulty, wordState.stability);
        wordState.stability *= stabilityMultiplier;

        // Ensure minimum stability
        wordState.stability = Math.max(0.1, wordState.stability);

        // Update state based on performance
        if (responseQuality === ResponseQuality.FAIL) {
            wordState.state = WordState.LEARNING; // Back to learning after failure
        } else if (wordState.stability > 1) {
            wordState.state = WordState.REVIEW; // Graduate to review state
        }
    }

    /**
     * Calculate stability multiplier based on FSRS formula
     */
    calculateStabilityMultiplier(responseQuality, difficulty, stability) {
        const w = this.fsrsParams.w;

        // FSRS stability calculation
        const factor1 = Math.exp(w[8]) * (11 - difficulty) * Math.pow(stability, -w[9]) *
                       (Math.exp(w[10] * (1 - responseQuality)) - 1);

        return Math.max(0.1, 1 + factor1);
    }

    /**
     * Calculate current retrievability using FSRS formula
     */
    calculateRetrievability(wordState, currentTime) {
        if (wordState.lastReviewTime === 0 || wordState.stability === 0) {
            return 1.0; // New word or no stability data
        }

        const daysSinceReview = (currentTime - wordState.lastReviewTime) / (24 * 60 * 60 * 1000);
        return Math.exp(-daysSinceReview / wordState.stability);
    }

    /**
     * Schedule next review time
     */
    scheduleNextReview(wordState, responseQuality, currentTime) {
        let interval = 0;

        if (wordState.state === WordState.NEW || wordState.state === WordState.LEARNING) {
            // Use learning steps
            const stepIndex = Math.min(wordState.repsCorrect, this.fsrsParams.learningSteps.length - 1);
            interval = this.fsrsParams.learningSteps[stepIndex] * 60 * 1000; // Convert minutes to ms
        } else {
            // Calculate interval based on stability and desired retention
            const desiredRetention = this.fsrsParams.retentionRate;
            interval = wordState.stability * Math.log(desiredRetention) / Math.log(0.9) * 24 * 60 * 60 * 1000;

            // Apply response quality adjustments
            if (responseQuality === ResponseQuality.EASY) {
                interval *= this.fsrsParams.easyInterval;
            } else if (responseQuality === ResponseQuality.HARD) {
                interval *= 0.5;
            } else if (responseQuality === ResponseQuality.FAIL) {
                interval = this.fsrsParams.learningSteps[0] * 60 * 1000; // Back to first learning step
            }
        }

        // Cap the interval
        const maxInterval = this.fsrsParams.maxInterval * 24 * 60 * 60 * 1000;
        interval = Math.min(interval, maxInterval);

        wordState.interval = interval;
        wordState.nextDueTime = currentTime + interval;
    }

    /**
     * Update word priority for intelligent selection
     */
    updateWordPriority(wordState, currentTime) {
        let priority = 0;

        // 1. Due factor (most important)
        if (currentTime >= wordState.nextDueTime) {
            const overdueDays = (currentTime - wordState.nextDueTime) / (24 * 60 * 60 * 1000);
            priority += 10.0 + Math.min(overdueDays * 2, 20); // Cap at 30 total
        }

        // 2. Retrievability factor (lower retrievability = higher priority)
        priority += (1.0 - wordState.retrievability) * 5.0;

        // 3. Difficulty factor (harder words get more practice)
        priority += wordState.difficulty * 2.0;

        // 4. Lapse factor (words that were failed recently)
        if (wordState.lapseCount > 0) {
            priority += Math.min(wordState.lapseCount * 1.5, 5.0);
        }

        // 5. New word bonus
        if (wordState.state === WordState.NEW) {
            priority += 3.0;
        }

        // 6. Uncertainty factor (for exploration)
        priority += wordState.uncertainty * this.uncertaintyWeight;

        wordState.priority = priority;
    }

    /**
     * Update uncertainty based on recent performance
     */
    updateUncertainty(wordState) {
        // Uncertainty decreases with more repetitions
        const baseUncertainty = Math.exp(-wordState.repsTotal * 0.1);

        // Increase uncertainty if performance is inconsistent
        const accuracy = wordState.repsTotal > 0 ? wordState.repsCorrect / wordState.repsTotal : 0;
        const consistencyFactor = Math.abs(accuracy - 0.5) * 2; // Higher when accuracy is close to 50%

        wordState.uncertainty = Math.max(0.1, baseUncertainty + (1 - consistencyFactor) * 0.3);
    }

    /**
     * Save word state to localStorage
     */
    saveWordState(wordState) {
        const wordStates = JSON.parse(localStorage.getItem('fsrs_word_states') || '{}');
        wordStates[wordState.wordId] = wordState;
        localStorage.setItem('fsrs_word_states', JSON.stringify(wordStates));
    }

    /**
     * Select words for next session using intelligent FSRS algorithm
     */
    selectWordsForSession(vocabularyData, sessionLength = 15) {
        const currentTime = Date.now();
        const wordPriorities = [];

        // Calculate priority for each word
        vocabularyData.forEach(vocabItem => {
            const wordState = this.getWordState(vocabItem.concept);
            this.updateWordPriority(wordState, currentTime);

            wordPriorities.push({
                ...vocabItem,
                wordState: wordState,
                priority: wordState.priority
            });
        });

        // Sort by priority (higher = more urgent)
        wordPriorities.sort((a, b) => b.priority - a.priority);

        // Select words with exploration vs exploitation
        const selectedWords = [];
        const targetCount = Math.min(sessionLength, wordPriorities.length);

        for (let i = 0; i < targetCount; i++) {
            let selectedWord;

            if (Math.random() < this.explorationRate && i < wordPriorities.length) {
                // Exploration: select based on uncertainty
                const remainingWords = wordPriorities.slice(i);
                const uncertaintyWeights = remainingWords.map(w => w.wordState.uncertainty);
                const totalWeight = uncertaintyWeights.reduce((sum, w) => sum + w, 0);

                if (totalWeight > 0) {
                    let randomValue = Math.random() * totalWeight;
                    let selectedIndex = 0;

                    for (let j = 0; j < uncertaintyWeights.length; j++) {
                        randomValue -= uncertaintyWeights[j];
                        if (randomValue <= 0) {
                            selectedIndex = j;
                            break;
                        }
                    }

                    selectedWord = remainingWords[selectedIndex];
                    // Remove selected word from remaining list
                    const originalIndex = wordPriorities.indexOf(selectedWord);
                    wordPriorities.splice(originalIndex, 1);
                } else {
                    selectedWord = wordPriorities[i];
                }
            } else {
                // Exploitation: select highest priority
                selectedWord = wordPriorities[i];
            }

            if (selectedWord) {
                selectedWords.push({
                    concept: selectedWord.concept,
                    definition: selectedWord.definition,
                    priority: selectedWord.priority,
                    state: selectedWord.wordState.state,
                    difficulty: selectedWord.wordState.difficulty
                });
            }
        }

        console.log('🧠 FSRS Selected Words:', selectedWords.map(w =>
            `${w.concept} (Priority: ${w.priority.toFixed(2)}, State: ${w.state})`
        ));

        return selectedWords;
    }

    /**
     * Get learning analytics
     */
    getAnalytics() {
        const wordStates = JSON.parse(localStorage.getItem('fsrs_word_states') || '{}');
        const wordIds = Object.keys(wordStates);

        if (wordIds.length === 0) {
            return {
                totalWords: 0,
                newWords: 0,
                learningWords: 0,
                reviewWords: 0,
                masteredWords: 0,
                averageAccuracy: 0,
                totalReviews: 0
            };
        }

        let newWords = 0, learningWords = 0, reviewWords = 0, masteredWords = 0;
        let totalReviews = 0, totalCorrect = 0;

        wordIds.forEach(wordId => {
            const state = wordStates[wordId];
            totalReviews += state.repsTotal;
            totalCorrect += state.repsCorrect;

            switch (state.state) {
                case WordState.NEW:
                    newWords++;
                    break;
                case WordState.LEARNING:
                    learningWords++;
                    break;
                case WordState.REVIEW:
                    if (state.retrievability > 0.9 && state.streakCorrect >= 3) {
                        masteredWords++;
                    } else {
                        reviewWords++;
                    }
                    break;
            }
        });

        return {
            totalWords: wordIds.length,
            newWords,
            learningWords,
            reviewWords,
            masteredWords,
            averageAccuracy: totalReviews > 0 ? totalCorrect / totalReviews : 0,
            totalReviews
        };
    }

    /**
     * Export all FSRS data for analysis
     */
    exportData() {
        return {
            wordStates: JSON.parse(localStorage.getItem('fsrs_word_states') || '{}'),
            learningLogs: JSON.parse(localStorage.getItem('fsrs_learning_logs') || '[]'),
            csvData: this.dataLogger.exportCSV(),
            jsonData: this.dataLogger.exportJSON()
        };
    }

    /**
     * Reset all FSRS data (for testing purposes)
     */
    resetData() {
        localStorage.removeItem('fsrs_word_states');
        localStorage.removeItem('fsrs_learning_logs');
        this.dataLogger.clearLogs();
        this.initializeStorage();
    }
}