# Security Investigation Platform

A professional security investigation dashboard built with React, Vite, TailwindCSS, and modern data visualization libraries.

## Tech Stack

- **React 18** with Vite
- **TailwindCSS** for styling
- **React Router** for navigation
- **Axios** for API calls
- **Recharts** for charts
- **React Flow** for graph visualization
- **Lucide React** for icons

## Features

### 1. Case Management
- Create and manage investigation cases
- View case status, risk levels, and record counts
- Delete cases with confirmation

### 2. File Upload
- Drag & drop file upload
- Real-time upload progress tracking
- Processing status monitoring with polling
- Error handling and display

### 3. Timeline View
- Chronological event feed
- Advanced filtering (date range, event type, search)
- Color-coded event cards
- Metadata display

### 4. Rule Engine Dashboard
- Summary cards for rule violations
- Midnight Activity detection
- Transaction Burst detection
- High Value Transfer detection
- Deleted Messages detection
- Suspicious events table

### 5. Anomaly Detection
- Run ML-based anomaly analysis
- Anomaly score gauge (0-100)
- Baseline vs Current behavior chart
- Anomalous events with deviation scores
- Model version and confidence tracking

### 6. Graph Intelligence
- Interactive network visualization
- Node and edge filtering
- Node details panel
- Centrality scores
- Connection analysis

### 7. Risk & Explainability
- Overall risk score (0-100) with color coding
- Risk contribution breakdown chart
- AI-generated explainability text
- Key metrics dashboard

### 8. Report Generation
- Generate investigation reports
- Report summary with key findings
- Executive summary
- Recommendations
- Report generation history
- Download reports (PDF)

## Project Structure

```
src/
├── api/
│   ├── client.js          # Axios instance
│   └── cases.js           # API functions
├── components/
│   ├── Badge.jsx          # Status badges
│   ├── Card.jsx           # Container component
│   ├── EmptyState.jsx     # Empty state UI
│   ├── Loader.jsx         # Loading spinner
│   ├── Modal.jsx          # Modal dialog
│   ├── Sidebar.jsx        # Navigation sidebar
│   ├── Table.jsx          # Data table
│   └── Topbar.jsx         # Top navigation bar
├── layouts/
│   └── MainLayout.jsx     # Main app layout
├── pages/
│   ├── CasesPage.jsx      # Case management
│   ├── UploadPage.jsx     # File upload
│   ├── TimelinePage.jsx   # Event timeline
│   ├── RulesPage.jsx      # Rule engine
│   ├── AnomalyPage.jsx    # Anomaly detection
│   ├── GraphPage.jsx      # Graph visualization
│   ├── RiskPage.jsx       # Risk analysis
│   └── ReportPage.jsx     # Report generation
├── App.jsx                # Route configuration
├── main.jsx               # Entry point
└── index.css              # Global styles
```

## Routes

- `/` - Redirects to `/cases`
- `/cases` - Case management page
- `/cases/:id/upload` - File upload page
- `/cases/:id/timeline` - Timeline view
- `/cases/:id/rules` - Rule engine dashboard
- `/cases/:id/anomaly` - Anomaly detection
- `/cases/:id/graph` - Graph intelligence
- `/cases/:id/risk` - Risk & explainability
- `/cases/:id/report` - Report generation

## Setup Instructions

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update the API URL:

```bash
cp .env.example .env
```

Edit `.env`:
```
VITE_API_URL=http://localhost:8000/api
```

### 3. Run Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### 4. Build for Production

```bash
npm run build
```

### 5. Preview Production Build

```bash
npm run preview
```

## API Integration

The frontend expects the following API endpoints:

- `GET /cases` - List all cases
- `GET /cases/:id` - Get case details
- `POST /cases` - Create new case
- `DELETE /cases/:id` - Delete case
- `POST /cases/:id/upload` - Upload file
- `GET /cases/:id/processing-status` - Get processing status
- `GET /cases/:id/timeline` - Get timeline events
- `GET /cases/:id/rules` - Get rule results
- `POST /cases/:id/anomaly/run` - Run anomaly detection
- `GET /cases/:id/anomaly` - Get anomaly results
- `GET /cases/:id/graph` - Get graph data
- `GET /cases/:id/risk` - Get risk score
- `POST /cases/:id/report/generate` - Generate report
- `GET /cases/:id/reports` - Get report history

## Design Philosophy

This is designed as a **professional security product**, not a college dashboard:

- Dark theme with subtle borders
- Color-coded risk indicators
- Professional typography
- Minimal but effective animations
- Clear information hierarchy
- Consistent spacing and layout
- Reusable component architecture

## Color Scheme

- Background: `#0a0a0a`
- Cards: `#111111`
- Borders: `#1f1f1f`
- Hover: `#1a1a1a`
- Primary: Blue (`#3b82f6`)
- Success: Green
- Warning: Yellow
- Danger: Red
- Info: Blue
- Purple: For special states

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

MIT
