# 🏗️ Architecture Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Module Breakdown](#module-breakdown)
4. [Data Flow](#data-flow)
5. [Event System](#event-system)
6. [State Management](#state-management)
7. [UI/UX Design Patterns](#uiux-design-patterns)
8. [File Structure](#file-structure)
9. [Development Guidelines](#development-guidelines)

## 🎯 Overview

The Vocabulary Matching Game is a modern web application built with vanilla JavaScript using a modular architecture pattern. The application follows the **Separation of Concerns** principle, where each module handles a specific aspect of the game functionality.

### Core Principles
- **Modular Design**: Each component has a single responsibility
- **Loose Coupling**: Modules communicate through well-defined interfaces
- **High Cohesion**: Related functionality is grouped together
- **Progressive Enhancement**: Works without JavaScript (basic HTML structure)

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Frontend Game Engine                          │
│                           (main.js controller)                         │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────────────┐ │
│  │ Audio Manager│ │  UI Manager  │ │ Game Engine  │ │ Learning Client │ │
│  │              │ │              │ │              │ │ (API Bridge)    │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └─────────────────┘ │
│                           │                                   │         │
│                    ┌──────────────┐                          │         │
│                    │ Data Manager │                          │         │
│                    │              │                          │         │
│                    └──────────────┘                          │         │
└─────────────────────────────────────────────────────────────┼─────────┘
                                                                │
                                  HTTP/REST API                 │
                                                                │
┌─────────────────────────────────────────────────────────────┼─────────┐
│                        Backend Learning System               │         │
├─────────────────────────────────────────────────────────────┼─────────┤
│                    ┌─────────────────────────────────────────┼───────┐ │
│                    │            FastAPI Server              │       │ │
│                    │            (learning_api.py)           │       │ │
│                    └─────────────────────────────────────────┼───────┘ │
│                                        │                     │         │
│                    ┌─────────────────────────────────────────┼───────┐ │
│                    │       Adaptive Learning Engine         │       │ │
│                    │       (adaptive_learning_engine.py)    │       │ │
│                    │                                         │       │ │
│                    │  ┌─────────────┐  ┌─────────────────┐   │       │ │
│                    │  │ FSRS Engine │  │ Word Selection  │   │       │ │
│                    │  │             │  │ Algorithm       │   │       │ │
│                    │  └─────────────┘  └─────────────────┘   │       │ │
│                    │                                         │       │ │
│                    │  ┌─────────────┐  ┌─────────────────┐   │       │ │
│                    │  │ User Model  │  │ Analytics       │   │       │ │
│                    │  │ (IRT θ)     │  │ Engine          │   │       │ │
│                    │  └─────────────┘  └─────────────────┘   │       │ │
│                    └─────────────────────────────────────────┼───────┘ │
│                                        │                     │         │
│                    ┌─────────────────────────────────────────┼───────┐ │
│                    │          SQLite Database               │       │ │
│                    │                                         │       │ │
│                    │  ┌─────────────┐  ┌─────────────────┐   │       │ │
│                    │  │ User States │  │ Word States     │   │       │ │
│                    │  │             │  │ (FSRS params)   │   │       │ │
│                    │  └─────────────┘  └─────────────────┘   │       │ │
│                    │                                         │       │ │
│                    │  ┌─────────────────────────────────────┐ │       │ │
│                    │  │       Session Logs                  │ │       │ │
│                    │  │   (Performance Analytics)           │ │       │ │
│                    │  └─────────────────────────────────────┘ │       │ │
│                    └─────────────────────────────────────────┼───────┘ │
└─────────────────────────────────────────────────────────────┼─────────┘
```

## 📦 Module Breakdown

### 1. 🎵 Audio Manager (`audio-manager.js`)
**Purpose**: Handles all audio feedback and haptic responses

```javascript
class AudioManager {
    // Web Audio API context for sound generation
    constructor()
    initializeSounds()     // Initialize Web Audio API
    playCorrectSound()     // Play success sound (C5-E5-G5 chord)
    triggerHapticFeedback() // Device vibration for errors
}
```

**Key Features**:
- **Web Audio API**: Generates procedural sound effects
- **Haptic Feedback**: Uses Vibration API for tactile responses
- **Graceful Degradation**: Works without audio support
- **Performance Optimized**: Reuses audio context

**Technical Details**:
```javascript
// Success sound: Musical chord progression
oscillator.frequency.setValueAtTime(523.25, currentTime); // C5
oscillator.frequency.setValueAtTime(659.25, currentTime + 0.1); // E5
oscillator.frequency.setValueAtTime(783.99, currentTime + 0.2); // G5
```

### 2. 📊 Data Manager (`data-manager.js`)
**Purpose**: Manages game data, CSV parsing, and dataset operations

```javascript
class DataManager {
    gameData[]             // Current vocabulary dataset
    loadDefaultData()      // Load built-in vocabulary
    parseCSV()            // Parse uploaded CSV files
    loadDatasetFromFile() // Load predefined datasets
    shuffleArray()        // Randomize data order
}
```

**Key Features**:
- **CSV Parsing**: Custom parser handling quoted fields and special characters
- **Data Validation**: Ensures proper concept-definition pairs
- **Multiple Data Sources**: Built-in data + file uploads + predefined datasets
- **Error Handling**: Comprehensive validation and user feedback

**CSV Format Support**:
```csv
Concept,Definition
"Photosynthesis","The process by which plants convert sunlight into energy"
"Algorithm","A step-by-step procedure for solving a problem"
```

**Technical Implementation**:
```javascript
parseCSVLine(line) {
    // Handles quoted fields with commas
    // Supports escape characters
    // Maintains data integrity
}
```

### 3. 🖥️ UI Manager (`ui-manager.js`)
**Purpose**: Handles all DOM manipulation and user interface updates

```javascript
class UIManager {
    initializeElements()   // Cache DOM references
    createItemElement()    // Generate game items with events
    renderGameItems()      // Populate game boards
    updateScore()          // Update score display
    updateProgress()       // Update progress indicator
    showFeedback()         // Display user feedback
    resetAllItems()        // Clear visual states
}
```

**Key Features**:
- **DOM Caching**: Stores element references for performance
- **Event Delegation**: Efficient event handling
- **Accessibility**: Keyboard navigation and ARIA support
- **Responsive Updates**: Real-time UI state synchronization

**DOM Structure Management**:
```javascript
createItemElement(item, clickHandler) {
    // Creates interactive game items
    // Adds keyboard accessibility
    // Attaches event listeners
    // Returns configured DOM element
}
```

### 4. 🎮 Game Engine (`game-engine.js`)
**Purpose**: Core game logic, state management, and rule enforcement

```javascript
class GameEngine {
    currentRound[]         // Active game items
    selectedConcept        // Current concept selection
    selectedDefinition     // Current definition selection
    matches               // Set of completed matches
    score                 // Current game score

    startNewRound()       // Initialize game round
    selectItem()          // Handle item selection
    checkMatch()          // Validate concept-definition pairs
    handleCorrectMatch()  // Process successful matches
    handleIncorrectMatch()// Process failed attempts
    showHint()           // Provide hint functionality
}
```

**Key Features**:
- **State Machine**: Manages game states and transitions
- **Scoring Algorithm**: Dynamic scoring based on attempts
- **Match Validation**: Ensures correct concept-definition pairing
- **Round Management**: Controls game flow and progression

**Scoring System**:
```javascript
// Score decreases with more attempts (max 4 points per match)
score += Math.max(1, 4 - attempts);
```

**State Management**:
```javascript
// Game states: selecting → validating → feedback → next
if (selectedConcept && selectedDefinition) {
    setTimeout(() => this.checkMatch(), 300);
}
```

### 5. 🎯 Main Controller (`main.js`)
**Purpose**: Orchestrates all modules and manages application lifecycle

```javascript
class VocabularyGame {
    constructor() {
        // Initialize all managers
        this.audioManager = new AudioManager();
        this.dataManager = new DataManager();
        this.uiManager = new UIManager();
        this.gameEngine = new GameEngine();
        this.learningClient = new AdaptiveLearningClient(); // NEW
    }

    bindEvents()              // Setup event listeners
    initializeGame()          // Application startup with AI integration
    startNewGame()            // Begin AI-optimized game session
    selectItem()              // Handle user selections with timing
    checkMatch()              // Coordinate match validation + logging
    showLearningAnalytics()   // Display learning insights
}
```

**Key Features**:
- **Dependency Injection**: Manages module instances
- **Event Coordination**: Routes events between modules
- **Error Handling**: Centralized error management
- **Application Lifecycle**: Controls startup and shutdown
- **Adaptive Learning Integration**: Connects to AI backend

### 6. 🧠 Adaptive Learning Client (`adaptive-learning-client.js`)
**Purpose**: Bridge between frontend game and backend AI system

```javascript
class AdaptiveLearningClient {
    constructor()               // Initialize API connection
    initializeUser()           // Setup user with vocabulary
    startSession()             // Begin adaptive session
    recordResponse()           // Log performance data
    endSession()               // Complete session analytics
    getAnalytics()             // Retrieve learning insights
    selectWordsIntelligently() // Fallback smart selection
}
```

**Key Features**:
- **API Integration**: RESTful communication with Python backend
- **Offline Fallback**: Local smart selection when API unavailable
- **Performance Tracking**: Response times, accuracy, hint usage
- **Progress Persistence**: Local storage for offline continuity
- **Error Resilience**: Graceful degradation to basic mode

### 7. 🌐 FastAPI Server (`learning_api.py`)
**Purpose**: Web API bridge between JavaScript game and Python AI engine

```python
# Key Endpoints
POST /api/initialize          # Setup user vocabulary
POST /api/start-session       # Begin adaptive session
POST /api/record-response     # Log user performance
POST /api/end-session         # Complete session
GET  /api/analytics/{user_id} # Get learning insights
GET  /api/word-states/{user_id} # Debug word performance
```

**Key Features**:
- **CORS Support**: Enables cross-origin requests from game
- **Data Validation**: Pydantic models for type safety
- **Error Handling**: Comprehensive HTTP status codes
- **Static File Serving**: Hosts the game directly

### 8. 🧠 Adaptive Learning Engine (`adaptive_learning_engine.py`)
**Purpose**: Core AI system implementing FSRS and intelligent word selection

```python
class AdaptiveLearningEngine:
    # Data Models
    UserState              # IRT ability, fatigue, preferences
    WordState              # FSRS parameters, performance history
    SessionLog             # Session analytics and cognitive load

    # Core Algorithms
    calculate_retrievability()    # FSRS forgetting curve
    update_fsrs_parameters()      # Update after each response
    select_words_for_session()    # AI word selection
    calculate_word_priority()     # Multi-factor scoring
```

**Scientific Algorithms**:
- **FSRS (Free Spaced Repetition Scheduler)**: Latest SRS research
- **Item Response Theory**: Ability estimation (θ parameter)
- **Multi-Armed Bandits**: Exploration vs exploitation
- **Cognitive Load Theory**: Session optimization

## 🔄 Data Flow

### Game Initialization Flow
```
1. Main Controller instantiates all managers
2. Data Manager loads default vocabulary
3. UI Manager caches DOM elements
4. Audio Manager initializes Web Audio API
5. Event listeners are bound
6. First game round starts
```

### User Interaction Flow
```
User clicks item → UI Manager captures event → Main Controller processes
                                            ↓
Game Engine updates state ← Main Controller validates selection
                                            ↓
Audio/UI feedback ← Game Engine determines outcome → Score updates
```

### Match Validation Process
```
1. User selects concept item (stored in gameEngine.selectedConcept)
2. User selects definition item (stored in gameEngine.selectedDefinition)
3. Game Engine compares IDs: selectedConcept.id === selectedDefinition.id
4. If match: playCorrectSound() + visual animations + score update
5. If no match: haptic feedback + shake animation + temporary freeze
6. UI updates reflect new game state
```

## ⚡ Event System

### Event-Driven Architecture
The application uses a **publisher-subscriber pattern** through DOM events and callback functions:

```javascript
// Event binding in Main Controller
this.uiManager.newGameBtn.addEventListener('click', () => this.startNewGame());

// Event delegation for dynamic content
element.addEventListener('click', () => clickHandler(element));
element.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        clickHandler(element);
    }
});
```

### Supported Events
- **Click Events**: Primary interaction method
- **Keyboard Events**: Accessibility support (Enter/Space)
- **File Events**: CSV upload handling
- **Change Events**: Dataset selection

## 🔧 State Management

### Game State Structure
```javascript
{
    currentRound: [          // Active vocabulary items
        {
            concept: "String",
            definition: "String"
        }
    ],
    selectedConcept: {       // Currently selected concept
        element: DOMElement,
        id: "String"
    },
    selectedDefinition: {    // Currently selected definition
        element: DOMElement,
        id: "String"
    },
    matches: Set(),          // Completed matches (by ID)
    score: Number,           // Current score
    attempts: Number,        // Attempts for current pair
    gameData: []            // Full vocabulary dataset
}
```

### State Transitions
1. **Idle**: No selections active
2. **Concept Selected**: One concept chosen
3. **Both Selected**: Concept + definition chosen
4. **Validating**: Checking match (300ms delay)
5. **Feedback**: Showing result to user
6. **Complete**: All matches found

## 🎨 UI/UX Design Patterns

### Glassmorphism Design System
```css
/* Glass effect pattern */
background: rgba(255, 255, 255, 0.12);
border: 1px solid rgba(255, 255, 255, 0.15);
backdrop-filter: blur(20px);
box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
```

### Animation Philosophy
- **Micro-interactions**: Hover effects, selection states
- **Feedback Animations**: Success (scale + rotate), error (shake)
- **State Transitions**: Smooth 0.3-0.4s cubic-bezier curves
- **Progressive Enhancement**: Respects `prefers-reduced-motion`

### Responsive Design Strategy
```css
/* Mobile-first approach */
@media (max-width: 768px) {
    .game-area { grid-template-columns: 1fr; }
    .items-list { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 480px) {
    .items-list { grid-template-columns: repeat(1, 1fr); }
}
```

## 📁 File Structure

```
📦 New-game/
├── 📄 index.html              # Main HTML structure
├── 📄 styles.css              # Complete styling system
├── 📄 architec.md             # This documentation
├── 📄 README.md               # Project overview
├── 📄 sample_vocabulary.json  # Sample data
├── 📄 csv_processor.py        # Data processing utility
└── 📁 js/                     # JavaScript modules
    ├── 📄 audio-manager.js    # Sound & haptic feedback
    ├── 📄 data-manager.js     # Data handling & CSV parsing
    ├── 📄 ui-manager.js       # DOM manipulation & UI
    ├── 📄 game-engine.js      # Core game logic
    └── 📄 main.js             # Application controller
```

## 👨‍💻 Development Guidelines

### Adding New Features

#### 1. New Audio Effect
```javascript
// In audio-manager.js
playNewSound() {
    if (!this.audioContext) return;
    // Add new sound generation logic
}

// In main.js
someGameEvent() {
    this.audioManager.playNewSound();
}
```

#### 2. New Game Mode
```javascript
// In game-engine.js
startTimedMode(timeLimit) {
    // Add timing logic
    this.timeLimit = timeLimit;
    this.startTime = Date.now();
}

// In ui-manager.js
updateTimer(remainingTime) {
    // Add timer display
}
```

#### 3. New Data Source
```javascript
// In data-manager.js
async loadFromAPI(apiUrl) {
    try {
        const response = await fetch(apiUrl);
        const data = await response.json();
        this.parseAPIData(data);
    } catch (error) {
        throw new Error(`API Error: ${error.message}`);
    }
}
```

### Best Practices

1. **Module Communication**: Always go through the main controller
2. **Error Handling**: Use try-catch blocks and user-friendly messages
3. **Performance**: Cache DOM elements, debounce events when needed
4. **Accessibility**: Add ARIA labels and keyboard support
5. **Testing**: Test with different CSV formats and edge cases

### Code Style Guidelines

```javascript
// Use descriptive variable names
const conceptElement = this.selectedConcept.element;

// Prefer const/let over var
const gameItems = this.prepareGameItems();

// Use arrow functions for callbacks
setTimeout(() => this.checkMatch(), 300);

// Add comments for complex logic
// Play success sound using Web Audio API chord progression
this.playCorrectSound();
```

### Performance Considerations

1. **DOM Queries**: Cache elements in constructor
2. **Event Listeners**: Use event delegation for dynamic content
3. **Memory Management**: Clear intervals/timeouts on cleanup
4. **CSS Animations**: Use transform/opacity for 60fps animations
5. **Asset Loading**: Lazy load audio context (user gesture required)

This architecture ensures the codebase remains maintainable, scalable, and easy to understand for new developers joining the project.