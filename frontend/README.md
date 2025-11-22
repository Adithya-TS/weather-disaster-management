# Weather Disaster Management - Frontend

Modern React frontend for the Weather Disaster Management system.

## Tech Stack

- **React 18** with Vite
- **TailwindCSS** for styling
- **Axios** for API communication
- **React Router** for navigation
- **React Hot Toast** for notifications
- **Lucide React** for icons

## Features

- 🎨 Modern, responsive UI with dark mode support
- 🔄 Centralized API service with interceptors
- 📱 Toast notifications for user feedback
- 🎯 Reusable UI components
- 🗂️ Context-based state management
- 📊 Dashboard with multiple views

## Getting Started

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build

```bash
npm run build
```

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable UI components
│   ├── pages/           # Page components
│   ├── hooks/           # Custom React hooks
│   ├── services/        # API services
│   ├── context/         # React Context providers
│   ├── utils/           # Utility functions
│   └── styles/          # Global styles
├── public/              # Static assets
└── package.json
```

## API Integration

The frontend connects to the FastAPI backend running on `http://localhost:8000` by default. All API calls are handled through the centralized service layer in `src/services/api.js`.

