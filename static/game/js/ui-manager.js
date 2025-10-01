class UIManager {
    constructor() {
        this.initializeElements();
        this.currentFontSize = 14; // Default font size
        this.fontSizes = [10, 14, 18, 22, 26, 30, 34, 38, 40]; // Font sizes from 10 to 40 in steps of 4, plus default
    }

    initializeElements() {
        this.conceptsList = document.getElementById('concepts-list');
        this.definitionsList = document.getElementById('definitions-list');
        this.scoreElement = document.getElementById('score');
        this.progressElement = document.getElementById('progress');
        this.feedbackElement = document.getElementById('feedback');
        this.feedbackText = document.getElementById('feedback-text');
        this.newGameBtn = document.getElementById('new-game-btn');
        this.hintBtn = document.getElementById('hint-btn');
        this.resetBtn = document.getElementById('reset-btn');
        this.csvUpload = document.getElementById('csv-upload');
        this.datasetSelect = document.getElementById('dataset-select');
        this.loadDatasetBtn = document.getElementById('load-dataset-btn');
        this.fontSizeIncreaseBtn = document.getElementById('font-size-increase-btn');
        this.fontSizeDecreaseBtn = document.getElementById('font-size-decrease-btn');
        this.fontSizeDisplay = document.getElementById('font-size-display');
        this.heatmapBtn = document.getElementById('heatmap-btn');
        this.gridSizeSelect = document.getElementById('grid-size-select');
    }

    createItemElement(item, clickHandler) {
        const element = document.createElement('div');
        element.className = 'item';
        element.textContent = item.text;
        element.dataset.id = item.id;
        element.dataset.uniqueId = item.uniqueId || item.id; // Use uniqueId for DOM targeting
        element.dataset.type = item.type;
        element.tabIndex = 0;
        element.style.fontSize = `${this.currentFontSize}px`;

        element.addEventListener('click', () => clickHandler(element));
        element.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                clickHandler(element);
            }
        });

        return element;
    }

    renderGameItems(concepts, definitions, clickHandler) {
        this.conceptsList.innerHTML = '';
        this.definitionsList.innerHTML = '';

        // Apply selected grid layout
        this.applyGridLayout();

        concepts.forEach(concept => {
            const element = this.createItemElement(concept, clickHandler);
            this.conceptsList.appendChild(element);
        });

        definitions.forEach(definition => {
            const element = this.createItemElement(definition, clickHandler);
            this.definitionsList.appendChild(element);
        });
    }

    updateScore(score) {
        this.scoreElement.textContent = `Score: ${score}`;
    }

    updateProgress(current, total) {
        this.progressElement.textContent = `Progress: ${current}/${total}`;
    }

    showFeedback(message, type) {
        this.feedbackText.textContent = message;
        this.feedbackElement.className = `feedback ${type}`;
        this.feedbackElement.classList.remove('hidden');
    }

    hideFeedback() {
        this.feedbackElement.classList.add('hidden');
    }

    populateDatasetSelect(datasets) {
        console.log('🎛️ Populating dataset select with:', datasets);
        console.log('🎛️ datasetSelect element:', this.datasetSelect);

        if (!this.datasetSelect) {
            console.error('❌ datasetSelect element not found!');
            return;
        }

        this.datasetSelect.innerHTML = '<option value="">Select a dataset...</option>';
        datasets.forEach(dataset => {
            const option = document.createElement('option');
            option.value = dataset;
            option.textContent = dataset.replace('.csv', '').replace(/_/g, ' ');
            this.datasetSelect.appendChild(option);
            console.log('➕ Added dataset option:', dataset);
        });

        console.log('✅ Dataset select populated with', datasets.length, 'datasets');
    }

    enableLoadDatasetButton(enabled) {
        this.loadDatasetBtn.disabled = !enabled;
    }

    enableHintButton(enabled) {
        this.hintBtn.disabled = !enabled;
    }

    resetAllItems() {
        document.querySelectorAll('.item').forEach(item => {
            item.classList.remove('matched', 'selected', 'incorrect', 'frozen', 'disappearing');
            item.style.visibility = 'visible';
        });
    }

    highlightDefinition(conceptId) {
        const definitionElement = document.querySelector(
            `[data-type="definition"][data-id="${conceptId}"]`
        );
        if (definitionElement && !definitionElement.classList.contains('matched')) {
            definitionElement.style.background = '#ffd700';
            setTimeout(() => {
                definitionElement.style.background = '';
            }, 2000);
            return true;
        }
        return false;
    }

    highlightCorrectPairs(selectedConceptId, selectedDefinitionId, gameData) {
        // Find the correct definition for the selected concept
        const correctDefinitionForConcept = gameData.find(item => item.concept === selectedConceptId);
        if (correctDefinitionForConcept) {
            const correctDefElement = document.querySelector(
                `[data-type="definition"][data-id="${correctDefinitionForConcept.concept}"]`
            );
            if (correctDefElement && !correctDefElement.classList.contains('matched')) {
                correctDefElement.style.background = '#48bb78';
                correctDefElement.style.border = '3px solid #38a169';
                correctDefElement.style.boxShadow = '0 0 15px rgba(72, 187, 120, 0.6)';
            }
        }

        // Find the correct concept for the selected definition
        const correctConceptForDefinition = gameData.find(item => item.concept === selectedDefinitionId);
        if (correctConceptForDefinition) {
            const correctConceptElement = document.querySelector(
                `[data-type="concept"][data-id="${correctConceptForDefinition.concept}"]`
            );
            if (correctConceptElement && !correctConceptElement.classList.contains('matched')) {
                correctConceptElement.style.background = '#48bb78';
                correctConceptElement.style.border = '3px solid #38a169';
                correctConceptElement.style.boxShadow = '0 0 15px rgba(72, 187, 120, 0.6)';
            }
        }

        // Clear highlights after 3 seconds
        setTimeout(() => {
            document.querySelectorAll('.item').forEach(item => {
                if (item.style.background === 'rgb(72, 187, 120)') {
                    item.style.background = '';
                    item.style.border = '';
                    item.style.boxShadow = '';
                }
            });
        }, 3000);
    }

    increaseFontSize() {
        const currentIndex = this.fontSizes.indexOf(this.currentFontSize);
        if (currentIndex < this.fontSizes.length - 1) {
            this.currentFontSize = this.fontSizes[currentIndex + 1];
            this.applyFontSize();
        }
        return this.currentFontSize;
    }

    decreaseFontSize() {
        const currentIndex = this.fontSizes.indexOf(this.currentFontSize);
        if (currentIndex > 0) {
            this.currentFontSize = this.fontSizes[currentIndex - 1];
            this.applyFontSize();
        }
        return this.currentFontSize;
    }

    applyFontSize() {
        // Apply font size to all items
        document.querySelectorAll('.item').forEach(item => {
            item.style.fontSize = `${this.currentFontSize}px`;
        });

        // Update button states
        this.updateFontSizeButtons();
    }

    updateFontSizeButtons() {
        const currentIndex = this.fontSizes.indexOf(this.currentFontSize);

        // Disable decrease button if at minimum font size
        this.fontSizeDecreaseBtn.disabled = currentIndex === 0;

        // Disable increase button if at maximum font size
        this.fontSizeIncreaseBtn.disabled = currentIndex === this.fontSizes.length - 1;

        // Update font size display (just the number)
        this.fontSizeDisplay.textContent = this.currentFontSize;
    }

    initializeFontSizeButtons() {
        this.updateFontSizeButtons();
    }

    applyGridLayout() {
        const selectedSize = this.gridSizeSelect.value;

        // Remove existing grid classes
        this.conceptsList.className = 'items-list';
        this.definitionsList.className = 'items-list';

        // Add the selected grid class
        if (selectedSize !== 'custom') {
            this.conceptsList.classList.add(`grid-${selectedSize}`);
            this.definitionsList.classList.add(`grid-${selectedSize}`);
        } else {
            this.conceptsList.classList.add('grid-custom');
            this.definitionsList.classList.add('grid-custom');
        }
    }

    getSelectedGridPairCount() {
        const selectedSize = this.gridSizeSelect.value;

        const gridSizes = {
            '2x2': 4,
            '3x3': 9,
            '3x4': 12,
            '4x3': 12,
            '4x4': 16,
            '5x3': 15,
            'custom': 9 // Default for auto-fit
        };

        return gridSizes[selectedSize] || 9;
    }

    onGridSizeChange(callback) {
        this.gridSizeSelect.addEventListener('change', () => {
            callback();
        });
    }
}