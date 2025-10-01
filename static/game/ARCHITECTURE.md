# 🏗️ Professional Architecture Documentation

## 📋 System Overview

The Vocabulary Matching Game is a modern, professional web application built with a modular architecture that combines frontend JavaScript with a Python-powered adaptive learning backend. The system emphasizes code quality, maintainability, and optimal learning outcomes.

### 🎯 Core Architecture Principles

1. **Modular Design**: Separated into logical, reusable modules
2. **Professional Code Structure**: Constants, utilities, and clear naming conventions
3. **Separation of Concerns**: Each module handles a specific responsibility
4. **Responsive-First**: Mobile-optimized with landscape support
5. **Event-Driven Architecture**: Components communicate through events
6. **Progressive Enhancement**: Works standalone, enhanced with AI
7. **Adaptive Learning**: FSRS algorithm with spaced repetition

## 🏛️ Updated System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│  │   CSS Modules   │    │  JS Core Files  │    │  JS Utilities   │        │
│  │                 │    │                 │    │                 │        │
│  │ • base.css      │    │ • main.js       │    │ • constants.js  │        │
│  │ • header.css    │    │ • game-engine.js│    │ • utils.js      │        │
│  │ • game-area.css │    │ • ui-manager.js │    │                 │        │
│  │ • game-items.css│    │ • data-manager.js│   │                 │        │
│  │ • controls.css  │    │ • audio-manager.js│  │                 │        │
│  │ • animations.css│    │                 │    │                 │        │
│  │ • responsive.css│    │                 │    │                 │        │
│  │ • landscape.css │    │                 │    │                 │        │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘        │
├─────────────────────────────────────────────────────────────────────────────┤
│                        GAME ENGINE LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      Main Game Controller                            │  │
│  │                         (main.js)                                   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│  ┌───────────┐ ┌────────────┐ ┌──────────────┐ ┌──────────────────────┐  │
│  │ Audio     │ │ UI Manager │ │ Game Engine  │ │ Adaptive Learning    │  │
│  │ Manager   │ │            │ │              │ │ Client               │  │
│  └───────────┘ └────────────┘ └──────────────┘ └──────────────────────┘  │
│                         │                              │                  │
│                ┌──────────────┐              ┌──────────────────────┐    │
│                │ Data Manager │              │ Heatmap Visualizer  │    │
│                │              │              │                      │    │
│                └──────────────┘              └──────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                          HTTP/REST API
                                  │
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BACKEND LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        FastAPI Server                              │   │
│  │                      (learning_api.py)                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                  │                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                  Adaptive Learning Engine                          │   │
│  │                (adaptive_learning_engine.py)                       │   │
│  │                                                                     │   │
│  │  • FSRS Algorithm Implementation                                   │   │
│  │  • Spaced Repetition Logic                                         │   │
│  │  • Item Response Theory (IRT)                                      │   │
│  │  • Multi-Armed Bandit Algorithm                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                  │                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      SQLite Database                               │   │
│  │                    (learning_data.db)                              │   │
│  │                                                                     │   │
│  │  Tables:                                                           │   │
│  │  • user_states                                                     │   │
│  │  • word_states                                                     │   │
│  │  • session_logs                                                    │   │
│  │  • response_logs                                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 📁 Professional File Structure

```
📂 vocabulary-game/
├── 📄 index.html                    # Main HTML file
├── 📄 ARCHITECTURE.md               # This architecture document
├── 📄 README.md                     # Project documentation
├── 📄 requirements.txt              # Python dependencies
├── 📄 update_datasets.py            # Dataset management utility
├── 📄 update_datasets.bat           # Windows batch script
│
├── 📂 css/                          # Modular CSS Architecture
│   ├── 📄 main.css                  # CSS entry point & imports
│   ├── 📄 base.css                  # Reset, body, container styles
│   ├── 📄 header.css                # Header & navigation styles
│   ├── 📄 game-area.css             # Game layout & panels
│   ├── 📄 game-items.css            # Game items & interactions
│   ├── 📄 controls.css              # Buttons & controls
│   ├── 📄 animations.css            # Animations & effects
│   ├── 📄 responsive.css            # Tablet & mobile responsive
│   └── 📄 mobile-landscape.css      # Mobile landscape optimization
│
├── 📂 js/                           # Professional JavaScript Modules
│   ├── 📄 constants.js              # Game configuration & constants
│   ├── 📄 utils.js                  # Utility functions & helpers
│   ├── 📄 main.js                   # Main game controller
│   ├── 📄 game-engine.js            # Game logic & mechanics
│   ├── 📄 ui-manager.js             # DOM manipulation & UI updates
│   ├── 📄 data-manager.js           # Data handling & CSV processing
│   ├── 📄 audio-manager.js          # Sound generation & effects
│   ├── 📄 adaptive-learning-client.js  # Backend API communication
│   └── 📄 heatmap-visualizer.js     # Progress visualization
│
├── 📂 data/                         # Dataset Management
│   ├── 📄 datasets.json             # Auto-generated dataset manifest
│   ├── 📄 README.md                 # Dataset documentation
│   ├── 📄 sample_vocabulary.csv     # Sample educational data
│   ├── 📄 words.csv                 # General vocabulary
│   ├── 📄 pali.csv                  # Pali language vocabulary
│   └── 📄 test_colors.csv           # Color vocabulary example
│
└── 📂 backend/                      # Python Backend System
    ├── 📄 learning_api.py           # FastAPI REST server
    ├── 📄 adaptive_learning_engine.py # FSRS & learning algorithms
    ├── 📄 run_server.py             # Server startup script
    └── 📄 learning_data.db          # SQLite database (auto-generated)
```

## 🧩 Module Breakdown

### Frontend Core Modules

#### **constants.js**
- **Purpose**: Centralized configuration management
- **Contains**: Game config, UI selectors, CSS classes, default data
- **Benefits**: Easy configuration changes, consistent constants

#### **utils.js**
- **Purpose**: Reusable utility functions
- **Modules**: ArrayUtils, DOMUtils, TimeUtils, ValidationUtils, StorageUtils, MathUtils
- **Benefits**: DRY principle, tested utilities, code reuse

#### **main.js** - Game Controller
- **Role**: Orchestrates all game components
- **Responsibilities**: Event binding, game flow control, module coordination
- **Pattern**: Mediator pattern for component communication

#### **game-engine.js** - Core Logic
- **Role**: Game mechanics and rules
- **Responsibilities**: Match validation, scoring, game state management
- **Features**: Grid size adaptation, unique element handling

#### **ui-manager.js** - View Layer
- **Role**: DOM manipulation and UI updates
- **Responsibilities**: Rendering, event handling, visual feedback
- **Features**: Font size control, grid layout management, animations

#### **data-manager.js** - Data Layer
- **Role**: Data handling and processing
- **Responsibilities**: CSV parsing, data validation, dataset management
- **Features**: Dynamic dataset discovery, data filtering

### CSS Module System

#### **Modular Architecture Benefits**
1. **Maintainability**: Easy to update specific components
2. **Performance**: Load only needed styles
3. **Scalability**: Add new modules without conflicts
4. **Team Collaboration**: Multiple developers can work on different modules
5. **Code Organization**: Logical grouping of related styles

#### **CSS Module Responsibilities**
- **base.css**: Foundation styles, reset, body, container
- **header.css**: Header layout, navigation, dataset controls
- **game-area.css**: Main game layout, panels, grid systems
- **game-items.css**: Game items, interactions, states, animations
- **controls.css**: Buttons, controls, font controls
- **animations.css**: Keyframes, transitions, feedback effects
- **responsive.css**: Tablet and mobile responsive design
- **mobile-landscape.css**: Mobile landscape optimization

## 🔄 Data Flow Architecture

### Game Initialization Flow
```
1. Main.js loads → 2. Initialize all managers → 3. Load datasets → 4. Start game
```

### Game Play Flow
```
1. User interaction → 2. UI Manager captures → 3. Game Engine processes →
4. Data validation → 5. Update game state → 6. UI feedback → 7. Audio response
```

### Adaptive Learning Flow
```
1. Game interaction → 2. Record response → 3. Send to backend →
4. FSRS processing → 5. Update user model → 6. Adaptive word selection
```

## 🚀 Professional Development Features

### Code Quality
- **ESLint**: Code linting and style consistency
- **Modular Architecture**: Separated concerns and responsibilities
- **Constants Management**: Centralized configuration
- **Utility Functions**: Reusable, tested functions
- **Error Handling**: Comprehensive error management

### Performance Optimization
- **Lazy Loading**: Load modules as needed
- **Efficient DOM Manipulation**: Batch updates, minimal reflows
- **Optimized CSS**: Modular loading, reduced bundle size
- **Mobile Optimization**: Touch-friendly, landscape support
- **Memory Management**: Proper cleanup, event listener removal

### Responsive Design
- **Mobile-First**: Optimized for mobile devices
- **Landscape Support**: Special handling for mobile landscape
- **Grid Adaptation**: Dynamic grid sizing based on screen
- **Touch Optimization**: Touch-action, tap highlights
- **Viewport Handling**: Proper mobile viewport configuration

## 🔧 Development Guidelines

### JavaScript Best Practices
1. **Use ES6+ Features**: Classes, modules, destructuring, arrow functions
2. **Const/Let Only**: No var declarations
3. **Function Documentation**: JSDoc comments for all public methods
4. **Error Handling**: Try-catch blocks for async operations
5. **Event Cleanup**: Remove event listeners when not needed

### CSS Best Practices
1. **BEM Methodology**: Block-Element-Modifier naming
2. **CSS Custom Properties**: Use CSS variables for themes
3. **Mobile-First**: Write mobile styles first, then desktop
4. **Performance**: Use transform/opacity for animations
5. **Accessibility**: ARIA labels, keyboard navigation support

### File Organization
1. **One Module Per File**: Single responsibility principle
2. **Clear Naming**: Descriptive, consistent file names
3. **Logical Grouping**: Related files in same directories
4. **Documentation**: README files in each major directory
5. **Version Control**: Clear commit messages, feature branches

This professional architecture ensures scalability, maintainability, and optimal performance across all devices while providing an engaging learning experience enhanced by AI-powered adaptive algorithms.