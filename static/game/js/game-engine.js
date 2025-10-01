class GameEngine {
    constructor() {
        this.currentRound = [];
        this.selectedConcept = null;
        this.selectedDefinition = null;
        this.matches = new Set();
        this.score = 0;
        this.totalQuestions = 0;
        this.currentQuestion = 0;
        this.attempts = 0;
        this.maxAttempts = 3;
        this.frozenItems = new Set();
    }

    startNewRound(gameData, maxPairs = 15) {
        if (gameData.length === 0) {
            throw new Error('No game data available');
        }

        this.currentRound = this.shuffleArray([...gameData]).slice(0, Math.min(maxPairs, gameData.length));
        this.matches.clear();
        this.score = 0;
        this.totalQuestions = this.currentRound.length;
        this.currentQuestion = 0;
        this.attempts = 0;
        this.selectedConcept = null;
        this.selectedDefinition = null;
        this.frozenItems.clear();

        return this.prepareGameItems();
    }

    prepareGameItems() {
        const concepts = this.shuffleArray(this.currentRound.map((item, index) => ({
            text: item.concept,
            id: item.concept,
            uniqueId: `concept_${index}_${item.concept}`,
            type: 'concept'
        })));

        const definitions = this.shuffleArray(this.currentRound.map((item, index) => ({
            text: item.definition,
            id: item.concept,
            uniqueId: `definition_${index}_${item.concept}`,
            type: 'definition'
        })));

        return { concepts, definitions };
    }

    selectItem(element) {
        // Prevent selection of matched, frozen, or disappearing elements
        if (element.classList.contains('matched') ||
            element.classList.contains('frozen') ||
            element.classList.contains('disappearing') ||
            element.style.visibility === 'hidden') {
            return false;
        }

        const type = element.dataset.type;
        const id = element.dataset.id;
        const uniqueId = element.dataset.uniqueId;

        if (type === 'concept') {
            this.clearSelection('concept');
            this.selectedConcept = { element, id, uniqueId };
            element.classList.add('selected');
        } else {
            this.clearSelection('definition');
            this.selectedDefinition = { element, id, uniqueId };
            element.classList.add('selected');
        }

        return this.selectedConcept && this.selectedDefinition;
    }

    clearSelection(type) {
        if (type === 'concept' && this.selectedConcept) {
            this.selectedConcept.element.classList.remove('selected');
            this.selectedConcept = null;
        } else if (type === 'definition' && this.selectedDefinition) {
            this.selectedDefinition.element.classList.remove('selected');
            this.selectedDefinition = null;
        }
    }

    checkMatch() {
        if (!this.selectedConcept || !this.selectedDefinition) {
            return null;
        }

        const isMatch = this.selectedConcept.id === this.selectedDefinition.id;
        this.attempts++;

        return {
            isMatch,
            conceptElement: this.selectedConcept.element,
            definitionElement: this.selectedDefinition.element,
            conceptId: this.selectedConcept.id,
            definitionId: this.selectedDefinition.id
        };
    }

    handleCorrectMatch() {
        this.matches.add(this.selectedConcept.id);
        this.score += Math.max(1, 4 - this.attempts);
        this.currentQuestion++;

        // Store references to the exact matched elements
        const matchedConceptElement = this.selectedConcept.element;
        const matchedDefinitionElement = this.selectedDefinition.element;

        // Add matched class to prevent further interaction
        matchedConceptElement.classList.add('matched', 'disappearing');
        matchedDefinitionElement.classList.add('matched', 'disappearing');

        // Clear selections immediately to prevent interference
        this.selectedConcept = null;
        this.selectedDefinition = null;

        // Hide the specific matched elements after animation
        setTimeout(() => {
            // Double-check the elements still exist and have the matched class
            if (matchedConceptElement && matchedConceptElement.classList.contains('matched')) {
                matchedConceptElement.style.visibility = 'hidden';
            }
            if (matchedDefinitionElement && matchedDefinitionElement.classList.contains('matched')) {
                matchedDefinitionElement.style.visibility = 'hidden';
            }
        }, 800);

        return this.matches.size === this.currentRound.length;
    }

    handleIncorrectMatch() {
        const conceptElement = this.selectedConcept.element;
        const definitionElement = this.selectedDefinition.element;

        conceptElement.classList.add('incorrect');
        definitionElement.classList.add('incorrect');

        setTimeout(() => {
            conceptElement.classList.remove('incorrect', 'selected');
            definitionElement.classList.remove('incorrect', 'selected');

            conceptElement.classList.add('frozen');
            definitionElement.classList.add('frozen');

            this.selectedConcept = null;
            this.selectedDefinition = null;

            setTimeout(() => {
                conceptElement.classList.remove('frozen');
                definitionElement.classList.remove('frozen');
            }, 3000);
        }, 1000);
    }

    showHint() {
        if (!this.selectedConcept) {
            return { success: false, message: 'Select a concept first to get a hint!' };
        }

        const matchingDefinition = this.currentRound.find(item =>
            item.concept === this.selectedConcept.id
        );

        if (matchingDefinition) {
            return { success: true, conceptId: matchingDefinition.concept };
        }

        return { success: false, message: 'No hint available' };
    }

    resetRound() {
        this.clearSelection('concept');
        this.clearSelection('definition');
        this.matches.clear();
        this.score = 0;
        this.currentQuestion = 0;
        this.attempts = 0;
        this.frozenItems.clear();
    }

    getGameStats() {
        return {
            score: this.score,
            matches: this.matches.size,
            totalQuestions: this.totalQuestions,
            isComplete: this.matches.size === this.currentRound.length,
            percentage: Math.round((this.score / (this.totalQuestions * 4)) * 100)
        };
    }

    shuffleArray(array) {
        const shuffled = [...array];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
    }

    getCurrentRound() {
        return this.currentRound || [];
    }
}