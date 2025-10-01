/**
 * Adaptive Learning Client - Offline FSRS-based intelligent word selection
 * No external API dependencies - pure offline functionality
 */
class AdaptiveLearningClient {
    constructor() {
        this.currentSessionId = null;
        this.userId = this.getUserId();

        // Initialize FSRS engine for offline intelligent learning
        this.fsrsEngine = new FSRSEngine();

        console.log('🧠 Adaptive Learning Client initialized in offline mode');
    }

    getUserId() {
        // Get or create user ID from localStorage
        let userId = localStorage.getItem('vocabularyGameUserId');
        if (!userId) {
            userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            localStorage.setItem('vocabularyGameUserId', userId);
        }
        return userId;
    }

    async initializeUser(vocabularyData) {
        // Store vocabulary for FSRS processing
        this.storeVocabulary(vocabularyData);
        return { status: 'success', message: 'Initialized with FSRS offline mode' };
    }

    async startSession(sessionLength = 15) {
        this.currentSessionId = `offline_${Date.now()}`;
        const storedVocab = this.getStoredVocabulary();
        const selectedWords = this.fsrsEngine.selectWordsForSession(storedVocab, sessionLength);

        console.log('🎯 Session started with FSRS-selected words:', selectedWords.length);

        return {
            session_id: this.currentSessionId,
            words: selectedWords.map(w => w.concept),
            selectedWords: selectedWords,
            method: 'fsrs_offline'
        };
    }

    async recordResponse(wordId, isCorrect, responseTimeMs, usedHint = false) {
        // Always use FSRS for recording and updating word states
        console.log('📝 Recording response for:', wordId, 'Correct:', isCorrect, 'Time:', responseTimeMs);
        const updatedWordState = this.fsrsEngine.updateWordState(wordId, isCorrect, responseTimeMs, usedHint);
        console.log('🧠 FSRS Updated:', wordId, {
            priority: updatedWordState.priority.toFixed(2),
            repsTotal: updatedWordState.repsTotal,
            repsCorrect: updatedWordState.repsCorrect,
            accuracy: updatedWordState.repsTotal > 0 ? (updatedWordState.repsCorrect / updatedWordState.repsTotal).toFixed(2) : 0
        });

        return {
            status: 'success',
            message: 'Recorded with FSRS',
            word_state: updatedWordState
        };
    }

    async endSession() {
        this.currentSessionId = null;
        return { status: 'success', message: 'Session ended locally' };
    }

    async getAnalytics() {
        return this.getOfflineAnalytics();
    }

    async getWordStates() {
        return this.getOfflineWordStates();
    }

    // Store vocabulary data locally for FSRS processing
    storeVocabulary(vocabularyData) {
        localStorage.setItem('vocabularyData', JSON.stringify(vocabularyData));
        console.log('📚 Stored', vocabularyData.length, 'vocabulary items for FSRS processing');
    }

    getStoredVocabulary() {
        const stored = localStorage.getItem('vocabularyData');
        return stored ? JSON.parse(stored) : [];
    }

    // Get comprehensive offline analytics
    getOfflineAnalytics() {
        const fsrsAnalytics = this.fsrsEngine.getAnalytics();
        const localStats = this.getLocalStats();

        const analytics = {
            total_words: fsrsAnalytics.totalWords,
            new_words: fsrsAnalytics.newWords,
            learning_words: fsrsAnalytics.learningWords,
            review_words: fsrsAnalytics.reviewWords,
            mastered_words: fsrsAnalytics.masteredWords,
            average_accuracy: fsrsAnalytics.averageAccuracy,
            total_reviews: fsrsAnalytics.totalReviews,
            session_count: localStats.sessionCount || 0,
            total_time_spent: localStats.totalTimeSpent || 0,
            average_session_length: localStats.averageSessionLength || 0,
            recommendations: this.generateRecommendations(fsrsAnalytics, localStats)
        };

        console.log('📊 Offline Analytics:', analytics);
        return analytics;
    }

    // Generate learning recommendations based on FSRS data
    generateRecommendations(fsrsAnalytics, localStats) {
        const recommendations = [];

        if (fsrsAnalytics.averageAccuracy < 0.7) {
            recommendations.push('📈 Focus on review sessions to improve accuracy');
        }

        if (fsrsAnalytics.newWords > fsrsAnalytics.learningWords * 2) {
            recommendations.push('🔄 Balance new words with reviewing learned ones');
        }

        if (fsrsAnalytics.masteredWords > 0) {
            recommendations.push(`🏆 Great progress! ${fsrsAnalytics.masteredWords} words mastered`);
        }

        if (localStats.sessionCount > 0 && localStats.averageSessionLength < 5) {
            recommendations.push('⏰ Try longer practice sessions for better retention');
        }

        if (recommendations.length === 0) {
            recommendations.push('✨ Keep up the excellent learning progress!');
        }

        return recommendations;
    }

    // Get offline word states from FSRS engine
    getOfflineWordStates() {
        const wordStates = JSON.parse(localStorage.getItem('fsrs_word_states') || '{}');
        console.log('🗂️ Retrieved word states from localStorage:', Object.keys(wordStates).length, 'words');
        console.log('📊 Sample word states:', Object.entries(wordStates).slice(0, 2));
        return {
            status: 'success',
            word_states: wordStates,
            total_words: Object.keys(wordStates).length
        };
    }

    // Get local learning statistics
    getLocalStats() {
        const stats = localStorage.getItem('learning_stats');
        return stats ? JSON.parse(stats) : {
            sessionCount: 0,
            totalTimeSpent: 0,
            averageSessionLength: 0,
            wordData: {}
        };
    }

    // Update local learning statistics
    updateLocalStats(sessionData) {
        const stats = this.getLocalStats();

        stats.sessionCount += 1;
        if (sessionData.duration) {
            stats.totalTimeSpent += sessionData.duration;
            stats.averageSessionLength = stats.totalTimeSpent / stats.sessionCount;
        }

        localStorage.setItem('learning_stats', JSON.stringify(stats));
    }

    // Export FSRS data for analysis
    downloadCSV() {
        this.fsrsEngine.dataLogger.downloadCSV();
    }

    downloadJSON() {
        this.fsrsEngine.dataLogger.downloadJSON();
    }

    resetFSRSData() {
        this.fsrsEngine.resetData();
        localStorage.removeItem('learning_stats');
        localStorage.removeItem('vocabularyData');
        console.log('🗑️ All learning data reset');
    }

    // Get learning insights
    getLearningInsights() {
        const insights = [];
        const analytics = this.getOfflineAnalytics();

        if (analytics.new_words > 0) {
            insights.push({
                type: 'new_words',
                message: `📝 ${analytics.new_words} new words ready to learn`
            });
        }

        if (analytics.review_words > 0) {
            insights.push({
                type: 'review',
                message: `🔄 ${analytics.review_words} words due for review`
            });
        }

        if (analytics.mastered_words > 0) {
            insights.push({
                type: 'mastered',
                message: `🎯 ${analytics.mastered_words} words mastered!`
            });
        }

        insights.push({
            type: 'offline',
            message: '🧠 Powered by FSRS algorithm - no internet required'
        });

        return insights;
    }

    // Always return true for offline mode
    isOnline() {
        return true; // Always "online" in offline mode
    }
}