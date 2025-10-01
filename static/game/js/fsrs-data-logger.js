/**
 * FSRS Data Logger - Handles logging and export of learning data
 */
class FSRSDataLogger {
    constructor() {
        this.logs = this.loadLogs();
    }

    /**
     * Load existing logs from localStorage
     */
    loadLogs() {
        return JSON.parse(localStorage.getItem('fsrs_learning_logs') || '[]');
    }

    /**
     * Save logs to localStorage
     */
    saveLogs() {
        localStorage.setItem('fsrs_learning_logs', JSON.stringify(this.logs));
    }

    /**
     * Log a review session
     */
    logReview(wordId, wordState, responseQuality, responseTime, usedHint) {
        const logEntry = {
            timestamp: new Date().toISOString(),
            wordId: wordId,
            responseQuality: responseQuality,
            responseTime: responseTime,
            usedHint: usedHint,
            stateBefore: {
                state: wordState.state,
                stability: wordState.stability,
                difficulty: wordState.difficulty,
                retrievability: wordState.retrievability,
                repsTotal: wordState.repsTotal,
                repsCorrect: wordState.repsCorrect,
                streakCorrect: wordState.streakCorrect
            }
        };

        this.logs.push(logEntry);
        this.saveLogs();
    }

    /**
     * Log state update after FSRS calculations
     */
    logStateUpdate(wordState, responseQuality) {
        // Find the last log entry for this word and update it with after-state
        const lastLog = this.logs[this.logs.length - 1];
        if (lastLog && lastLog.wordId === wordState.wordId) {
            lastLog.stateAfter = {
                state: wordState.state,
                stability: wordState.stability,
                difficulty: wordState.difficulty,
                retrievability: wordState.retrievability,
                repsTotal: wordState.repsTotal,
                repsCorrect: wordState.repsCorrect,
                streakCorrect: wordState.streakCorrect,
                nextDueTime: wordState.nextDueTime,
                priority: wordState.priority
            };

            // Calculate changes
            lastLog.changes = {
                stabilityChange: lastLog.stateAfter.stability - lastLog.stateBefore.stability,
                difficultyChange: lastLog.stateAfter.difficulty - lastLog.stateBefore.difficulty,
                retrievabilityChange: lastLog.stateAfter.retrievability - lastLog.stateBefore.retrievability
            };

            this.saveLogs();
        }
    }

    /**
     * Export data as CSV format
     */
    exportCSV() {
        if (this.logs.length === 0) {
            return 'No data to export';
        }

        const headers = [
            'Timestamp', 'WordId', 'ResponseQuality', 'ResponseTime', 'UsedHint',
            'StateBefore', 'StabilityBefore', 'DifficultyBefore', 'RetrievabilityBefore',
            'StateAfter', 'StabilityAfter', 'DifficultyAfter', 'RetrievabilityAfter',
            'StabilityChange', 'DifficultyChange', 'RetrievabilityChange',
            'RepsTotal', 'RepsCorrect', 'StreakCorrect', 'NextDueTime', 'Priority'
        ];

        const csvRows = [headers.join(',')];

        this.logs.forEach(log => {
            if (log.stateAfter) {
                const row = [
                    log.timestamp,
                    log.wordId,
                    log.responseQuality,
                    log.responseTime,
                    log.usedHint,
                    log.stateBefore.state,
                    log.stateBefore.stability.toFixed(4),
                    log.stateBefore.difficulty.toFixed(4),
                    log.stateBefore.retrievability.toFixed(4),
                    log.stateAfter.state,
                    log.stateAfter.stability.toFixed(4),
                    log.stateAfter.difficulty.toFixed(4),
                    log.stateAfter.retrievability.toFixed(4),
                    log.changes.stabilityChange.toFixed(4),
                    log.changes.difficultyChange.toFixed(4),
                    log.changes.retrievabilityChange.toFixed(4),
                    log.stateAfter.repsTotal,
                    log.stateAfter.repsCorrect,
                    log.stateAfter.streakCorrect,
                    new Date(log.stateAfter.nextDueTime).toISOString(),
                    log.stateAfter.priority.toFixed(4)
                ];
                csvRows.push(row.join(','));
            }
        });

        return csvRows.join('\n');
    }

    /**
     * Export data as JSON format
     */
    exportJSON() {
        return {
            exportTime: new Date().toISOString(),
            totalLogs: this.logs.length,
            logs: this.logs
        };
    }

    /**
     * Download CSV file
     */
    downloadCSV() {
        const csvContent = this.exportCSV();
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `fsrs_learning_data_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
    }

    /**
     * Download JSON file
     */
    downloadJSON() {
        const jsonContent = JSON.stringify(this.exportJSON(), null, 2);
        const blob = new Blob([jsonContent], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `fsrs_learning_data_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        window.URL.revokeObjectURL(url);
    }

    /**
     * Clear all logs
     */
    clearLogs() {
        this.logs = [];
        localStorage.removeItem('fsrs_learning_logs');
    }
}