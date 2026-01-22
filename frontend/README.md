# Frontend

Next.js (React) frontend for Blood Transfusion CDS system (TransfusionIQ MVP).

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000)

## Features

### User Interface
- **3-Step Form Flow**: Guided patient input process
  1. Patient & Labs (demographics and laboratory values)
  2. Context & Procedure (clinical context and planned procedures)
  3. Review & Submit (review and get recommendation)

### Multi-Component Recommendations
- Display multiple blood component recommendations simultaneously
- Component-specific dosing, warnings, and rationale
- MTP (Massive Transfusion Protocol) context detection and warnings

### Clinical Features
- **Context Badges**: Visual indicators for patient conditions (bleeding, dengue, ICU, etc.)
- **Quick Toggles**: Fast access to critical inputs (active bleeding, hemodynamic instability)
- **Copy Order Note**: One-click copy of formatted order note to clipboard
- **Why Not Transfuse?**: Explicit contraindication explanations

### Internationalization (i18n)
- **Multi-language Support**: English and Bangla (বাংলা)
- **Language Toggle**: Easy switching between languages
- **PDF Export**: Language-specific PDF generation with proper font rendering

### Responsive Design
- **Mobile-First**: Optimized for mobile devices
- **Responsive Layout**: Adapts to desktop, tablet, and mobile screens
- **Touch-Friendly**: Large touch targets and intuitive interactions

### Export & Sharing
- **PDF Export**: Generate printable PDFs in English or Bangla
- **Order Note**: Formatted text for copy/paste into order systems
- **Override Logging**: Capture clinician overrides with reasons

### Admin Features (Admin-only)
- **Threshold Configuration**: Manage hospital-configurable clinical thresholds
- **AI Evidence Summary**: View AI-generated guideline summaries (admin only)

## Components

- `MultiStepForm.tsx` - Main 3-step patient input form
- `RecommendationCard.tsx` - Display multi-component recommendations
- `ContextBadges.tsx` - Visual context indicators
- `LanguageToggle.tsx` - Language switcher
- `PatientForm.tsx` - Legacy form (replaced by MultiStepForm, kept as backup)

## Technology

- **Next.js 14+** with App Router
- **React 18+** with hooks
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **React Hook Form** for form management
