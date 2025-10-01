class DataManager {
    constructor() {
        this.gameData = [];
        this.loadDefaultData();
    }

    loadDefaultData() {
        this.gameData = [
            { concept: 'Photosynthesis', definition: 'The process by which plants convert sunlight into energy' },
            { concept: 'Democracy', definition: 'A system of government where citizens vote for their representatives' },
            { concept: 'Ecosystem', definition: 'A community of living organisms and their physical environment' },
            { concept: 'Renaissance', definition: 'A period of cultural rebirth in Europe from 14th to 17th century' },
            { concept: 'Algorithm', definition: 'A step-by-step procedure for solving a problem or completing a task' },
            { concept: 'Mitosis', definition: 'The process of cell division that produces two identical daughter cells' },
            { concept: 'Capitalism', definition: 'An economic system based on private ownership and free market competition' },
            { concept: 'Gravity', definition: 'The force that attracts objects toward the center of the Earth' },
            { concept: 'Metaphor', definition: 'A figure of speech that compares two unlike things without using like or as' },
            { concept: 'Inflation', definition: 'A general increase in prices and fall in purchasing value of money' },
            { concept: 'Biodiversity', definition: 'The variety of life forms within ecosystems including species diversity' },
            { concept: 'Quantum', definition: 'The smallest discrete unit of any physical property involved in an interaction' },
            { concept: 'Empathy', definition: 'The ability to understand and share the feelings of others' },
            { concept: 'Entropy', definition: 'A measure of randomness or disorder within a thermodynamic system' },
            { concept: 'Catalyst', definition: 'A substance that speeds up a chemical reaction without being consumed' }
        ];
    }

    async loadAvailableDatasets() {
        try {
            console.log('📂 Loading available datasets from data/datasets.json...');
            // Load datasets from the auto-generated manifest
            const response = await fetch('data/datasets.json');
            if (response.ok) {
                const manifest = await response.json();
                console.log('✅ Successfully loaded datasets:', manifest);
                return manifest.datasets || [];
            } else {
                throw new Error('Failed to load datasets manifest');
            }
        } catch (error) {
            console.log('⚠️ Could not load dataset list from manifest, falling back to directory scan attempt:', error);

            // Fallback: try to detect common CSV files
            const commonFiles = ['sample_vocabulary.csv', 'words.csv', 'pali.csv'];
            const availableFiles = [];

            for (const file of commonFiles) {
                try {
                    const testResponse = await fetch(`data/${file}`, { method: 'HEAD' });
                    if (testResponse.ok) {
                        availableFiles.push(file);
                    }
                } catch (e) {
                    // File doesn't exist, skip it
                }
            }

            return availableFiles;
        }
    }

    async loadDatasetFromFile(filename) {
        try {
            const response = await fetch(`data/${filename}`);
            if (!response.ok) {
                throw new Error(`Failed to load dataset: ${response.statusText}`);
            }
            const csvText = await response.text();
            this.parseCSV(csvText);
            return true;
        } catch (error) {
            throw error;
        }
    }

    parseCSV(csvText) {
        const lines = csvText.trim().split('\n');
        const data = [];

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            if (!line) continue;

            const columns = this.parseCSVLine(line);
            if (columns.length >= 2) {
                const concept = columns[0].trim();
                const definition = columns[1].trim();

                if (i === 0 && (concept.toLowerCase() === 'concept' || concept.toLowerCase() === 'term')) {
                    continue;
                }

                data.push({
                    concept: concept,
                    definition: definition
                });
            }
        }

        if (data.length === 0) {
            throw new Error('No valid data found in CSV');
        }

        this.gameData = data;
    }

    parseCSVLine(line) {
        const result = [];
        let current = '';
        let inQuotes = false;

        for (let i = 0; i < line.length; i++) {
            const char = line[i];

            if (char === '"') {
                inQuotes = !inQuotes;
            } else if (char === ',' && !inQuotes) {
                result.push(current);
                current = '';
            } else {
                current += char;
            }
        }

        result.push(current);
        return result;
    }

    getData() {
        return this.gameData;
    }

    shuffleArray(array) {
        const shuffled = [...array];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
    }
}