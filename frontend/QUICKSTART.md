# Quick Start Guide

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file (optional, defaults to `http://localhost:8000`):
```env
VITE_API_BASE_URL=http://localhost:8000
```

## Development

Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/          # Reusable UI components
│   │   └── layout/      # Layout components
│   ├── pages/           # Page components
│   ├── hooks/           # Custom React hooks
│   ├── services/        # API services
│   ├── context/         # React Context providers
│   ├── utils/           # Utility functions
│   └── styles/          # Global styles
├── public/              # Static assets
└── package.json
```

## Features

- ✅ React 18 with Vite
- ✅ TailwindCSS with dark mode
- ✅ Axios with interceptors
- ✅ React Router for navigation
- ✅ React Hot Toast for notifications
- ✅ Context-based state management
- ✅ Reusable UI components
- ✅ Responsive design

## API Integration

The frontend connects to the FastAPI backend. Make sure the backend is running on `http://localhost:8000` (or update the `VITE_API_BASE_URL` in `.env`).

## Troubleshooting

- **API connection errors**: Check that the backend is running and the `VITE_API_BASE_URL` is correct
- **Build errors**: Make sure all dependencies are installed with `npm install`
- **Dark mode not working**: Check browser console for errors related to theme context

